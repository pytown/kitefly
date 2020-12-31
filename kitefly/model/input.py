from typing import List, Optional

from .step import Step

class Option:
  def __init__(self, label: str, value: str):
    self.label = label
    self.value = value

class Field:
  def __init__(self, key: str):
    self.key = key

class SelectField(Field):
  def __init__(
    self,
    key: str,
    options: List[Option],
    hint: str = "",
    required: bool = True,
    multiple: bool = False,
    default: Union[str, List[str]] = ""
  ):
    super.__init__(key)
    self.options = options
    self.hint = hint
    self.required = required
    self.multiple = multiple
    self.default = default

  def asdict(self) -> dict:
    d = {
      "key": self.key,
      "options": []
    }
    for option in self.options:
      d["options"].append({
        "label": option.label,
        "value": option.value,
      })
    if self.hint:
      d["hint"] = self.hint
    if not self.required:
      d["required"] = self.required
    if self.multiple:
      d["multiple"] = self.multiple
    if self.default:
      d["default"] = self.default
    return d

class InputField(Field):
  def __init__(
    self,
    key: str,
    required: bool = True,
    hint: str = "",
    default: str = ""
  ):
    super.__init__(key)
    self.required = required
    self.hint = hint
    self.default = default

  def asdict(self) -> dict:
    d = {"key": self.key, "required": self.required}
    if self.hint:
      d["hint"] = self.hint
    if self.default:
      d["default"] = self.default


class Input(Step):
  """
  A step that prompts the user for information that can be used in
  dependent builds
  """
  def __init__(
    self,
    label: str,
    prompt: str = "",
    fields: Optional[List[Field]] = None,
    blocked_state: str = "",
    **kwargs
  ):
    self.prompt = prompt
    self.label = label
    self.blocked_state = blocked_state
    self.fields = fields or []
    super().__init__(**kwargs)

  def asdict(self) -> dict:
    d = super().asdict()
    d["block"] = self.label
    if self.prompt:
      d["prompt"] = self.prompt
    if self.fields:
      d["fields"] = [f.asdict() for f in self.fields]
    if self.blocked_state:
      d["blocked_state"] = self.blocked_state
    return d


class Block(Input):
  """
  An Input step that implicitly blocks any steps following it, functioning much like a Wait step
  """
  def asdict(self) -> dict:
    d = super().asdict()
    d["block"] = d["input"]
    del d["input"]
    return d