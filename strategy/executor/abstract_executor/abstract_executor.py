from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError
