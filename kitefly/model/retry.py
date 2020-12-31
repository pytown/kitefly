class AutomaticRetry:
  """
  Entity specifying automatic retry configuration.
  """
  def __init__(self, limit: int, exit_code: str = '*'):
    self.limit = limit
    self.exit_code = exit_code

  def asdict(self) -> dict:
    return {"exit_code": self.exit_code, "limit": self.limit}

class ManualRetry:
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