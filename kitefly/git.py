from typing import Dict, List
from subprocess import check_output, check_call
import os

class Git:
  _files_changed_since_branch: Dict[str, List[str]] = {}

  @classmethod
  def files_changed_since_branch(cls, branch: str) -> List[str]:
    if not branch in cls._files_changed_since_branch:
      check_call(["git", "fetch", "origin", branch])
      lines = check_output([
        "git",
        "diff",
        "--name-only",
        branch
      ], universal_newlines=True).split(os.linesep)
      cls._files_changed_since_branch[branch] = [name.strip() for name in lines if name.strip()]
    return cls._files_changed_since_branch[branch]