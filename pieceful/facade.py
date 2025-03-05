import re
from inspect import _empty, signature
from typing import Any, Callable, Iterator, ParamSpec, Type, TypeVar

from .core import piece_data_factory
from .enums import InitStrategy, Scope
from .exceptions import PieceException, PieceIncorrectUseException
from .registry import registry

_T = TypeVar("_T")
P = ParamSpec("P")

LAZY = InitStrategy.LAZY


def _track_piece(
    piece_type: Type[_T],
    piece_name: str,
    constructor: Callable[..., _T],
    creation_type: InitStrategy = LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    if (scope, creation_type) == (Scope.ORIGINAL, InitStrategy.EAGER):
        raise PieceIncorrectUseException(
            "ORIGINAL scope with EAGER creation strategy is illegal"
        )
    if not piece_name:
        raise PieceException("Piece name cannot be empty string.")

    registry.add(piece_name, piece_data_factory(piece_type, scope, constructor))

    if creation_type == InitStrategy.EAGER:
        registry.get_object(piece_name, piece_type)


def need(piece_type: Type[_T], piece_name: str | None = None) -> _T:
    """This function is used to retrieeve a piece from registry."""
    return registry.get_object(piece_name, piece_type)


def get_piece(piece_name: str, piece_type: Type[_T]) -> _T:
    """This function returns registered piece by name and type.

    Parameters
    ----------
    piece_name : str
        name of the piece
    piece_type : Type[_T]

    Returns
    -------
    T
        desired instance
    """
    return registry.get_object(piece_name, piece_type)


def get_pieces_by_supertype(super_type: Type[_T]) -> Iterator[_T]:
    """This function returns all registered pieces that are subtypes of given type.

    Parameters
    ----------
    super_type : Type[T]

    Returns
    -------
    T
        desired instance
    """
    return registry.get_all_objects_by_supertype(super_type)


def get_pieces_by_name(name_pattern: str | re.Pattern[str]) -> Iterator[Any]:
    """This function returns all registered pieces that match given name pattern.

    Parameters
    ----------
    name_pattern : str | re.Pattern[str]
        regular expression pattern to match name

    Returns
    -------
    Iterator[Any]
        iterator of instances matching name
    """
    return registry.get_all_objects_by_name_matching(re.compile(name_pattern))


def register_piece(
    cls: Type[_T],
    piece_name: str | None = None,
    creation_type: InitStrategy = InitStrategy.LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    """This function registers class as a dependency.
    __init__ method's parameters must be annotated references to registered pieces.

    Parameters
    ----------
    name : str
        unique name of piece
    creation_type : InitStrategy, optional
        defines instantiation strategy, by default `InitStrategy.LAZY`\\
        `LAZY` - object is created on first access\\
        `EAGER` - object is created immediately
    scope : Scope, optional
        scope of the piece, by default Scope.UNIVERSAL\\
        `ORIGINAL` - piece is created only once and is shared among all usages\\
        `UNIVERSAL` - piece is created for each usage separately
    """
    _track_piece(
        cls,
        piece_name if piece_name is not None else cls.__name__,
        cls,
        creation_type,
        scope,
    )


def register_piece_factory(
    factory: Callable[..., _T],
    name: str | None = None,
    creation_type: InitStrategy = LAZY,
    scope: Scope = Scope.UNIVERSAL,
) -> None:
    """This function registers a factory function to create dependency.\\
    Factory function's parameters must be annotated references to registered pieces.\\
    Factory function must declare return type.\\
    **Tip**: Use `PieceFactory` decorator instead.

    Parameters
    ----------
    factory : Callable[..., T]
        factory function to be registered
    name : str | None, optional
        name of piece, if None piece piece has same name as factory function, by default None
    creation_type : InitStrategy, optional
        defines instantiation strategy, by default `InitStrategy.LAZY`\\
        `LAZY` - object is created on first access\\
        `EAGER` - object is created immediately
    scope : Scope, optional
        scope of the piece, by default Scope.UNIVERSAL\\
        `ORIGINAL` - piece is created only once and is shared among all usages\\
        `UNIVERSAL` - piece is created for each usage separately
    """
    piece_type = signature(factory).return_annotation

    if piece_type is _empty or piece_type is None:
        raise PieceIncorrectUseException(
            f"Function `{factory.__name__}` must have return type specified and cannot be None"
        )

    _track_piece(
        piece_type,
        name if name is not None else factory.__name__,
        factory,
        creation_type,
        scope,
    )


def Piece(
    name: str | None = None,
    init_strategy: InitStrategy = LAZY,
    scope: Scope = Scope.UNIVERSAL,
):
    """This decorator registers class as a dependency.
    __init__ method's parameters must be annotated references to registered pieces.

    Parameters
    ----------
    name : str
        unique name of piece
    creation_type : InitStrategy, optional
        defines instantiation strategy, by default `InitStrategy.LAZY`\\
        `LAZY` - object is created on first access\\
        `EAGER` - object is created immediately
    scope : Scope, optional
        scope of the piece, by default Scope.UNIVERSAL\\
        `ORIGINAL` - piece is created only once and is shared among all usages\\
        `UNIVERSAL` - piece is created for each usage separately
    """

    def inner(cls: Type[_T]) -> Type[_T]:
        register_piece(cls, name, init_strategy, scope)
        return cls

    return inner


def PieceFactory(
    name: str | None = None,
    init_strategy: InitStrategy = InitStrategy.LAZY,
    scope: Scope = Scope.UNIVERSAL,
):
    """This decorator registers a factory function to create dependency.\\
    Factory function's parameters must be annotated references to registered pieces.\\
    Factory function must declare return type.

    Parameters
    ----------
    name : str | None, optional
        name of piece, if None piece piece has same name as factory function, by default None
    creation_type : InitStrategy, optional
        defines instantiation strategy, by default `InitStrategy.LAZY`\\
        `LAZY` - object is created on first access\\
        `EAGER` - object is created immediately
    scope : Scope, optional
        scope of the piece, by default Scope.UNIVERSAL\\
        `ORIGINAL` - piece is created only once and is shared among all usages\\
        `UNIVERSAL` - piece is created for each usage separately
    """

    def inner(factory: Callable[P, _T]) -> Callable[P, _T]:
        register_piece_factory(factory, name, init_strategy, scope)
        return factory

    return inner
