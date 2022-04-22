from abc import ABC, abstractmethod
from kitefly.model.step import Step

class Filter():
    def __call__(self, step: Step) -> bool:
        return False
