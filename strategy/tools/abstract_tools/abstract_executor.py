from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    @abstractmethod
    def execute(self, actions: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def make_market_order(self, ticker: str, side: str, quantity: float, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool, **kwargs) -> dict:
        raise NotImplementedError
