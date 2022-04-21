import os

from kitefly import GitFilter, Command, Target, Pipeline
from kitefly.filter.filter import Filter
import kitefly.filter.git_filter


class GitMocked:
    def __init__(self, file_list: list[str]):
        self.file_list = file_list
        self._orig_check_call = None
        self._orig_check_output = None

    def __enter__(self):
        self.orig_check_call = kitefly.filter.git_filter.check_call
        self.orig_check_output = kitefly.filter.git_filter.check_output
        kitefly.filter.git_filter.check_call = self._check_call
        kitefly.filter.git_filter.check_output = self._check_output

    def __exit__(self, _1, _2, _3):
        kitefly.filter.git_filter.check_call = self._orig_check_call
        kitefly.filter.git_filter.check_output = self._orig_check_output

    def _check_call(self, *args, **kwargs):
        return True

    def _check_output(self, cmd, *args, **kwargs):
        if len(cmd) < 2:
            return ""
        if cmd[1] == "rev-parse":
            return os.getcwd()
        elif cmd[1] == "diff":
            return "\n".join(self.file_list) + "\n"


def test_git_filter():
    with GitMocked(["README.md", "app/file.py"]):
        c1 = Command("Run cmd", "cmd.sh", targets=[Target("**/*.py")])
        c2 = Command("Library Tests", "libtest.sh", targets=[Target("lib/**/*.py")])
        steps = Pipeline([c1, c2]).filtered(GitFilter(base_branch="main")).steps
        assert len(steps) == 1
        assert steps[0].key == "run_cmd"

        # Filtering should not happen without a base branch
        steps = Pipeline([c1, c2]).filtered(GitFilter()).steps
        assert len(steps) == 2


def test_base_filter():
    f = Filter()
    assert f(None) == False
