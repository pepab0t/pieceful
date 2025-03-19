from typing import Annotated, Any, Dict, Generic, List, Literal, Set, Tuple, TypeVar, Union

from pieceful.typing_utils import is_generic, is_subclass


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
    assert not is_generic(Any)
    assert not is_generic(Literal[1])
    assert not is_generic(Annotated[int, "a"])
    assert not is_generic(int | str)
    assert not is_generic(Union[int, str])


def test_is_subclass():
    class Armor:
        pass

    class ChestArmor(Armor):
        pass

    class Inventory[T]:
        pass

    class SmallInventory[T](Inventory[T]):
        def __init__(self, value: T | None = None) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            return isinstance(other, SmallInventory) and self.value == other.value

        def __hash__(self) -> int:
            return hash(self.value)

    class ArmorInventory(Inventory[Armor]):
        pass

    class Character:
        pass

    class Mage(Character):
        pass

    assert is_subclass(Character, Character)
    assert is_subclass(Mage, Character)
    assert is_subclass(Inventory[int], Inventory[int])
    assert is_subclass(SmallInventory[int], Inventory[int])
    assert is_subclass(ArmorInventory, Inventory[Armor])
    assert is_subclass(Character, object)
    assert is_subclass(Character, Any)
    assert is_subclass(Inventory[int], object)
    assert is_subclass(Inventory[int], Any)
    assert is_subclass(Literal[1], Any)
    assert is_subclass(Literal[1], object)
    assert is_subclass(Literal[1], Literal[1])
    assert is_subclass(Literal[1], Literal[1, 2, 3])
    assert is_subclass(Literal[1], Literal[1, "string"])
    assert is_subclass(Literal[1], int)
    assert is_subclass(Literal[1, 2, 3], int)
    assert is_subclass(int, int | str)
    assert is_subclass(Literal[1], Literal[1] | Literal[2])
    str_inventory = Inventory[str]()
    assert is_subclass(Literal[str_inventory], Literal[str_inventory, Inventory[int]()])
    assert is_subclass(Literal["a", "b"], Literal["a", "b", "c"])
    assert is_subclass(Literal[SmallInventory[int]()], Literal[SmallInventory[int]()])  # has hash and equals
    assert is_subclass(Inventory[int], Inventory[str] | Inventory[int])
    assert is_subclass(Inventory[Literal[1]], Inventory[Literal[1]] | Inventory[str])
    assert is_subclass(Annotated[int, "a"], int)
    assert is_subclass(int, Annotated[int, "a"])
    assert is_subclass(Annotated[int, "a"], Annotated[int, "a"])
    assert is_subclass(Annotated[int, "b"], Annotated[int, "a"])
    assert is_subclass(Annotated[Inventory[int], "b"], Annotated[Inventory[int], "a"])
    assert is_subclass(Annotated[int, "b"], Annotated[int | str, "a"])
    assert is_subclass(Annotated[Literal[2], "b"], Annotated[Literal[1, 33] | Literal[2], "a"])

    assert not is_subclass(Inventory[int], Inventory)
    assert not is_subclass(Inventory, Inventory[int])
    assert not is_subclass(Inventory[ChestArmor], Inventory[Armor])
    assert not is_subclass(Inventory[Armor], Inventory[Any])
    assert not is_subclass(SmallInventory[ChestArmor], Inventory[Armor])
    assert not is_subclass(int, Literal[1])
    assert not is_subclass(Literal[1, "string"], int)
    assert not is_subclass(int, str)
    assert not is_subclass(Literal[ArmorInventory()], Literal[Inventory[Armor]()])
    assert not is_subclass(Literal[Inventory[str]()], Literal[Inventory[int]()])
    assert not is_subclass(Literal[Inventory[str]()], Literal[Inventory[str]()])
    assert not is_subclass(Annotated[Inventory[ChestArmor], "b"], Annotated[Inventory[Armor], "a"])
