from inspect import signature
from math import pi
from typing import Type, TypeVar

from .core import PieceData, _Initializer, piece_data_factory
from .entity import Parameter
from .enums import CreationType as Ct
from .enums import Scope
from .parameter_parser import parse_parameter
from .registry import registry

_T = TypeVar("_T")


def track_piece(
    piece_type: Type[_T],
    piece_name: str,
    creation_type: Ct = Ct.LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    piece_data = piece_data_factory(piece_type, scope, piece_type)

    registry.add(piece_name, piece_data)

    if creation_type == Ct.EAGER:
        piece_data.get_instance()


def get_piece(piece_name: str, piece_type: Type[_T]) -> _T:
    return registry.get_object(piece_name, piece_type)
