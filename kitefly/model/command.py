from typing import Iterable, List, Optional, Union
from copy import deepcopy

from .plugin import Plugin
from .step import Step
from .retry import AutomaticRetry, ManualRetry

from ..util import generate_key, as_tuple

class Command(Step):
  """
  Entity representing a command step in a Buildkite pipeline
  """

  def __init__(
      self,
      label: str,
      command: str,
      env: Optional[dict] = None,
      agents: Optional[dict] = None,
      automatic_retries: Union[None, int, List[AutomaticRetry]] = None,
      manual_retry: Optional[ManualRetry] = None,
      soft_fail: Union[bool, list] = False,
      artifact_paths: Union[str, List[str]] = "",
      concurrency: int = 0,
      concurrency_group: str = "",
      skip_reason: str = "",
      parallelism: int = 0,
      timeout_in_minutes: int = 0,
      plugins: Optional[List[Plugin]] = None,
      **kwargs
    ):
    cls = self.__class__
    self.key = generate_key(label)
    self.label = label
    self.command = command
    self.env = env or {}
    self.agents = agents or {}
    self.automatic_retries: List[AutomaticRetry] = []
    self.soft_fail = soft_fail
    if automatic_retries:
      if type(automatic_retries) == int:
        self.automatic_retries = [AutomaticRetry(automatic_retries)]
      else:
        self.automatic_retries = list(automatic_retries)
    self.manual_retry = manual_retry
    self.concurrency = concurrency
    self.concurrency_group = concurrency_group
    self.plugins = plugins
    self.artifact_paths = []
    if artifact_paths:
      if type(artifact_paths) is str:
        self.artifact_paths = artifact_paths.split(';')
      else:
        self.artifact_paths = artifact_paths
    self.skip_reason = skip_reason
    self.parallelism = parallelism
    self.timeout_in_minutes = timeout_in_minutes
    super().__init__(**kwargs)

  def asdict(self) -> dict:
    d = super().asdict()
    d["command"] = self.command
    d["label"] = self.label
    d["key"] = self.key

    # Setup inheritable properties using class-based defaults using MRO
    # to aggregate hash and list types, or determine the first valid value
    # for scalar types like timeout_in_minutes
    classes = [cls for cls in self.__class__.__mro__ if cls is not object]
    classes.reverse()
    env = {**self.env}
    agents = {**self.agents}
    artifact_paths = set(self.artifact_paths)
    plugins = set(self.plugins)
    timeout_in_minutes = self.timeout_in_minutes
    for cls in classes:
      env.update(getattr(cls, 'env', {})
      agents.update(getattr(cls, 'agents', {}))
      artifact_paths |= set(getattr(cls, 'artifact_paths', []))
      plugins |= set(getattr(cls, 'plugins', []))
      if not timeout_in_minutes:
        timeout_in_minutes = getattr(cls, 'timeout_in_minutes', 0)
    if env:
      d["env"] = env
    if agents:
      d["agents"] = agents
    if artifact_paths:
      d["artifact_paths"] = list(artifact_paths)
    if timeout_in_minutes:
      d["timeout_in_minutes"] = timeout_in_minutes
    if plugins:
      d["plugins"] = {}
      for plugin in list(plugins):
        d["plugins"][plugin.name] = plugin.args

    if self.manual_retry or self.automatic_retries:
      retry = {}
      if self.manual_retry:
        retry["manual"] = self.manual_retry.asdict()
      if self.automatic_retries:
        retry["automatic"] = [r.asdict() for r in self.automatic_retries]
      d["retry"] = retry

    if self.soft_fail:
      if type(self.soft_fail) == list:
        d["soft_fail"] = [{"exit_status": i} for i in self.soft_fail]
      elif self.soft_fail is True:
        d["soft_fail"] = True

    if self.concurrency:
      d["concurrency"] = self.concurrency
      if self.concurrency_group:
        d["concurrency_group"] = self.concurrency_group
    if self.parallelism:
      d["parallelism"] = self.parallelism
    if self.skip_reason:
      d["skip"] = self.skip_reason

    return d

  def __rshift__(self, deps: Union[Step, Iterable[Step]]) -> 'Command':
    """
    Declare a triggering relationship from the command step to another step. When this operator
    is executed, the given dependent steps will include this step's key in their depends_on key list
    """
    for dep in as_tuple(deps):
      dep.depends_on.push(self.key)
    return self
