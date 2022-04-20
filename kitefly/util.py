import os
import re
from typing import Any, Iterable, Pattern, TypeVar, Union, cast

RE_NONID = re.compile(r"[^a-zA-Z0-9_]")
RE_MULTI_US = re.compile(r"__+")
T = TypeVar("T")
ST = TypeVar("ST")

KEY_COUNT = {}


def generate_key(name: str) -> str:
    """
    Given a display name, generate a global unique value suitable
    for use as a step key in Buildkite.
    """
    if not name:
        return ""
    norm = name.lower()
    for regex in (RE_NONID, RE_MULTI_US):
        norm = regex.sub("_", norm)
    if norm not in KEY_COUNT:
        KEY_COUNT[norm] = 1
        return norm
    suffix = f"__kf__{KEY_COUNT[norm]}"
    KEY_COUNT[norm] += 1
    return f"{norm}{suffix}"


def is_iterable(v: Any) -> bool:
    """
    Return True if the provided object is iterable.
    """
    try:
        _ = iter(v)
    except TypeError:
        return False
    return True


def as_iterable(v: Union[T, Iterable[T]]) -> Iterable[T]:
    """
    Convert passed object to a tuple.
    """
    if is_iterable(v):
        return cast(Iterable, v)
    else:
        return (cast(T, v),)


def glob(pattern: str) -> Pattern:
    """
    Return a compiled regular expression that will match full filepaths
    using the provided glob pattern.
    """
    escaped = re.escape(pattern)
    globkey = "__:GLOB:__"
    pattern = (
        escaped.replace("\\*\\*/", globkey)
        .replace("\\*\\*", globkey)
        .replace("\\*", f"[^{os.sep}]*")
        .replace(globkey, ".*")
    )
    return re.compile(pattern)
