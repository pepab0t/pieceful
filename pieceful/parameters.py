from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Type

from .exceptions import _NeedCalculation


@dataclass(frozen=True)
class AbstractFrozenDataclass(ABC):
    def __new__(cls, *args, **kwargs):
        if (
            cls is AbstractFrozenDataclass
            or cls.__bases__[0] == AbstractFrozenDataclass
        ):
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)


@dataclass(frozen=True, slots=True)
class Parameter(AbstractFrozenDataclass):
    name: str

    @abstractmethod
    def get(self) -> Any:
        """
        Returns a parameter value or raise _NeedCalculation if parameter is another piece.
        """


@dataclass(frozen=True, slots=True)
class PieceParameter(Parameter):
    piece_name: str
    type: Type[Any]

    def get(self) -> Any:
        raise _NeedCalculation(self.piece_name, self.type)


@dataclass(frozen=True, slots=True)
class DefaultParameter(Parameter):
    value: Any

    def get(self):
        return self.value


@dataclass(frozen=True, slots=True)
class DefaultFactoryParameter(Parameter):
    factory: Callable[[], Any]

    def get(self):
        return self.factory()
