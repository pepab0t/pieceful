import inspect
import typing as t
from collections import defaultdict
from enum import Enum, auto

from ._depends import Depends

# from functools import partial

_pieces: dict[str, dict[type, object]] = defaultdict(dict)

register: dict[str, dict[type, t.Any]] = defaultdict(dict)

annot_type = type(t.Annotated[str, "type"])

T = t.TypeVar("T")


class PieceException(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class HasMetadata(t.Protocol):
    __metadata__: t.Any


def _check_annot_type(param_name, type_hint: t.Any):
    if type(type_hint) is not annot_type:
        raise PieceException(
            f"Parameter `{param_name}` is not annotated for dependency injection."
        )


def _check_annot_definition(type_hint: HasMetadata):
    if len(type_hint.__metadata__) != 1:
        raise PieceException(
            'Expected using one component name in annotations: Annotated[MyClass, "component_name"].'
        )


def _parse_annotation(param_name: str, type_hint: t.Any) -> tuple[str, type]:
    _check_annot_type(param_name, type_hint)
    _check_annot_definition(type_hint)

    component_name = type_hint.__metadata__[0]
    component_type = type_hint.__origin__

    if not isinstance(component_name, str):
        raise PieceException("Expected annotated component name to be str")

    if isinstance(component_type, t.ForwardRef):
        raise PieceException(
            f"This library does not support forward references. Replace {component_type} with explicit reference."
        )

    return component_name, component_type


def _find_existing_component(component_name: str, component_type: t.Type[T]) -> T:
    found = []
    for _cls, _obj in _pieces[component_name].items():
        if issubclass(_cls, component_type):
            found.append((_cls, _obj))

    if len(found) == 0:
        raise PieceException(
            f"Missing component `{component_name}` of type {component_type.__name__}"
        )
    elif len(found) > 1:
        raise PieceException(
            f"Found total {len(found)} components of subclass `{component_type.__name__}` with name `{component_name}`"
        )
    return found[0][1]


def _run_lazy(cls: t.Type[T], name: str, params: dict[str, t.Any]) -> t.Type[T]:
    register[name][cls] = component_dict = {}

    for param_name, param in inspect.signature(cls).parameters.items():
        if param_name in params:
            component_dict[param_name] = params[param_name]
            continue

        if param.default is not param.empty:
            component_dict[param_name] = param.default
            continue

        component_name, component_type = _parse_annotation(param_name, param.annotation)

        component_dict[param_name] = Depends(component_name, component_type)

    return cls


def _run_eager(cls: t.Type[T], name: str, params: dict[str, t.Any]) -> t.Type[T]:
    args: dict[str, t.Any] = {}

    for param_name, param in inspect.signature(cls).parameters.items():
        if param_name in params:
            args[param_name] = params[param_name]
            continue

        if param.default is not param.empty:
            continue

        component_name, component_type = _parse_annotation(param_name, param.annotation)

        if component_name not in _pieces:
            raise PieceException(
                f"Missing component `{component_name}` of type {component_type.__name__}"
            )

        args[param_name] = _find_existing_component(component_name, component_type)

    _pieces[name][cls] = cls(**args)
    return cls


class Piece:
    """Decorate class as a component.\\
    Automatically instantiates the class and inject all other required components dependencies and parameters.
    
    Args:
        name (str): Name of piece
        params: Parameters, that are not @Piece and should be injected on initialization
    """

    class PieceStrategy(Enum):
        LAZY = auto()
        EAGER = auto()

    LAZY: PieceStrategy = PieceStrategy.LAZY
    EAGER: PieceStrategy = PieceStrategy.EAGER

    def __init__(
        self, name: str, strategy: PieceStrategy = PieceStrategy.LAZY, **params
    ):
        self.name = name
        self.strategy = strategy
        self.params = params

    def __call__(self, cls: t.Type[T]) -> t.Type[T]:
        if not isinstance(cls, type):
            raise PieceException(
                f"Wrong usage of @{self.__class__.__name__}. Must be used on class. `{cls.__name__}` is not a class."
            )

        if self.strategy == Piece.LAZY:
            return _run_lazy(cls, self.name, self.params)
        elif self.strategy == Piece.EAGER:
            return _run_eager(cls, self.name, self.params)
        else:
            raise PieceException(f"Invalid strategy: `{self.strategy}`")


def _get_singular_piece(
    piece_name: str, piece_type: t.Type[T], storage: dict[str, dict[type, t.Any]]
) -> t.Optional[T]:
    if piece_name not in storage:
        return None

    found_pieces: list[T] = [
        p_obj
        for p_type, p_obj in storage[piece_name].items()
        if issubclass(p_type, piece_type)
    ]

    if (count_pieces := len(found_pieces)) == 0:
        return None

    if count_pieces > 1:
        raise PieceException(f"Found {count_pieces} matching pieces")

    return found_pieces[0]


def _save_piece(piece_name: str, piece: object):
    named_pieces = _pieces[piece_name]
    if piece.__class__ in named_pieces:
        raise PieceException(
            f"Dependency {piece_name}({piece.__class__.__name__}) already exist"
        )

    named_pieces[piece.__class__] = piece


def create_object(piece_name: str, piece_type: t.Type[T]) -> T:
    if (piece := _get_singular_piece(piece_name, piece_type, _pieces)) is not None:
        return piece

    if piece_name not in register:
        raise PieceException(
            f"Piece `{piece_name}` not registered, use @Piece() to register component"
        )

    cls_params_list: list[tuple[type, dict[str, t.Any]]] = list(
        filter(
            lambda item: issubclass(item[0], piece_type), register[piece_name].items()
        )
    )

    if len(cls_params_list) == 0:
        raise PieceException(
            f"Not found `{piece_name}` of type `{piece_type.__name__}`"
        )

    if len(cls_params_list) > 1:
        raise PieceException(
            f"Found {len(cls_params_list)} components {piece_name}({piece_type.__name__})"
        )

    cls, params = cls_params_list[0]

    for param_name, param_val in params.items():
        if isinstance(param_val, Depends):
            params[param_name] = create_object(param_val.name, param_val.component_type)

    piece = cls(**params)
    _save_piece(piece_name, piece)

    return piece


def get_piece(piece_name: str, piece_type: t.Type[T]) -> T:
    return _find_existing_component(piece_name, piece_type)


def inject_pieces(fn: t.Callable[..., T]) -> t.Callable[..., T]:
    def wrapper(*args, **kwargs):
        # TODO
        raise NotImplementedError("Not implemented yet")

    return wrapper
