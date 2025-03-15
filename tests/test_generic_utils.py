from typing import Dict, Generic, List, Set, Tuple, TypeVar

from pieceful.generic_utils import is_generic


def test_is_generic():
    T = TypeVar("T")

    class InventoryOldGeneric(Generic[T]):  # Generic class
        pass

    class InventoryNewGeneric[S]:
        pass

    class NonGeneric:
        pass

    assert is_generic(list[int])
    assert is_generic(list)
    assert is_generic(List[int])
    assert is_generic(List)

    assert is_generic(tuple[int])
    assert is_generic(tuple)
    assert is_generic(Tuple[int])
    assert is_generic(Tuple)

    assert is_generic(dict[int, str])
    assert is_generic(dict)
    assert is_generic(Dict[int, str])
    assert is_generic(Dict)

    assert is_generic(set[int])
    assert is_generic(set)
    assert is_generic(Set[int])
    assert is_generic(Set)

    assert is_generic(InventoryOldGeneric)
    assert is_generic(InventoryNewGeneric)

    assert not is_generic(NonGeneric)
    assert not is_generic(int)
    assert not is_generic(str)
    assert not is_generic(float)
    assert not is_generic(bool)
