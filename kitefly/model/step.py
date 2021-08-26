from typing import Any, Dict, List, Iterable, Union

from .target import Target
from ..util import as_iterable

class Step:
    """
    Generic root for pipeline steps containing common attributes such
    as 'if', 'branches', 'depends_on', and 'allow_dependency_failure'
    """

    _instance_count = 0

    def __init__(self,
        when: str = "",
        branches: str = "",
        allow_dependency_failure: bool = False,
        tags: List[str] = None,
        targets: List[Target] = None,
        **kwargs
    ):
        self.__class__._instance_count += 1
        self.instance_serial = self.__class__._instance_count
        self.key = ""
        self.when = when
        self.depends_on: List[str] = []
        self.dependents: List[Step] = []
        self.branches = branches
        self.allow_dependency_failure = allow_dependency_failure
        self.properties: dict = kwargs
        self._tags = tags or []
        self._targets = targets or []


    def classes(self) -> List[type]:
        """
        Return parent classes in reverse MRO, which is used to aggregate set or hash
        properties based on lineage.

        Example:
        cmd: Cokmand
        cmd.classes() -> [Step, Command]
        """
        classes = [cls for cls in self.__class__.__mro__ if cls is not object]
        classes.reverse()
        return classes

    def combined_parent_list(self, property: str) -> list:
        values = list(as_iterable(self.properties.get(property) or []))
        for cls in self.classes():
            values += getattr(cls, property, [])
        return values

    @property
    def targets(self) -> List[Target]:
        """
        Return distinct list of Targets associated with this step.
        """
        return list(set(self.combined_parent_list("targets")))

    @property
    def tags(self) -> List[str]:
        """
        Return distinct list of tags associated with this step.
        """
        return list(set(self.combined_parent_list("tags")))

    def asdict(self) -> dict:
        """
        Every Step class has an asdict() method to generate a plain dictionary mapping that can
        be used to generate serialized text formats, primarily YAML for Buildkite
        """
        d: Dict[str, Any] = {}
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

    def __lshift__(self, deps: Union['Step', Iterable['Step']]) -> 'Step':
        """
        Declare a dependency relationship from the command step (A) with another step (B)
        that will become its dependent. The key of step A (keyA) will be added to B's
        depends_on list
        """
        for dep in as_iterable(deps):
            if self.key is None:
                raise ValueError("Cannot add reverse dependency on self: key is not defined")
            dep.depends_on.append(self.key)
            self.dependents.append(dep)
        return self

    def __rshift__(self, dep_on: Union['Step', Iterable['Step']]) -> 'Step':
        """
        Declare a dependency relationship from this step (A) on another step (B)
        Step B's key will be added to this step's depends_on list.
        """
        for parent in as_iterable(dep_on):
            if parent.key is None:
                raise ValueError("Cannot depend on step without a key")
            self.depends_on.append(parent.key)
            parent.dependents.append(self)
        return self

    def __eq__(self, step: Any) -> bool:
        if isinstance(step, Step):
            return self.asdict() == step.asdict()
        return False

    def __hash__(self) -> int:
        return self.instance_serial