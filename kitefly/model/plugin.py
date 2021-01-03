class Plugin:
  """
  A Plugin configuration which may be applied to steps.

  See: https://buildkite.com/docs/plugins
  """
  def __init__(self, name: str, args: dict):
    self.name = name
    self.args = args