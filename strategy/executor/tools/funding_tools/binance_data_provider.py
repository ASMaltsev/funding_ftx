import time
from typing import Tuple

from connectors import ConnectorRouter

import connectors.exceptions
from strategy.others import Logger
from strategy.executor.tools.abstract_tools import AbstractExecutorDataProvider

logger = Logger('DataProviderExecutor').create()


def control_rpc(current_rpc, max_rpc) -> bool:
    """
    @param current_rpc: current rpc
    @param max_rpc: maximum rpc
    @return: Is warning rpc?
    """
    bad_rpc = False
    while True:
        if current_rpc > 0.9 * max_rpc:
            bad_rpc = True
            sleep = 60
            logger.error(msg='You used all RPC. Sleep. ',
                         extra=dict(current_rpc=current_rpc, max_rpc=max_rpc, sleep=sleep))
            time.sleep(sleep)
        if 0.5 * max_rpc < current_rpc < 0.9 * max_rpc:
            logger.warning(msg='You used a lot of RPC', extra=dict(current_rpc=current_rpc, max_rpc=max_rpc))
            if not bad_rpc:
                return True
        return False


def update_rpc(func):
    def wrapper_rpc(*args, **kwargs):
        args[0].current_rpc = args[0].connector.USED_RPC
        current_rpc = args[0].current_rpc
        max_rpc = args[0].max_rpc
        warning_rpc = control_rpc(current_rpc, max_rpc)
        args[0].warning_rpc = warning_rpc
        return func(*args, **kwargs)

    return wrapper_rpc


class BinanceDataProvider(AbstractExecutorDataProvider):

    def __init__(self, api_key: str, secret_key: str, section: str):
        super().__init__(api_key, secret_key)
        self.connector = ConnectorRouter(exchange='Binance', section=section).init_connector(api_key, secret_key)

        self._correct_coef = 1.3
        self._max_limit_coef = 0.8
        self.current_rpc = 0
        self.max_rpc = self._get_max_limit()
        self.warning_rpc = False

    def _get_max_limit(self) -> int:
        for type_limit in self.connector.get_exchange_info()['rateLimits']:
            if type_limit['rateLimitType'] == 'REQUEST_WEIGHT' and type_limit['interval'] == 'MINUTE':
                return int(type_limit['limit'])

    @update_rpc
    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool) \
            -> Tuple[int, str]:
        response = self.connector.make_limit_order(ticker=ticker, side=side.lower(), price=price, quantity=quantity,
                                                   reduce_only=reduce_only)
        return int(response.get('orderId', None)), str(response.get('status', None))

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
            if str(e).find('-2011') > 0:
                return True
            return False

    @update_rpc
    def get_amount_positions(self, ticker: str) -> float:
        return self.connector.get_positions(ticker=ticker)[0]['positionAmt']

    @update_rpc
    def get_bbid_bask(self, ticker: str) -> Tuple[float, float]:
        response = self.connector.get_bbid_bask(ticker=ticker)
        return float(response.get('bidPrice', None)), float(response.get('askPrice', None))

    @update_rpc
    def get_order_status(self, ticker: str, order_id: int) -> str:
        response = self.connector.status_order(ticker=ticker, order_id=order_id)
        return response.get('status', None)

    @update_rpc
    def make_safety_limit_order(self, ticker: str, side: str, quantity: float, reduce_only: bool):
        """
        place a limit order at the best price
        @return: price, orderId
        """
        side_index = 0 if side == 'sell' else 1
        while True:
            price = self.get_bbid_bask(ticker)[side_index]
            order_id, _ = self.make_limit_order(ticker=ticker, side=side, price=price, quantity=quantity,
                                                reduce_only=reduce_only)
            logger.debug(msg='Place LIMIT ORDER.', extra=dict(ticker=ticker, order_id=order_id))

            time.sleep(0.2)

            status = self.get_order_status(ticker=ticker, order_id=order_id)
            logger.debug(msg='Info LIMIT ORDER:', extra=dict(ticker=ticker, status=status, order_id=order_id))
            if status == 'NEW':
                return order_id, status

    @update_rpc
    def make_safety_market_order(self, ticker: str, side: str, quantity: float, min_size_order: float) -> bool:
        """
        When order less than MIN NOTIONAL, we sell/buy correct_size and buy/sell correct_size + quantity
        @return: True if success False otherwise
        """
        try:
            return self.make_market_order(ticker=ticker, side=side, quantity=quantity)
        except connectors.exceptions.RequestError as e:
            logger.warning(msg='Market order less MIN NOTIONAL.', extra=dict(Exception=e))
            if str(e).find('-4164') > 0:
                precision = abs(str(min_size_order).find('.') - len(str(min_size_order))) + 1

                correct_size = round(self._correct_coef * float(min_size_order), precision)

                logger.info(msg='Start correction.', extra=dict(Correct_size=correct_size, precision=precision))

                self.make_market_order(ticker=ticker, side=self._get_inverse_market_op(side), quantity=correct_size)
                self.make_market_order(ticker=ticker, side=side, quantity=round(quantity + correct_size, precision))

    @update_rpc
    def min_size_for_market_order(self, ticker):
        for symbol_info in self.connector.get_exchange_info()['symbols']:
            if symbol_info['symbol'] == ticker:
                filters = symbol_info['filters']
                for f in filters:
                    if f.get('tickSize') is not None:
                        return f['tickSize']

    @staticmethod
    def _get_inverse_market_op(side):
        side = side.lower()
        if side == 'sell':
            return 'buy'
        elif side == 'buy':
            return 'sell'
        else:
            return NotImplementedError