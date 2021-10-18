from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    def __init__(self, api_key: str, secret_key: str):
        """
        @param api_key: client's api ket
        @param secret_key: client's secret key
        """
        self.api_key = api_key
        self.secret_key = secret_key

    @abstractmethod
    def execute(self, actions: dict) -> bool:
        """
        @param actions: message from strategy
        @return bool: True if worked correctly False otherwise
        """
        raise NotImplementedError
