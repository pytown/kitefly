from typing import Iterable, List, Optional, Tuple, Union

from .group import Group
from .step import Step
from .target import Target

class Pipeline:
  """
  Methods for manipulating entire pipelines of steps, including
  the important role of rendering a de-duplicated properly
  ordered collection via steps(), or filtering based on
  targets and tags.
  """

  def __init__(self, *steps: Tuple[Union[Step, Group]]):
    self.items: List[Union[Step, Group]] = list(steps)

  def __iadd__(self, value: Union[Step, Group]):
    self.items.append(value)

  def filter(
      self,
      targets: Iterable[Target]=(),
      tags: Iterable[str]=(),
      exclude_tags: Iterable[str]=()
    ) -> 'Pipeline':
    """
    Filter the pipeline with the optional provided values and return a flattened
    list of steps with duplicate steps (via key) removed.
    """
    return Pipeline(*self.items)

  def steps(self) -> List[Step]:
    """
    Flatten nested group structure into a list of Step objects where:
    1. Steps with keys (Command steps) will be de-duplicated, such that the last instance
       of that Step in the list is preserved
    2. Multiple Wait steps in a row will be removed from the beginning/end of the step list
    """
    # (1) Iterate through items and flatten into a list of Step objects
    steps: List[Step] = []
    for item in self.items:
      coll = [step]
      if isinstance(item, Group):
        coll = item.steps()
      for step in coll:
          steps.append(step)

    # (2) Iterate through all steps and ensure all dependents are added to the list of steps,
    #     even if they weren't in the list of steps added directly to the pipeline
    seen = set()
    queue = []
    while queue or not seen:
      for dep in queue:
        steps.append(dep)
      queue = []
      for step in steps:
        if step not in seen:
          seen.add(step)
          for dep in step.dependents():
            if dep not in seen:
              seen.add(dep)
              queue.append(dep)

    # (3) Remove any depends_on keys for filtered-out steps
    keys = set([step.key for step in steps if isinstance(step, Command)])
    for step in steps:
      step.depends_on = [key for key in step.depends_on if key in keys]

    # (4) Remove duplicate steps (via key property) and only preserve
    #     the last instance of that step in the list.
    steps.reverse()
    uniq: List[Step] = []
    seen = set()
    for step in steps:
      if not step.key or step.key not in seen:
        uniq.append(step)
        if step.key:
          seen.add(step.key)
    uniq.reverse()
    return uniq


  def targets(self) -> List[Target]:
    """
    Return the unique set of targets for the current Pipeline
    """
    seen = set()
    for step in self.steps():
      for target in step.targets:
        seen.add(target)
    return list(seen)


  def asdict(self) -> dict:
    return {
      "steps": [s.asdict() for s in self.steps()]
    }