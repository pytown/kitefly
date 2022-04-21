import functools
import os
import re
from subprocess import check_output, check_call
from typing import Dict, List

from .filter import Filter
from ..model.step import Step
from ..model.target import Target


class GitFilter(Filter):
    def __init__(self, base_branch: str = "") -> None:
        self.base_branch = base_branch or os.environ.get(
            "BUILDKITE_PULL_REQUEST_BASE_BRANCH", ""
        )
        self.match_cache: Dict[Target, bool] = {}
        super().__init__()

    def __call__(self, step: Step) -> bool:
        if not self.base_branch:
            return True
        for filepath in self._files_changed_since_branch(self.base_branch):
            for target in step.get_targets():
                if target.matches(filepath):
                    return True
        return False

    @functools.lru_cache()
    def _files_changed_since_branch(self, branch: str) -> List[str]:
        check_call(["git", "fetch", "origin", branch])
        git_root = check_output(
            ["git", "rev-parse", "--show-toplevel"], universal_newlines=True
        ).split(os.linesep)[0]
        lines = check_output(
            ["git", "diff", "--name-only", branch],
            universal_newlines=True,
            cwd=git_root,
        ).split(os.linesep)
        re_word_char = re.compile(r"\w")
        return [n.strip() for n in lines if re_word_char.match(n)]
