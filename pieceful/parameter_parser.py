import inspect
from typing import Annotated, Any, Callable, ForwardRef, Iterable, Type

from .entity import DefaultFactoryParameter, DefaultParameter, Parameter, PieceParameter
from .exceptions import (
    ParameterNotAnnotatedException,
    PieceException,
    PieceIncorrectUseException,
)

ANNOTATION_TYPE = type(Annotated[str, "example"])


def create_piece_parameter(name: str, piece_name: str, piece_type: Any) -> PieceParameter:
    if not piece_name.strip():
        raise PieceException("piece_name must not be blank")
    if isinstance(piece_type, ForwardRef):
        # piece_type._evaluate(globals())
        raise PieceException("ForwardRef not supported")
    return PieceParameter(name, piece_name, piece_type)


def create_default_factory_parameter(name: str, factory: Callable[[], Any]):
    return DefaultFactoryParameter(name, factory)


def count_non_default_parameters(fn) -> int:
    filtered = filter(
        lambda p: p.default is inspect.Parameter.empty,
        inspect.signature(fn).parameters.values(),
    )
    return sum(1 for _ in filtered)


def parse_parameter(parameter: inspect.Parameter) -> Parameter:
    annotation = parameter.annotation

    if parameter.default is not inspect.Parameter.empty:
        return DefaultParameter(parameter.name, parameter.default)

    if type(annotation) is not ANNOTATION_TYPE:
        raise ParameterNotAnnotatedException(parameter)

    metadata = annotation.__metadata__
    if len(metadata) < 1:
        raise PieceIncorrectUseException("piece metadata not specified in Annotated[]")

    piece_type = annotation.__origin__

    metainfo = metadata[0]
    if isinstance(metainfo, str):
        return create_piece_parameter(parameter.name, metainfo, piece_type)

    if callable(metainfo) and count_non_default_parameters(metainfo) == 0:
        return create_default_factory_parameter(parameter.name, metainfo)

    raise PieceIncorrectUseException("invalid use")


def get_parameters(fn) -> Iterable[Parameter]:
    return map(parse_parameter, inspect.signature(fn).parameters.values())
