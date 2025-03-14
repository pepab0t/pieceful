import inspect
from typing import Annotated, Any, Callable, ForwardRef, Iterable

from .exceptions import (
    PieceException,
    PieceIncorrectUseException,
    UnresolvableParameter,
)
from .parameters import (
    DefaultFactoryParameter,
    DefaultParameter,
    Parameter,
    PieceParameter,
)

ANNOTATION_TYPE = type(Annotated[str, "example"])


def _create_piece_parameter(name: str, piece_type: Any, piece_name: str) -> PieceParameter:
    if not piece_name.strip():
        raise PieceException("piece_name must not be blank")
    return PieceParameter(name, piece_name, piece_type)


def _create_default_factory_parameter(name: str, factory: Callable[[], Any]):
    return DefaultFactoryParameter(name, factory)


def _evaluate_forward_ref(fr: ForwardRef, globals_dict: dict[str, Any]) -> Any:
    raise PieceException("ForwardRef is not supported")


def _count_non_default_parameters(fn) -> int:
    try:
        parameters = inspect.signature(fn).parameters.values()
    except ValueError:
        parameters = tuple()

    filtered = filter(
        lambda p: p.default is inspect.Parameter.empty,
        parameters,
    )
    return sum(1 for _ in filtered)


def _parse_annotated_parameter(param_name: str, annotation) -> Parameter:
    metadata = annotation.__metadata__
    if len(metadata) < 1:
        raise PieceIncorrectUseException("piece metadata not specified in Annotated[]")

    piece_type = annotation.__origin__

    if isinstance(piece_type, ForwardRef):
        try:
            gd = metadata[1]
            assert isinstance(gd, dict), "expected globals to be instance of dict"
        except IndexError:
            raise PieceException("globals not provided to evaluate ForwardRef")
        except AssertionError as e:
            raise PieceException(e.args[0])

        piece_type = _evaluate_forward_ref(piece_type, gd)

    name_or_factory = metadata[0]
    if isinstance(name_or_factory, str):
        return _create_piece_parameter(param_name, piece_type, name_or_factory)

    if callable(name_or_factory):
        if _count_non_default_parameters(name_or_factory) != 0:
            raise PieceIncorrectUseException("Factory function must not have non-default parameters.")
        return _create_default_factory_parameter(param_name, name_or_factory)

    raise PieceIncorrectUseException("invalid use")


def parse_parameter(parameter: inspect.Parameter) -> Parameter:
    annotation = parameter.annotation

    if parameter.default is not inspect.Parameter.empty:
        return DefaultParameter(parameter.name, parameter.default)

    if annotation is inspect.Parameter.empty:
        raise UnresolvableParameter(f"Parameter `{parameter.name}` must be annotated")

    return (
        _parse_annotated_parameter(parameter.name, annotation)
        if type(annotation) is ANNOTATION_TYPE
        else _create_piece_parameter(parameter.name, annotation, annotation.__name__)
    )


def get_parameters(fn: Callable[..., Any]) -> Iterable[Parameter]:
    return tuple(map(parse_parameter, inspect.signature(fn).parameters.values()))


__all__ = ["get_parameters"]
