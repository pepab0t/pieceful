from functools import lru_cache
from types import UnionType
from typing import Annotated, Any, Generic, Literal, Type, TypeAliasType, Union, get_args, get_origin


@lru_cache(typed=True)
def is_generic(cls: Type[object]) -> bool:
    # If cls is a typing generic alias (e.g., List, Dict), get_origin(cls) is not None
    if (get_origin(cls)) not in (None, Annotated, Literal, Union, UnionType):
        return True

    # If cls is a user-defined generic, it should have Generic in its bases
    if isinstance(cls, type) and any(issubclass(base, Generic) for base in cls.__bases__):
        return True

    # Check if it's a built-in generic like list, dict, set, etc.
    if cls in {list, dict, set, tuple}:  # Extend with more built-in generics if needed
        return True

    return False


def _resolve_type_alias(cls):
    while cls.__class__ is TypeAliasType:
        cls = cls.__value__
    return cls


def is_subclass(cls, parent) -> bool:
    # TODO union? literal?
    cls = _resolve_type_alias(cls)
    parent = _resolve_type_alias(parent)

    if parent is object or parent is Any:
        return True

    if cls.__class__ is not parent.__class__:
        if get_origin(parent) in (UnionType, Union):
            return any(is_subclass(cls, arg) for arg in get_args(parent))
        if get_origin(cls) is Literal:
            return all(is_subclass(getattr(arg, "__orig_class__", arg.__class__), parent) for arg in get_args(cls))
        if get_origin(parent) is Annotated:
            return is_subclass(cls, get_args(parent)[0])
        if get_origin(cls) is Annotated:
            return is_subclass(get_args(cls)[0], parent)
        if cls.__class__ is type and is_generic(parent):
            return any(is_subclass(base, parent) for base in cls.__orig_bases__)
        return False

    if is_generic(cls):
        return issubclass(get_origin(cls), get_origin(parent)) and get_args(cls) == get_args(parent)

    if get_origin(cls) is Literal:
        parent_args = set(get_args(parent))
        return len(set(get_args(cls)) - parent_args) == 0

    if get_origin(parent) is Annotated:
        return is_subclass(get_args(cls)[0], get_args(parent)[0])

    return issubclass(cls, parent)
