from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    def __init__(self, section):
        """
        @param section: Binance section
        """
        self.section = section

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError
