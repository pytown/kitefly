import os
from yaml import dump as yaml_dump
from typing import List, Optional

from .model import Pipeline, Target
from .targets import find_matching_targets

VERSION = "0.1.0"

def generate(
  pipeline: Pipeline,
  filter_by_base_branch: bool = False,
  base_branch: str = "",
  only_tags: Optional[List[str]] = None
) -> str:
  """
  Execute the given Pipeline, filtering by base-branch comparison if specified,
  and print the resulting Buildkite YAML output

  Raises a ValueError if filter_by_base_branch is set to True, but no base branch
  can be determined.

  Parameters:
  - pipeline:
      The Pipeline instance that has been composed from Kitefly models.
  - filter_by_base_branch:
      If True, run git commands to compare the current git HEAD against the given base branch.
  - base_branch:
      The base branch to use for filtering. If not specified, the BUILDKITE_BASE_BRANCH environmental
      variable will be used.
  - only_tags: Filter pipeline to contain steps marked with the given tags only.
  """
  matched_targets: Optional[List[Target]] = None
  if filter_by_base_branch:
    selected_base_branch: str = base_branch or os.getenv('BUILDKITE_BASE_BRANCH')
    if not selected_base_branch:
      raise ValueError(
        "[WARN] Base branch not specified, will not filter pipeline.\n"
        "The environmental variable BUILDKITE_BASE_BRANCH must be defined, or base_branch\n"
        "must be passed to the run() function."
      )
    else:
      matched_targets = find_matching_targets(
        targets=pipeline.targets(),
        base_branch=selected_base_branch,
      )
  filtered = pipeline.filter(
    targets=matched_targets,
    only_tags=only_tags,
  )
  return yaml_dump(filtered.asdict())
