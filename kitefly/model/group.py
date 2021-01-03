from typing import Iterable, List, Tuple, Union

from .agents import Agents
from .env import Env

from .step import Step

class Group:
  """
  Entity used to group multiple steps together, useful mostly for adding dependency relationships en-masse
  """
  def __init__(self, *steps: Tuple[Union[Step, Group]]):
    self.items: List[Union[Step, Group]] = list(steps)

  def __iadd__(self, value: Union[Step, 'Group']) -> 'Group':
    self.items.append(value)
    return self

  def __add__(self, value: Union[Step, 'Group']) -> 'Group':
    group = Group(*self.items)
    group += value
    return group

  def __rshift__(self, dep: Step) -> 'Group':
    for item in self.items:
      item >> dep
    return self

  def steps(self) -> List[Step]:
    steps: List[Step] = []
    for item in self.items:
      if isinstance(item, Group):
        steps += item.steps()
      else:
        steps.append(item)
    return steps