from abc import ABC, abstractmethod
from typing import Tuple


class AbstractExecutorDataProvider(ABC):
    """DataProvider interface for executor"""

    def __init__(self, api_key: str, secret_key: str):
        """
        @param api_key: client's api key
        @param secret_key: client's secret key
        """
        self.api_key = api_key
        self.secret_key = secret_key

    @abstractmethod
    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool) \
            -> Tuple[int, str]:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @param side: 'sell' or 'buy'
        @param price: price
        @param quantity: quantity
        @param reduce_only: reduce only
        @return: orderId, order status (NEW, FILLED, EXPIRED, PARTIALLY_FILLED)
        """

    @abstractmethod
    def make_market_order(self, ticker: str, side: str, quantity: float) -> bool:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @param side: 'sell' or 'buy'
        @param quantity: quantity
        @return: True if success False otherwise
        """

    @abstractmethod
    def cancel_all_orders(self, ticker: str) -> bool:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @return: True if success False otherwise
        """

    @abstractmethod
    def cancel_order(self, ticker: str, order_id: int) -> bool:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @param order_id: order id
        @return: True if success False otherwise
        """

    @abstractmethod
    def get_amount_positions(self, ticker: str) -> float:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @return: amount positions for this pair
        """

    @abstractmethod
    def get_bbid_bask(self, ticker: str) -> Tuple[float, float]:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @return: (best bid price, best ask price)
        """

    @abstractmethod
    def get_order_status(self, ticker: str, order_id: int) -> str:
        """
        @param ticker: pair name (BTCUSDT, ETHUSDT...)
        @param order_id: order id
        @return: order status (NEW, FILLED, EXPIRED, PARTIALLY_FILLED)
        """
