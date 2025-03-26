from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, Type, TypeVar

from .enums import Scope
from .parameter_parser import get_parameters
from .parameters import Parameter

_T = TypeVar("_T")
Constructor = Callable[..., _T]


class PieceData(ABC, Generic[_T]):
    __slots__ = ("type", "_constructor", "parameters", "_instance")

    def __init__(self, type: Type[_T], constructor: Constructor[_T]) -> None:
        self.type: Type[_T] = type
        self._constructor = constructor
        self.parameters: Iterable[Parameter] = get_parameters(constructor)
        self._instance: _T | None = None

    @abstractmethod
    def get_instance(self) -> _T | None:
        """Simple getter for the instance of the piece.

        Returns
        -------
        _T | None
            instance if it exists, otherwise None
        """

    @abstractmethod
    def initialize(self, parameters: dict[str, Any]) -> _T:
        """Initializes instance from specified PieceData with help of self._constructor.

        Parameters
        ----------
        parameters : dict[str, Any]
            _description_

        Returns
        -------
        _T
            created instance
        """


class OriginalPieceData(PieceData[_T]):
    def get_instance(self) -> _T | None:
        return None

    def initialize(self, parameters) -> _T:
        return self._constructor(**parameters)


class UniversalPieceData(PieceData[_T]):
    def get_instance(self) -> _T | None:
        return self._instance

    def initialize(self, parameters) -> _T:
        self._instance = self._constructor(**parameters)
        return self._instance


piece_data_mapping = {
    Scope.UNIVERSAL: UniversalPieceData,
    Scope.ORIGINAL: OriginalPieceData,
}


def piece_data_factory(type_: Type[_T], scope: Scope, constructor: Constructor) -> PieceData[_T]:
    return piece_data_mapping[scope][_T](type_, constructor)
