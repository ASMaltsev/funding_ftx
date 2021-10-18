from abc import abstractmethod


class AbstractStrategy:
    """Strategy interface"""

    @abstractmethod
    def decide(self) -> dict:
        """
        @return: information for executor
        """
        raise NotImplementedError
