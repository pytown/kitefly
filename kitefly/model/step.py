from typing import Optional, List, Set, Union

from .target import Target
from ..util import generate_key, as_tuple

class Step:
    """
    Generic root for pipeline steps containing common attributes such
    as 'if', 'branches', 'depends_on', and 'allow_dependency_failure'
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
        self.depends_on: List[str] = []
        self.dependents: List[Step] = []
        self.branches = branches
        self.allow_dependency_failure = allow_dependency_failure
        self.properties: dict = kwargs
        agg_targets: Set[Target] = set(targets or [])
        for cls in self.classes():
            agg_targets |= set(getattr(cls, 'targets', []))
        self.targets: List[Target] = list(agg_targets)


    def classes(self) -> List[type]:
        """
        Return parent classes in reverse MRO, which is used to aggregate set or hash
        properties based on lineage.

        Example:
        cmd: Command
        cmd.classes() -> [Step, Command]
        """
        classes = [cls for cls in self.__class__.__mro__ if cls is not object]
        classes.reverse()
        return classes

    def asdict(self) -> dict:
        """
        Every Step class has an asdict() method to generate a plain dictionary mapping that can
        be used to generate serialized text formats, primarily YAML for Buildkite
        """
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

    def __lshift__(self, deps: Union[Step, Iterable[Step]]) -> 'Command':
        """
        Declare a dependency relationship from the command step (A) with another step (B)
        that will become its dependent. The key of step A (keyA) will be added to B's
        depends_on list
        """
        for dep in as_tuple(deps):
            dep.depends_on.push(self.key)
            self.dependents.append(dep)
        return self

    def __rshift__(self, dep_on: Union[Step, Iterable[Step]]) -> 'Command':
        """
        Declare a dependency relationship from this step (A) on another step (B)
        Step B's key will be added to this step's depends_on list.
        """
        for parent in as_tuple(dep_on):
            self.depends_on.push(parent.key)
            parent.dependents.append(self)
        return self