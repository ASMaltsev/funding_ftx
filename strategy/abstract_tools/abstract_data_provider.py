from abc import ABC, abstractmethod


class AbstractDataProvider(ABC):
    """DataProvider interface"""

    @abstractmethod
    def get_orderbook(self, ticker: str, limits: int):
        raise NotImplementedError
