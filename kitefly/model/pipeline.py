from typing import Iterable, List, Optional, Set, Tuple, Union

from .command import Command
from .group import Group
from .step import Step
from .target import Target
from .wait import Wait

class PipelineFilter:
  def __init__(
      self,
      targets: Optional[Iterable[Target]] = None,
      only_tags: Iterable[str] = (),
      exclude_tags: Optional[Iterable[str]] = None
  ):
    self.targets = targets
    self.only_tags = only_tags
    self.exclude_tags = exclude_tags

  def include(self, items: List[Union[Step, Group]], item: Union[Step, Group]):
    if isinstance(item, Step):
      if self.targets is not None and not (set(item.targets()) & set(self.targets)):
        return
      if self.only_tags and not (set(item.tags()) & set(self.only_tags)):
        return
      if self.exclude_tags and (set(item.tags()) & set(self.exclude_tags)):
        return
      items.append(item)
    elif isinstance(item, Group):
      filtered_items = []
      for group_item in item.items:
        self.include(filtered_items, group_item)
      if not filtered_items:
        return
      items.append(Group(*filtered_items))


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
      targets: Optional[Iterable[Target]] = None,
      only_tags: Iterable[str] = (),
      exclude_tags: Iterable[str] = ()
    ) -> 'Pipeline':
    """
    Filter the pipeline with the optional provided values and return a flattened
    list of steps with duplicate steps (via key) removed.
    """
    filtered = []
    pf = PipelineFilter(targets=targets, only_tags=only_tags, exclude_tags=exclude_tags)
    for item in self.items:
      pf.include(filtered, item)
    return Pipeline(*filtered)

  def steps(self) -> List[Step]:
    """
    Flatten nested group structure into a list of Step objects where:
    1. Steps with keys (Command steps) will be de-duplicated, such that the last instance
       of that Step in the list is preserved
    2. Multiple Wait steps in a row will be removed from the beginning/end of the step list
    """
    # (1) Flatten
    # Iterate through items and flatten Groups into a one-dimensional list of Step objects
    steps: List[Step] = []
    for item in self.items:
      coll = [item]
      if isinstance(item, Group):
        coll = item.steps()
      for step in coll:
          steps.append(step)

    # (2) Dependent Inclusion
    # Iterate through all steps and ensure all dependents are added to the list of steps,
    # even if they weren't in the list of steps added directly to the pipeline
    seen = set()
    queue = []
    while queue or not seen:
      for dep in queue:
        steps.append(dep)
      queue = []
      for step in steps:
        if step not in seen:
          seen.add(step)
          for dep in step.dependents:
            if dep not in seen:
              seen.add(dep)
              queue.append(dep)

    # (3) Clean depends_on
    # Remove any depends_on keys for filtered-out steps
    keys = set([step.key for step in steps if isinstance(step, Command)])
    for step in steps:
      step.depends_on = [key for key in step.depends_on if key in keys]

    # (4) De-duplicate
    # Remove duplicate steps and only preserve the final instance of that
    # step in the list.
    steps.reverse()
    uniq: List[Step] = []
    seen: Set[Step] = set()
    for step in steps:
      if isinstance(step, Wait) or step not in seen:
        uniq.append(step)
        seen.add(step)
    uniq.reverse()
    steps = uniq

    # (5) Remove unnecessary Waits
    # Remove runs of identical wait steps, and strip waits from the beginning/end
    # of the pipeline
    last_step = None
    cleaned: List[Step] = []
    for step in steps:
      is_valid = True
      if isinstance(step, Wait):
        is_valid = last_step and last_step != step
      last_step = step
      if is_valid:
        cleaned.append(step)
    if isinstance(steps[-1], Wait):
      steps.pop()

    return steps

  def targets(self) -> List[Target]:
    """
    Return the unique set of targets for the current Pipeline
    """
    seen = set()
    for step in self.steps():
      for target in step.targets():
        seen.add(target)
    return list(seen)


  def asdict(self) -> dict:
    return {
      "steps": [s.asdict() for s in self.steps()]
    }