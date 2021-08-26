from typing import Any, Dict, Mapping, Optional

from .step import Step

class BuildAttributes:
  """
  Attributes used when triggering a build.
  """
  def __init__(
    self,
    message: str = "",
    commit: str = "",
    branch: str = "",
    meta_data: Optional[Mapping[str, str]] = None,
    env: Optional[Mapping[str, str]] = None,
  ):
    self.message = message
    self.commit = commit
    self.branch = branch
    self.meta_data = meta_data or {}
    self.env = env or {}

  def asdict(self) -> dict:
    d: Dict[str, Any] = {}
    if self.message:
      d["message"] = self.message
    if self.commit:
      d["commit"] = self.commit
    if self.branch:
      d["branch"] = self.branch
    if self.meta_data:
      d["meta_data"] = self.meta_data
    if self.env:
      d["env"] = self.env
    return d


class Trigger(Step):
  """
  A Step which triggers a build on another pipeline.

  See: https://buildkite.com/docs/pipelines/trigger-step
  """
  def __init__(
    self,
    pipeline: str,
    build: Optional[BuildAttributes] = None,
    label: str = "",
    asynchronous: bool = False,
    **kwargs
  ):
    super().__init__(**kwargs)
    self.pipeline = pipeline
    self.build = build
    self.label = label
    self.asynchronous = asynchronous

  def asdict(self) -> dict:
    d = super().asdict()
    d["trigger"] = self.pipeline
    if self.build:
      d["build"] = self.build.asdict()
    if self.label:
      d["label"] = self.label
    if self.asynchronous:
      d["async"] = True
    return d
