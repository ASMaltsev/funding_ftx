import time
from datetime import datetime
from typing import Tuple
from connectors.router import ConnectorRouter
import connectors
from strategy.logging import Logger
from strategy.others import inverse_operation
from strategy.data_provider.abstract_provider.abstract_data_provider import AbstractExecutorDataProvider

logger = Logger('DataProviderExecutor').create()


class BinanceDataProvider(AbstractExecutorDataProvider):

    def __init__(self, api_key: str, secret_key: str, section: str, ws_provider=None):
        super().__init__(api_key, secret_key)

        self.connector = ConnectorRouter(exchange='FTX', section='').init_connector(api_key, secret_key,
                                                                                    subaccount='HASH_CIB_ALGO_USD_SP')
        self.section = section
        self._correct_coef = 4
        self.current_rpc = 0
        self.warning_rpc = False
        # self.ws_provider = ws_provider

    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool) \
            -> Tuple[int, str]:
        if quantity > 0:
            response = self.connector.make_limit_order(ticker=ticker, side=side.lower(), price=price,
                                                       quantity=quantity,
                                                       reduce_only=reduce_only)
            return int(response.get('orderId', None)), str(response.get('status', None))
        else:
            return -1, 'FILLED'

    def get_account_info(self):
        return self.connector.get_account_info()

    def get_balance(self, ticker):
        return self.connector.get_balances(symbol=ticker)

    def get_price(self, ticker):
        return self.connector.get_price(ticker=ticker)

    def get_contract_size(self, ticker):
        for symbols_info in self.connector.get_exchange_info()['symbols']:
            if symbols_info['symbol'] == ticker:
                return float(symbols_info['contractSize'])
        return 0

    def get_exchange_info(self):
        return self.connector.get_exchange_info()

    def make_market_order(self, ticker: str, side: str, quantity: float) -> bool:
        response = self.connector.make_market_order(ticker=ticker, side=side, quantity=quantity)
        status = str(response.get('status', None))
        return status == 'NEW'

    def cancel_all_orders(self, ticker: str) -> bool:
        if self.connector.cancel_all_orders(ticker=ticker)['code'] == 200:
            return True
        return False

    def cancel_order(self, ticker: str, order_id: int) -> bool:
        try:
            response = self.connector.cancel_order(ticker=ticker, order_id=order_id)
            if response['status'] == 'CANCELED':
                return True
            return False
        except connectors.exceptions.RequestError as e:
            if str(e).find('-2011') > 0:  # {'code': -2011, 'msg': 'Unknown order sent.'}
                return True
        except Exception as e:
            return False

    def get_amount_positions(self, ticker: str) -> float:
        return self.connector.get_positions(ticker=ticker)[0]['positionAmt']

    def get_bbid_bask(self, ticker: str) -> Tuple[float, float]:
        response = self.connector.get_orderbook(ticker, limits=1)
        return float(response.get('bids')[0][0]), float(response.get('asks')[0][0])

    def get_order_status(self, ticker: str, order_id: int) -> Tuple[str, float]:
        for _ in range(10):
            try:
                response = self.connector.status_order(ticker=ticker, order_id=order_id)
                return response.get('status', None), float(response.get('executedQty', None))
            except connectors.exceptions.RequestError as e:
                if str(e).find('-2013') > 0:  # {'code': -2013, 'msg': 'Order does not exist.'}
                    time.sleep(0.1)
        raise Exception('Order does not exist.')

    def get_mid_price(self, ticker):
        bbid_bask = self.connector.get_bbid_bask(ticker)
        bbid = float(bbid_bask['bidPrice'])
        bask = float(bbid_bask['askPrice'])
        mid_price = (bbid + bask) / 2
        return mid_price

    def get_spread(self, ticker_swap, ticker_quart):
        price_swap = self.get_price(ticker_swap)
        price_quart = self.get_price(ticker_quart)

        spread_pct = (price_quart - price_swap) / price_swap
        tte = self.get_tte(ticker_quart)
        tte = tte if tte != 0 else 0.0001
        spread_apr = spread_pct * 365 / tte
        return spread_pct, spread_apr

    def get_tte(self, ticker):
        tte = ticker.split('_')[1]
        y = '20' + tte[:2]
        m = tte[2:4]
        d = tte[4:]
        date = f'{y}/{m}/{d}'
        date = datetime.strptime(date, "%Y/%m/%d")
        tte = (date - datetime.utcnow()).days
        return tte

    def make_safety_limit_order(self, ticker: str, side: str, quantity: float, reduce_only: bool) \
            -> Tuple[str, int, float, float]:
        """
        place a limit order at the best price
        @return: order status, orderId, price, executed quantity
        """
        side_index = 1 if side == 'sell' else 0
        while True:
            price = self.get_bbid_bask(ticker)[side_index]
            order_id, _ = self.make_limit_order(ticker=ticker, side=side, price=price, quantity=quantity,
                                                reduce_only=reduce_only)
            time.sleep(0.1)
            status, executed_qty = self.get_order_status(ticker=ticker, order_id=order_id)
            if status != 'EXPIRED':
                logger.info(msg='Order status for limit order.',
                            extra=dict(order_id=order_id, order_status=status, executed_qty=executed_qty))
                return status, order_id, price, executed_qty

    def make_safety_market_order(self, ticker: str, side: str, quantity: float, min_size_order: float,
                                 precision) -> bool:
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

                correct_size = round(self._correct_coef * float(min_size_order), precision)

                logger.info(msg='Start correction', extra=dict(Correct_size=correct_size, precision=precision))

                self.make_market_order(ticker=ticker, side=inverse_operation(side), quantity=correct_size)
                self.make_market_order(ticker=ticker, side=side, quantity=round(quantity + correct_size, precision))

            elif str(e).find('-4003') > 0:  # {'code': -4003, 'msg': 'Quantity less than zero.'}
                return True

    def min_size_for_market_order(self, ticker):
        return 0.00001

    def get_available_balance(self, ticker, section):
        pass
