from typing import Tuple, Union, List, Iterable

from .group import Group
from .step import Step
from .target import Target

class Pipeline:
  def __init__(self, *steps: Tuple[Union[Step, Group]]):
    self.items: List[Union[Step, Group]] = list(steps)

  def __iadd__(self, value: Union[Step, Group]):
    self.items.append(value)

  def filter(
      self,
      targets: Iterable[Target]=(),
      tags: Iterable[str]=(),
      exclude_tags: Iterable[str]=()
    ) -> 'Pipeline':
    """
    Filter the pipeline with the optional provided values and return a flattened
    list of steps with duplicate steps (via key) removed.
    """
    return Pipeline(*self.items)

  def steps(self) -> List[Step]:
    seen: dict = {}
    steps: List[Step] = []
    for item in self.items:
      coll = [step]
      if isinstance(item, Group):
        coll = item.steps()
      for step in coll:
        if not step.key or step.key not in seen:
          seen[step.key or ''] = True
          steps.append(step)
    return steps