from inspect import _empty, signature
from typing import Callable, ParamSpec, Type, TypeVar

from .core import piece_data_factory
from .enums import CreationType as Ct
from .enums import Scope
from .exceptions import PieceIncorrectUseException
from .registry import registry

_T = TypeVar("_T")
P = ParamSpec("P")


def _track_piece(
    piece_type: Type[_T],
    piece_name: str,
    constructor: Callable[..., _T],
    creation_type: Ct = Ct.LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    if (scope, creation_type) == (Scope.ORIGINAL, Ct.EAGER):
        raise PieceIncorrectUseException(
            "ORIGINAL scope with EAGER creation strategy is illegal"
        )

    piece_data = piece_data_factory(piece_type, scope, constructor)

    registry.add(piece_name, piece_data)

    if creation_type == Ct.EAGER:
        registry.get_object(piece_name, piece_type)


def get_piece(piece_name: str, piece_type: Type[_T]) -> _T:
    return registry.get_object(piece_name, piece_type)


def register_piece(
    cls: Type[_T],
    piece_name: str,
    creation_type: Ct = Ct.LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    _track_piece(cls, piece_name, cls, creation_type, scope)


def register_piece_factory(
    fn: Callable[..., _T],
    piece_name: str,
    creation_type: Ct = Ct.LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    piece_type = signature(fn).return_annotation

    if piece_type is _empty or piece_type is None:
        raise PieceIncorrectUseException(
            f"Function `{fn.__name__}` must have return type specified and cannot be None"
        )

    _track_piece(piece_type, piece_name, fn, creation_type, scope)


def Piece(piece_name: str, creation_type: Ct = Ct.LAZY, scope: Scope = Scope.UNIVERSAL):
    def inner(cls: Type[_T]) -> Type[_T]:
        register_piece(cls, piece_name, creation_type, scope)
        return cls

    return inner


def PieceFactory(
    piece_name: str, creation_type: Ct = Ct.LAZY, scope: Scope = Scope.UNIVERSAL
):
    def inner(fn: Callable[P, _T]) -> Callable[P, _T]:
        register_piece_factory(fn, piece_name, creation_type, scope)
        return fn

    return inner
