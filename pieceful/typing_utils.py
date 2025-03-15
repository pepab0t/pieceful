from functools import lru_cache
from typing import Generic, Type, get_origin


# @lru_cache
def is_generic(cls: Type[object]) -> bool:
    # If cls is a typing generic alias (e.g., List, Dict), get_origin(cls) is not None
    if get_origin(cls) is not None:
        return True

    # If cls is a user-defined generic, it should have Generic in its bases
    if isinstance(cls, type) and any(issubclass(base, Generic) for base in cls.__bases__):
        return True

    # Check if it's a built-in generic like list, dict, set, etc.
    if cls in {list, dict, set, tuple}:  # Extend with more built-in generics if needed
        return True

    return False
