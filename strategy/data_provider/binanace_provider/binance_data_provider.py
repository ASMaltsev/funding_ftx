import time
from datetime import datetime
from typing import Tuple

from connectors import ConnectorRouter

import connectors.exceptions
from strategy.logging import Logger
from strategy.data_provider.abstract_provider.abstract_data_provider import AbstractExecutorDataProvider
from strategy.data_provider.binanace_provider.binance_data_ws import WebSocketStream

logger = Logger('DataProviderExecutor').create()


def _control_rpc(current_rpc, max_rpc, connector) -> bool:
    """
    @param current_rpc: current rpc
    @param max_rpc: maximum rpc
    @return: Is warning rpc?
    """
    warning_min = 0.7
    warning_max = 0.95
    bad_rpc = False
    while True:
        if current_rpc > warning_max * max_rpc:
            bad_rpc = True
            sleep = 60
            logger.error(msg='You used all RPC. Sleep ',
                         extra=dict(current_rpc=current_rpc, max_rpc=max_rpc, sleep=sleep))
            time.sleep(sleep)
            connector.get_server_time()
            current_rpc = connector.USED_RPC
        if warning_min * max_rpc < current_rpc < warning_max * max_rpc:
            logger.warning(msg='You used a lot of RPC', extra=dict(current_rpc=current_rpc, max_rpc=max_rpc))
            if not bad_rpc:
                return True
        return False


def update_rpc(func):
    def wrapper_rpc(*args, **kwargs):
        args[0].current_rpc = args[0].connector.USED_RPC
        current_rpc = args[0].current_rpc
        max_rpc = args[0].max_rpc
        warning_rpc = _control_rpc(current_rpc, max_rpc, args[0].connector)
        args[0].warning_rpc = warning_rpc
        return func(*args, **kwargs)

    return wrapper_rpc


class BinanceDataProvider(AbstractExecutorDataProvider):

    def __init__(self, api_key: str, secret_key: str, section: str):
        super().__init__(api_key, secret_key)
        self.connector = ConnectorRouter(exchange='Binance', section=section).init_connector(api_key, secret_key)
        self.section = section
        self._correct_coef = 1.3
        self._max_limit_coef = 0.8
        self.current_rpc = 0
        self.max_rpc = self._get_max_limit()
        self.warning_rpc = False
        self.ws = None

    def _get_max_limit(self) -> int:
        for type_limit in self.connector.get_exchange_info()['rateLimits']:
            if type_limit['rateLimitType'] == 'REQUEST_WEIGHT' and type_limit['interval'] == 'MINUTE':
                return int(type_limit['limit'])

    @update_rpc
    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool) \
            -> Tuple[int, str]:
        if quantity > 0:
            response = self.connector.make_limit_order(ticker=ticker, side=side.lower(), price=price, quantity=quantity,
                                                       reduce_only=reduce_only)
            return int(response.get('orderId', None)), str(response.get('status', None))
        else:
            return -1, 'FILLED'

    @update_rpc
    def get_account_info(self):
        return self.connector.get_account_info()

    @update_rpc
    def get_balance(self, symbol):
        return self.connector.get_balances(symbol=symbol)

    @update_rpc
    def get_price(self, ticker):
        return self.connector.get_price(ticker=ticker)

    @update_rpc
    def get_contract_size(self, symbol):
        for symbols_info in self.connector.get_exchange_info()['symbols']:
            if symbols_info['symbol'] == symbol:
                return float(symbols_info['contractSize'])
        return 0

    @update_rpc
    def get_exchange_info(self):
        return self.connector.get_exchange_info()

    @update_rpc
    def make_market_order(self, ticker: str, side: str, quantity: float) -> bool:
        response = self.connector.make_market_order(ticker=ticker, side=side, quantity=quantity)
        status = str(response.get('status', None))
        return status == 'NEW'

    @update_rpc
    def cancel_all_orders(self, ticker: str) -> bool:
        if self.connector.cancel_all_orders(ticker=ticker)['code'] == 200:
            return True
        return False

    @update_rpc
    def cancel_order(self, ticker: str, order_id: int) -> bool:
        try:
            response = self.connector.cancel_order(ticker=ticker, order_id=order_id)
            if response['status'] == 'CANCELED':
                return True
            return False
        except connectors.exceptions.RequestError as e:
            if str(e).find('-2011') > 0:  # {'code': -2011, 'msg': 'Unknown order sent.'}
                return True
            return False

    @update_rpc
    def get_amount_positions(self, ticker: str) -> float:
        return self.connector.get_positions(ticker=ticker)[0]['positionAmt']

    def get_bbid_bask(self, ticker: str) -> Tuple[float, float]:
        self._create_webosocket(ticker=ticker)
        data = self.ws.get_state()
        while data is None:
            data = self.ws.get_state()
        return float(data['b']), float(data['a'])

    def _create_webosocket(self, ticker):
        if self.ws is None:
            self.ws = WebSocketStream(section=self.section, ticker=ticker)
            self.ws.daemon = True
            self.ws.start()

    @update_rpc
    def get_order_status(self, ticker: str, order_id: int) -> Tuple[str, float]:
        response = self.connector.status_order(ticker=ticker, order_id=order_id)
        return response.get('status', None), float(response.get('executedQty', None))

    @update_rpc
    def get_mid_price(self, ticker):
        bbid_bask = self.connector.get_bbid_bask(ticker)
        bbid = float(bbid_bask['bidPrice'])
        bask = float(bbid_bask['askPrice'])
        mid_price = (bbid + bask) / 2
        return mid_price

    @update_rpc
    def get_spread(self, ticker_swap, ticker_quart):
        price_swap = self.get_price(ticker_swap)
        price_quart = self.get_price(ticker_quart)

        spread_pct = (price_quart - price_swap) / price_swap
        tte = self.get_tte(ticker_quart)
        spread_apr = spread_pct * 365 / tte

        return spread_pct, spread_apr

    def get_tte(self, ticker_quart) -> int:
        tte = ticker_quart.split('_')[1]
        y = '20' + tte[:2]
        m = tte[2:4]
        d = tte[4:]
        date = f'{y}/{m}/{d}'
        date = datetime.strptime(date, "%Y/%m/%d")
        tte = (date - datetime.utcnow()).days
        return tte

    @update_rpc
    def make_safety_limit_order(self, ticker: str, side: str, quantity: float, reduce_only: bool) \
            -> Tuple[str, int, float, float]:
        """
        place a limit order at the best price
        @return: order status, orderId, price, executed quantity
        """
        side_index = 1 if side == 'sell' else 0
        while True:
            time.sleep(0.3)

            price = self.get_bbid_bask(ticker)[side_index]
            order_id, _ = self.make_limit_order(ticker=ticker, side=side, price=price, quantity=quantity,
                                                reduce_only=reduce_only)
            time.sleep(0.1)
            status, executed_qty = self.get_order_status(ticker=ticker, order_id=order_id)
            if status != 'EXPIRED':
                logger.info(msg='Order status for limit order.',
                            extra=dict(order_id=order_id, order_status=status, executed_qty=executed_qty))
                return status, order_id, price, executed_qty

    @update_rpc
    def make_safety_market_order(self, ticker: str, side: str, quantity: float, min_size_order: float) -> bool:
        """
        When order less than MIN NOTIONAL, we sell/buy correct_size and buy/sell correct_size + quantity
        @return: True if success False otherwise
        """
        try:
            if quantity == 0:
                return True
            return self.make_market_order(ticker=ticker, side=side, quantity=quantity)
        except connectors.exceptions.RequestError as e:
            logger.warning(msg='Market order less MIN NOTIONAL', extra=dict(Exception=e))
            if str(e).find('-4164') > 0:
                precision = abs(str(min_size_order).find('.') - len(str(min_size_order))) + 1

                correct_size = round(self._correct_coef * float(min_size_order), precision)

                logger.info(msg='Start correction', extra=dict(Correct_size=correct_size, precision=precision))

                self.make_market_order(ticker=ticker, side=self._get_inverse_market_op(side), quantity=correct_size)
                self.make_market_order(ticker=ticker, side=side, quantity=round(quantity + correct_size, precision))

            elif str(e).find('-4003') > 0:  # {'code': -4003, 'msg': 'Quantity less than zero.'}
                return True

    @update_rpc
    def min_size_for_market_order(self, ticker):
        for symbol_info in self.connector.get_exchange_info()['symbols']:
            if symbol_info['symbol'] == ticker:
                filters = symbol_info['filters']
                for f in filters:
                    if f.get('minQty') is not None:
                        return f['minQty']

    @update_rpc
    def get_available_balance(self, ticker, section):
        pass

    @staticmethod
    def _get_inverse_market_op(side):
        side = side.lower()
        if side == 'sell':
            return 'buy'
        elif side == 'buy':
            return 'sell'
        else:
            return NotImplementedError
