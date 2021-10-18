from typing import Tuple
from logging import getLogger
from connectors import ConnectorRouter

from strategy.executor.tools.abstract_tools import AbstractExecutorDataProvider


class BinanceDataProvider(AbstractExecutorDataProvider):

    def __init__(self, api_key: str, secret_key: str, section: str):
        super().__init__(api_key, secret_key)
        self.connector = ConnectorRouter(exchange='Binance', section=section).init_connector(api_key, secret_key)
        self.logger = getLogger('test')

    def get_max_limit(self) -> int:
        pass

    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool) \
            -> Tuple[int, str]:
        response = self.connector.make_limit_order(ticker=ticker, side=side, price=price, quantity=quantity,
                                                   reduce_only=reduce_only)

    def make_market_order(self, ticker: str, side: str, quantity: float) -> bool:
        response = self.connector.make_market_order(ticker=ticker, side=side, quantity=quantity)

    def cancel_all_orders(self, ticker: str) -> bool:
        self.connector.cancel_all_orders(ticker=ticker)

    def cancel_order(self, ticker: str, order_id: int) -> bool:
        self.connector.cancel_order(ticker=ticker, order_id=order_id)

    def get_amount_positions(self, ticker: str) -> float:
        self.connector.get_positions(ticker=ticker)

    def get_bbid_bask(self, ticker: str) -> Tuple[float, float]:
        self.logger.warning(msg='Tut')
        print(self.connector.get_bbid_bask(ticker=ticker))

    def get_order_status(self, ticker: str, order_id: int) -> str:
        self.connector.status_order(ticker=ticker, order_id=order_id)

    def make_safety_limit_order(self):
        pass

    def make_safety_market_order(self):
        pass
