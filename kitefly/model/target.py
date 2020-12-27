from typing import List, Tuple

class Target:
  def __init__(self, *file_patterns: Tuple[str]):
    self.file_patterns: List[str] = list(file_patterns)
    self.depends_on: List[Target] = []

  def __rshift__(self, dep: 'Target') -> 'Target':
    self.depends_on.append(dep)
    return self