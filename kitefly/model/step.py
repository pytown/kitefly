from typing import Optional
from ..util import generate_key

class Step:
    """
    Generic root for pipeline steps

    Params:

    """
    def __init__(self, when: str = "", branches: str = "", **kwargs):
        self.key = None
        self.when = when
        self.depends_on = []
        self.branches = branches
        self.properties = kwargs

    def __iadd__(self, val: any):
        """
        Generic noop for inline adding used primarily so that Group objects containing
        different types of steps can safely inline-add to all steps
        """
        pass

    def asdict(self) -> dict:
        d = {}
        if self.when:
            d['if'] = self.when
        if self.depends_on:
            d['depends_on'] = self.depends_on
        if self.branches:
            d['branches'] = self.branches
        if self.properties:
            d.update(self.properties)
        return d