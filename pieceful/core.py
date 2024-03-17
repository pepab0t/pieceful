from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Type, TypeVar

from .entity import Parameter
from .enums import Scope
from .parameter_parser import get_parameters

_T = TypeVar("_T")
Constructor = Callable[..., _T]


class _Initializer:
    __slots__ = ("constructor", "params")

    def __init__(self, constructor: Constructor):
        self.constructor = constructor
        self.params: Iterable[Parameter] = get_parameters(constructor)

    def initialize(self) -> Any:
        return self.constructor(**{param.name: param.get() for param in self.params})


class PieceData(ABC):
    __slots__ = ("type", "_initializer", "_instance")

    def __init__(self, type: Type[Any], constructor: Constructor) -> None:
        self.type: Type[Any] = type
        self._initializer: _Initializer = _Initializer(constructor)
        self._instance: Any = None

    @abstractmethod
    def get_instance(self): ...


class OriginalPieceData(PieceData):
    def get_instance(self):
        return self._initializer.initialize()


class UniversalPieceData(PieceData):
    def get_instance(self):
        if self._instance is None:
            self._instance = self._initializer.initialize()
        return self._instance


def piece_data_factory(
    type: Type[Any], scope: Scope, constructor: Constructor
) -> PieceData:
    if scope == Scope.UNIVERSAL:
        return UniversalPieceData(type, constructor)
    elif scope == Scope.ORIGINAL:
        return OriginalPieceData(type, constructor)
    else:
        raise ValueError(f"Invalid scope: {scope}")
