from abc import abstractmethod
from strategy.tools.abstract_tools.abstract_data_provider import AbstractDataProvider


class AbstractStrategy:
    """Strategy interface"""

    def __init__(self, data_provider: AbstractDataProvider):
        self.data_provider = data_provider

    @abstractmethod
    def decide(self) -> dict:
        raise NotImplementedError
