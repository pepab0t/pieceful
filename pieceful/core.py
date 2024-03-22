from abc import ABC, abstractmethod
from ast import Param
from typing import Any, Callable, Generic, Iterable, Type, TypeVar

from .entity import Parameter
from .enums import Scope
from .parameter_parser import get_parameters

_T = TypeVar("_T")
Constructor = Callable[..., _T]


# class _Initializer:
#     __slots__ = ("constructor", "params")

#     def __init__(self, constructor: Constructor):
#         self.constructor = constructor
#         self.params: Iterable[Parameter] = get_parameters(constructor)

# def initialize(self) -> Any:
#     return self.constructor(**{param.name: param.get() for param in self.params})


class PieceData(ABC, Generic[_T]):
    # __slots__ = ("type", "_initializer", "_instance")

    def __init__(self, type: Type[_T], constructor: Constructor) -> None:
        self.type: Type[_T] = type
        self.constructor = constructor
        self.parameters: Iterable[Parameter] = get_parameters(constructor)
        self._instance: _T | None = None

    @abstractmethod
    def get_instance(self) -> _T | None: ...

    @abstractmethod
    def initialize(self, parameters: dict[str, Any]) -> _T: ...


class OriginalPieceData(PieceData[_T]):

    def get_instance(self):
        return None

    def initialize(self, parameters):
        return self.constructor(**parameters)


class UniversalPieceData(PieceData[_T]):
    def get_instance(self):
        return self._instance

    def initialize(self, parameters):
        self._instance = self.constructor(**parameters)
        return self._instance


def piece_data_factory(type_: Type[_T], scope: Scope, constructor: Constructor) -> PieceData[_T]:
    if scope == Scope.UNIVERSAL:
        return UniversalPieceData[_T](type_, constructor)
    elif scope == Scope.ORIGINAL:
        return OriginalPieceData[_T](type_, constructor)
    else:
        raise ValueError(f"Invalid scope: {scope}")
