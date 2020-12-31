from .step import Step

class Wait(Step):
  """
  Entity representing a "wait" step in a Buildkite pipeline
  """
  def __init__(
    self,
    continue_on_failure: bool = False,
    **kwargs
  ):
    super().__init__(**kwargs)
    self.continue_on_failure = continue_on_failure

  def asdict(self) -> dict:
    d = super().asdict()
    d["wait"] = "~"
    if self.continue_on_failure:
      d["continue_on_failure"] = True
    return d

