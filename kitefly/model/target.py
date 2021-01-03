from re import Pattern
from typing import List, Tuple, Union
import os

from wcmatch import glob


def partion_all()

class TargetPattern:
  GLOB_ALL = object()

  def __init__(self, pattern: Union[str, Pattern]):
    self.pattern = pattern
    self.is_regex = False
    if isinstance(pattern, Pattern):
      self.is_regex = True

  def matches(self, filepath: str) -> bool:
    if self.is_regex:
      return self.pattern.match(filepath) is not None
    return glob.globmatch(filepath, self.pattern)

  def __len__(self) -> int:
    if self.is_regex:
      return len(self.pattern.pattern)
    return len(self.pattern)

  def __lt__(self, comp: 'TargetPattern') -> bool:
    return len(self) < len(comp)

class Target:
  """
  A grouping of file-matching patterns used to group sources for a single Build
  Target, which can be associated with one or more Step entities in the Pipeline.
  When base-branch comparison is used, each changed file in the list will be matched
  with the Target with the highest priority, or pattern length if the priorities are equal.
  This collection of Targets will be used to include/exclude steps in the pipeline.

  A Target can also depend on another Target, meaning that if A depends on B, and
  B is included in the list of matched Targets, then A will also be included.
  """
  def __init__(self, sources: Union[str, Iterable[str]], priority: int = 0):
    self.patterns = [TargetPattern(p) for p in as_tuple(sources)]
    self.depends_on: List[Target] = []

  def __rshift__(self, dep: 'Target') -> 'Target':
    self.depends_on.append(dep)
    return self

  def __lt__(self, comp: 'Target') -> bool:
    if self.priority != comp.priority:
      return self.priority < comp.priority
    return self.patterns < comp.patterns