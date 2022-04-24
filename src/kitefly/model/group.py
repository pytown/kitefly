from typing import Iterable, List, Tuple, Union
from kitefly.filter.filter import Filter

from kitefly.util import generate_key

from .step import Step

class Group(Step):
  """
  Entity used to group multiple steps together, useful mostly for adding dependency relationships en-masse
  """
  def __init__(self, steps: Iterable[Step], *, key: str = "", label: str = "", **kwargs):
    super().__init__(**kwargs)
    self._steps: list[Step] = list(steps)
    self.label = label
    self.key = generate_key(label or 'Group')

  def __iadd__(self, value: Step) -> 'Group':
    if isinstance(value, Group):
      self._steps += value.steps
    else:
      self._steps.append(value)
    return self

  def __add__(self, value: Step) -> 'Group':
    group = Group(self._steps)
    group += value
    return group

  def __rshift__(self, dep: Union[Step, Iterable[Step]]) -> 'Group':
    for item in self._steps:
      item >> dep
    return self

  def __lshift__(self, dep: Union[Step, Iterable[Step]]) -> 'Group':
    for item in self._steps:
      item << dep
    return self

  def filtered(self, filter: Filter) -> 'Group':
    fs = [s for s in self._steps if filter(s)]
    return Group(fs, label=self.label)

  @property
  def steps(self) -> list[Step]:
    """
    Return a flattened list of steps
    """
    steps: list[Step] = []
    for step in self._steps:
      if isinstance(step, Group):
        steps += step.steps
      else:
        steps.append(step)
    return steps

  def asdict(self) -> dict:
    return {
      "group": self.label or "Group",
      "key": self.key,
      "steps": [s.asdict() for s in self.steps]
    }
