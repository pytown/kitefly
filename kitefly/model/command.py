from typing import Iterable, Optional, Union
from copy import deepcopy

from .agents import Agents
from .env import Env
from .step import Step

from ..util import generate_key, as_tuple

class Command(Step):
  """
  Entity representing a command step in a Buildkite pipeline
  """

  def __init__(
      self,
      name: str,
      command: str,
      env: Optional[dict]=None,
      agents: Optional[dict]=None,
      **kwargs
    ):
    self.key = generate_key(name)
    self.name = name
    self.command = command
    self.env = Env(env or {})
    self.agents = Agents(agents or {})
    super().__init__(**kwargs)

  def __rshift__(self, deps: Union[Step, Iterable[Step]]) -> 'Command':
    """
    Declare a triggering relationship from the command step to another step. When this operator
    is executed, the given dependent steps will include this step's key in their depends_on key list

    """
    for dep in as_tuple(deps):
      dep.depends_on.push(self.key)
    return self

  def __add__(self, item: Union[Env, Agents]) -> 'Command':
    """
    """
    cp = deepcopy(self)
    cp += item
    return cp

  def __iadd__(self, item: Union[Env, Agents]) -> 'Command':
    if isinstance(item, Env):
      self.env += item
    elif isinstance(item, Agents):
      self.agents += item
    return self
