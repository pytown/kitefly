from typing import Generic, Optional, Union, TypeVar

T = TypeVar('T')

class DictWrapper(Generic[T]):
  def __init__(self, data: Optional[dict]=None):
    self.data = data or {}

  def __getitem__(self, key: str) -> Optional[str]:
    v = self.data.get(key)
    return v if v == None else str(v)

  def __add__(self, env: Union[T, dict]) -> T:
    comb = self.__class__()
    comb += self
    comb += env
    return comb

  def __iadd(self, item: Union[T, dict]) -> T:
    self.data.update(item.data if isinstance(item, DictWrapper) else item)
    return self