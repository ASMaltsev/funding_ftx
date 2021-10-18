from abc import abstractmethod


class AbstractAlpha:
    """Strategy interface"""

    @abstractmethod
    def decide(self) -> dict:
        """
        @return: information for executor
        """
        raise NotImplementedError
