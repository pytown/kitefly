from abc import ABC, abstractmethod
from kitefly.model.step import Step

class Filter(ABC):
    """
    Base abstract class
    """
    @abstractmethod
    def __call__(self, step: Step) -> bool:
        return False

