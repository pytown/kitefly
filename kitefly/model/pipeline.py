from typing import Union, Iterable

from .command import Command
from .group import Group
from .step import Step
from .target import Target
from .wait import Wait

from ..filter.filter import Filter


class Pipeline:
    """
    Methods for manipulating entire pipelines of steps, including
    the important role of rendering a de-duplicated properly
    ordered collection via steps(), or filtering based on
    targets and tags.
    """

    def __init__(self, steps: Iterable[Step]):
        self.items: list[Step] = list(steps)

    def filtered(self, filter: Filter) -> "Pipeline":
        """
        Filter the pipeline with the optional provided values and return a flattened
        list of steps with duplicate steps (via key) removed.
        """
        filtered: list[Step] = []
        for item in self.items:
            if isinstance(item, Group):
                filtered.append(item.filtered(filter))
            if isinstance(item, Step):
                if filter(item):
                    filtered.append(item)
        return Pipeline(filtered)

    @property
    def steps(self) -> list[Step]:
        # (1) Dependent Inclusion
        # Iterate through all steps and ensure all dependents are added to the list of steps,
        # even if they weren't in the list of steps added directly to the pipeline
        steps = self.items
        all_steps = steps[:]
        for step in steps:
            if isinstance(step, Group):
                all_steps += step.steps
        seen = set(all_steps)
        for step in all_steps:
            for dep in step.dependents:
                if dep not in seen:
                    seen.add(dep)
                    steps.append(dep)
                    all_steps.append(dep)

        # (2) Clean depends_on
        # Remove any depends_on keys for steps that have been removed via filtering
        keys = set([step.key for step in all_steps if isinstance(step, Command)])
        for step in all_steps:
            step.depends_on = [key for key in step.depends_on if key in keys]

        # (3) Remove empty groups
        cleaned: list[Step] = []
        for step in steps:
            if not isinstance(step, Group) or step.steps:
                cleaned.append(step)
        steps = cleaned

        # (4) Remove unnecessary Waits
        #     Remove runs of identical wait steps, and strip waits from the beginning/end
        #     of the pipeline
        last_step = None
        cleaned = []
        for step in steps:
            is_valid = True
            if isinstance(step, Wait):
                is_valid = last_step is not None and last_step != step
            last_step = step
            if is_valid:
                cleaned.append(step)
        if isinstance(cleaned[-1], Wait):
            cleaned.pop()
        steps = cleaned

        return steps

    def asdict(self) -> dict:
        d: dict = {"steps": [s.asdict() for s in self.steps]}
        return d

    def asyaml(self) -> str:
        import yaml

        return yaml.dump(self.asdict())
