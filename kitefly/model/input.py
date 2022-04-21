from typing import Any, Dict, List, Optional, Union

from .step import Step

class Option:
  def __init__(self, label: str, value: str):
    self.label = label
    self.value = value

class Field:
  def __init__(self, key: str):
    self.key = key

  def asdict(self) -> Dict[str, Any]:
    raise NotImplementedError("Field is an abstract class")


class SelectField(Field):
  def __init__(
    self,
    key: str,
    name: str,
    options: List[Option],
    hint: str = "",
    required: bool = True,
    multiple: bool = False,
    default: Union[str, List[str]] = ""
  ):
    super().__init__(key)
    self.name = name
    self.options = options
    self.hint = hint
    self.required = required
    self.multiple = multiple
    self.default = default

  def asdict(self) -> dict:
    d: Dict[str, Any] = {
      "key": self.key,
      "select": self.name,
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

class TextField(Field):
  """
  A text field for Input step.
  """
  def __init__(
    self,
    key: str,
    name: str,
    required: bool = True,
    hint: str = "",
    default: str = ""
  ):
    super().__init__(key)
    self.name = name
    self.required = required
    self.hint = hint
    self.default = default

  def asdict(self) -> Dict[str, Any]:
    d: Dict[str, Any] = {"key": self.key, "required": self.required, "text": self.name}
    if self.hint:
      d["hint"] = self.hint
    if self.default:
      d["default"] = self.default
    return d

class Input(Step):
  """
  A step that prompts the user for information that can be used in
  dependent builds

  See: https://buildkite.com/docs/pipelines/input-step
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
  An Input Step that implicitly blocks any steps following it, functioning as a Wait and Input Step combined.

  See: https://buildkite.com/docs/pipelines/block-step
  """
  def asdict(self) -> dict:
    d = super().asdict()
    d["block"] = d["input"]
    del d["input"]
    return d