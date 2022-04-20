from typing import Generator, List, Set, Iterable, Union, Pattern
from ..util import glob


class TargetPattern:
    GLOB_ALL = object()

    def __init__(self, pattern: Union[str, Pattern]):
        if isinstance(pattern, str):
            self.pattern = glob(pattern)
        else:
            self.pattern = pattern

    def matches(self, filepath: str) -> bool:
        return self.pattern.match(filepath) is not None

    def __len__(self) -> int:
        return len(self.pattern.pattern)

    def __lt__(self, comp: "TargetPattern") -> bool:
        return len(self) < len(comp)

    def __str__(self) -> str:
        return f"r/{self.pattern.pattern}/"


class Target:
    """
    A collection of file-matching patterns used to group sources for a single Build
    Target, which can be associated with one or more Step entities in the Pipeline.
    When base-branch comparison is used, each changed file in the list will be matched
    with the Target with the highest priority, or pattern length if the priorities are equal.
    This collection of Targets will be used to include/exclude steps in the pipeline.

    A Target can also depend on another Target, meaning that if A depends on B, and
    B is included in the list of matched Targets, then A will also be included.
    """

    def __init__(
        self,
        sources: Union[Iterable[Union[str, Pattern]], str, Pattern],
        priority: int = 0,
        name: str = "",
    ):
        if type(sources) == str or isinstance(sources, Pattern):
            self.patterns = [TargetPattern(sources)]
        elif type(sources) == list or type(sources) == tuple:
            self.patterns = [TargetPattern(p) for p in sources]
        self.depends_on: List[Target] = []
        self.name = name
        default_priority = getattr(self, "priority", 0)
        self.priority = priority or default_priority

    @property
    def dependencies(self) -> Set["Target"]:
        """
        Return distinct set of Targets in the dependency graph
        """
        deps: Set["Target"] = set()
        for target in self.depends_on:
            deps.add(target)
            deps |= target.dependencies
        return deps

    def _iterate_patterns(self) -> Generator[TargetPattern, None, None]:
        """
        Iterate recursively through all patterns in the depencency tree.
        """
        for pattern in self.patterns:
            yield pattern
        for target in self.depends_on:
            for pattern in target._iterate_patterns():
                yield pattern

    def matches(self, filepath: str) -> bool:
        """
        Returns True if the Target patterns or any of its dependency patterns match the provided filepath.
        """
        for pattern in self._iterate_patterns():
            if pattern.matches(filepath):
                return True
        return False

    @classmethod
    def src(cls, *sources: Union[str, Pattern]) -> "Target":
        return Target(sources=sources)

    def prio(self, priority: int) -> "Target":
        self.priority = priority
        return self

    def __rshift__(self, dep: "Target") -> "Target":
        self.depends_on.append(dep)
        return dep

    def __lt__(self, comp: "Target") -> bool:
        if self.priority != comp.priority:
            return self.priority < comp.priority
        return self.patterns < comp.patterns

    def __str__(self) -> str:
        plist = ",".join([str(p) for p in self.patterns])
        return f"Target(priority={self.priority},sources={plist})"
