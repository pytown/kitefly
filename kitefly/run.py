import os
import sys
from yaml import dump as yaml_dump

from .model import Pipeline

VERSION = "0.1.0"

def run(
  pipeline: Pipeline,
  filter_by_base_branch: bool = False,
  base_branch: str = "",
  only_tags: Optional[List[str]] = None,
):
  """
  Execute the given Pipeline, filtering by base-branch comparison if specified,
  and print the resulting Buildkite YAML output
  """
  filtered_pipeline = pipeline
  if filter_by_base_branch:
    targets = pipeline.targets()
    selected_base_branch: str = base_branch or os.getenv('BUILDKITE_BASE_BRANCH')
    if not selected_base_branch:
      sys.stderr.write("[WARN] Base branch not specified, will not filter pipeline. BUILDKITE_BASE_BRANCH must be defined.")
    else:
      matched_targets = find_matching_targets(
        targets=pipeline.targets(),
        base_branch=selected_base_branch,
      )
      filtered_pipeline = pipeline.filter(targets=[matched_targets])
  if only_tags:


  print(yaml_dump(filtered_pipeline.asdict()))