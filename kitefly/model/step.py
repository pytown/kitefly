from typing import Optional, List

from .target import Target
from ..util import generate_key

class Step:
    """
    Generic root for pipeline steps

    Params:

    """
    def __init__(self,
        when: str = "",
        branches: str = "",
        allow_dependency_failure: bool = False,
        targets: Optional[List[Target]] = None,
        **kwargs
    ):
        self.key = None
        self.when = when
        self.depends_on = []
        self.branches = branches
        self.allow_dependency_failure = allow_dependency_failure
        self.properties = kwargs
        self.targets = targets or []
        if not self.targets:
            self.targets = getattr(self.__class__, 'targets', [])

    def asdict(self) -> dict:
        d = {}
        if self.when:
            d['if'] = self.when
        if self.depends_on:
            d['depends_on'] = self.depends_on
        if self.branches:
            d['branches'] = self.branches
        if self.allow_dependency_failure:
            d['allow_dependency_failure'] = True
        if self.properties:
            d.update(self.properties)
        return d