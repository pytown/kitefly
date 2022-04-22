from typing import Any, Dict


class AutomaticRetry:
    """
    Configuration entry for an automatic retry on a Command Step, of which there may be
    one or more limit settings bound to particular exit codes. The '*' exit code (default)
    will match all exit codes.
    """

    def __init__(self, limit: int, exit_code: str = "*"):
        self.limit = limit
        try:
            exit_code_int = int(exit_code)
        except ValueError:
            exit_code_int = -1
        self.exit_code = exit_code_int if exit_code_int >= 0 else exit_code

    def asdict(self) -> dict:
        return {"exit_code": self.exit_code, "limit": self.limit}


class ManualRetry:
    """
    Configuration entry for manual retry on a Command Step.
    """

    def __init__(
        self, allowed: bool = True, permit_on_passed: bool = False, reason: str = ""
    ):
        self.allowed = allowed
        self.permit_on_passed = permit_on_passed
        self.reason = reason

    def asdict(self) -> dict:
        d: Dict[str, Any] = {
            "allowed": self.allowed,
        }
        if self.permit_on_passed:
            d["permit_on_passed"] = True
        if self.reason:
            d["reason"] = self.reason
        return d
