from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Type

from .exceptions import PieceNotFound
from .parameter_parser import get_parameters
from .registry import registry


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
    def get(self) -> Any: ...


@dataclass(frozen=True, slots=True)
class PieceParameter(Parameter):
    piece_name: str
    type: Type[Any]

    def get(self) -> Any:
        # recursion here
        try:
            return registry.get_object(self.piece_name, self.type)
        except PieceNotFound:
            parameters = {p.name: p.get() for p in get_parameters(self.type)}
            piece = self.type(**parameters)
            registry.add(self.piece_name, piece)
            return piece


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
