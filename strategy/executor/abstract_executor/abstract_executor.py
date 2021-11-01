from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    def __init__(self, data_provider):
        """
        @param data_provider: provider for exchange
        """
        self.data_provider = data_provider

    @abstractmethod
    def execute(self, market_ticker: str, limit_ticker: str, limit_side: str, market_side: str,
                total_amount: float, reduce_only: bool) -> bool:
        """

        @param market_ticker: ticker for market orders
        @param limit_ticker: ticker for limit orders
        @param limit_side: side for limit orders
        @param market_side: side for market orders
        @param total_amount: total amount
        @param reduce_only: reduce only
        @return: True if good False otherwise
        """
        raise NotImplementedError
