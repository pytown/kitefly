from typing import Any, Dict, List, Optional, Union

from .plugin import Plugin
from .step import Step
from .retry import AutomaticRetry, ManualRetry

from ..util import generate_key


class Command(Step):
    """
    A Step which runs an executable in the repository and marks the step as
    pass/fail based on exit code.

    See: https://buildkite.com/docs/pipelines/command-step
    """

    def __init__(
        self,
        label: str,
        command: str,
        *,
        ## sort alphabetically:
        agents: Optional[dict] = None,
        artifact_paths: Union[str, List[str]] = "",
        automatic_retries: Union[None, int, List[AutomaticRetry]] = None,
        concurrency: int = 0,
        concurrency_group: str = "",
        env: Optional[dict] = None,
        key: str = "",
        manual_retry: Optional[ManualRetry] = None,
        parallelism: int = 0,
        plugins: Optional[List[Plugin]] = None,
        priority: Optional[int] = None,
        skip_reason: str = "",
        soft_fail: Union[bool, list] = False,
        tags: List[str] = None,
        timeout_in_minutes: int = 0,
        **kwargs
    ):
        super().__init__(tags=tags, **kwargs)
        self.key = key or generate_key(label)
        self.label = label
        self.command = command
        self.env = env or {}
        self.agents = agents or {}
        self.automatic_retries: List[AutomaticRetry] = []
        self.soft_fail = soft_fail
        if automatic_retries:
            if isinstance(automatic_retries, int):
                self.automatic_retries = [AutomaticRetry(automatic_retries)]
            else:
                self.automatic_retries = list(automatic_retries)
        self.manual_retry = manual_retry
        self.concurrency = concurrency
        self.concurrency_group = concurrency_group
        self.plugins = plugins
        self.priority = priority
        self.artifact_paths: List[str] = []
        if artifact_paths:
            if isinstance(artifact_paths, str):
                self.artifact_paths = artifact_paths.split(";")
            else:
                self.artifact_paths = artifact_paths
        self.skip_reason = skip_reason
        self.parallelism = parallelism
        self.timeout_in_minutes = timeout_in_minutes

    def asdict(self) -> dict:
        d = super().asdict()
        d["command"] = self.command
        d["label"] = self.label
        d["key"] = self.key

        # Setup inheritable properties using class-based defaults using MRO
        # to aggregate hash and list types, or determine the first valid value
        # for scalar types like timeout_in_minutes
        env: dict[str, str] = {}
        agents: dict[str, str] = {}
        artifact_paths = set(self.artifact_paths or [])
        plugins = set(self.plugins or [])
        timeout_in_minutes = self.timeout_in_minutes
        for cls in self.classes():
            env.update(getattr(cls, "env", {}))
            agents.update(getattr(cls, "agents", {}))
            artifact_paths |= set(getattr(cls, "artifact_paths", []))
            plugins |= set(getattr(cls, "plugins", []))
            if not timeout_in_minutes:
                timeout_in_minutes = getattr(cls, "timeout_in_minutes", 0)
        env.update(self.env)
        agents.update(self.agents)

        if env:
            d["env"] = env
        if agents:
            d["agents"] = agents
        if artifact_paths:
            d["artifact_paths"] = list(sorted(list(artifact_paths)))
        if timeout_in_minutes:
            d["timeout_in_minutes"] = timeout_in_minutes
        if plugins:
            d["plugins"] = {}
            for plugin in list(plugins):
                d["plugins"][plugin.name] = plugin.args
        if self.priority is not None:
            d["priority"] = self.priority
        if self.manual_retry or self.automatic_retries:
            retry: Dict[str, Any] = {}
            if self.manual_retry:
                retry["manual"] = self.manual_retry.asdict()
            if self.automatic_retries:
                retry["automatic"] = [r.asdict() for r in self.automatic_retries]
            d["retry"] = retry

        if self.soft_fail:
            if isinstance(self.soft_fail, list):
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

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self) -> str:
        return f"Command(key={self.key}, label={self.label})"