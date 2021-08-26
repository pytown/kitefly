from .filter import Filter
from ..model.step import Step

class NoopFilter(Filter):
    def __call__(self, step: Step) -> bool:
        return True