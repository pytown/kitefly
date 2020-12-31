from typing import Iterable, List, Tuple, Union

from .agents import Agents
from .env import Env

from .step import Step

class Group:
  def __init__(self, *steps: Tuple[Union[Step, Group]]):
    self.items: List[Union[Step, Group]] = list(steps)

  def __iadd__(self, value: Union[Step, 'Group']) -> 'Group':
    self.items.append(value)

  def __add__(self, value: Union[Step, 'Group']) -> 'Group':
    group = Group(*self.items)
    group += value
    return group

  def steps(self) -> List[Step]:
    steps: List[Step] = []
    for item in self.items:
      if isinstance(item, Group):
        steps += item.steps()
      else:
        steps.append(item)
    return steps