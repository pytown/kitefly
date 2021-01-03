class AutomaticRetry:
  """
  Configuration entry for an automatic retry on a Command Step, of which there may be
  one or more limit settings bound to particular exit codes. The '*' exit code (default)
  will match all exit codes.
  """
  def __init__(self, limit: int, exit_code: str = '*'):
    self.limit = limit
    self.exit_code = exit_code

  def asdict(self) -> dict:
    return {"exit_code": self.exit_code, "limit": self.limit}

class ManualRetry:
  """
  Configuration entry for manual retry on a Command Step.
  """
  def __init_(self, allowed: bool = True, permit_on_passed: bool = False, reason: str = ""):
    self.allowed = allowed
    self.permit_on_passed = permit_on_passed
    self.reason = reason

  def asdict(self) -> dict:
    d = {
      "allowed": self.allowed,
    }
    if self.permit_on_passed:
      d["permit_on_passed"] = True
    if self.reason:
      d["reason"] = self.reason
    return d