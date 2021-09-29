from abc import ABC, abstractmethod


class AbstractExecutor(ABC):
    """Executor interface"""

    @abstractmethod
    def execute(self, actions: list) -> bool:
        raise NotImplementedError
