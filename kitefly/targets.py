
from .model import Target
from .git import Git

def find_matching_targets(targets: List[Target], base_branch: str) -> List[Target]:
  """
  Given a list of targets, return the list of targets that match by comparing
  the current repository's branch against the base branch
  """
  files_changed = Git.files_changed_since_branch(base_branch)
  return [target for target in targets if any(target.match(name) for name in files_changed)]