import re
from typing import Tuple, Union, TypeVar

RE_NONID = re.compile(r'[^a-zA-Z0-9_]')
RE_MULTI_US = re.compile(r'__+')
T = TypeVar('T')

KEY_COUNT = {}

def generate_key(name: str) -> str:
    """
    Given a display name, generate a global unique value suitable
    for use as a step key in Buildkite.
    """
    norm = name.lower()
    for regex in (RE_NONID, RE_MULTI_US):
        norm = regex.sub('_', norm)
    if norm not in KEY_COUNT:
        KEY_COUNT[norm] = 1
        return norm
    suffix = f"__kf__{KEY_COUNT[norm]}"
    KEY_COUNT[norm] += 1
    return f"{norm}{suffix}"


def is_iterable(v: any) -> bool:
    """
    Return True if the provided object is iterable.
    """
    try:
        _ = iter(v)
    except TypeError:
        return False
    return True


def as_tuple(v: Union[Tuple[T], T]) -> Tuple[T]:
    """
    Convert passed object to a tuple.
    """
    if type(v) == tuple:
        return tuple(v)
    elif is_iterable(v):
        return tuple(v)
    return (v,)