import inspect
import typing as t
from collections import defaultdict
from functools import partial

_components: dict[str, dict[type, object]] = defaultdict(dict)

annot_type = type(t.Annotated[str, "type"])

T = t.TypeVar("T")


class PieceException(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def _check_annot_type(param_name, type_hint: t.Any):
    if type(type_hint) is not annot_type:
        raise PieceException(
            f"Parameter `{param_name}` is not annotated for dependency injection."
        )


def _parse_annotation(param_name: str, type_hint: t.Any) -> tuple[str, type]:
    _check_annot_type(param_name, type_hint)
    if len(type_hint.__metadata__) != 1:
        raise PieceException(
            'Expected using one component name in annotations: Annotated[MyClass, "component_name"].'
        )
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
    for _cls, _obj in _components[component_name].items():
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


class Piece:
    """Decorate class as a component.\\
    Automatically instantiates the class and inject all other required components dependencies and parameters.
    
    Args:
        name (str): Name of piece
        params: Parameters, that are not @Piece and should be injected on initialization
    """

    def __init__(self, name: str, **params):
        self.name = name
        self.params = params

    def __call__(self, cls: t.Type[T]) -> t.Type[T]:
        if not isinstance(cls, type):
            raise PieceException(
                f"Wrong usage of @{self.__class__.__name__}. Must be used on class. `{cls.__name__}` is not a class."
            )

        params: dict[str, t.Any] = {}

        for param_name, param in inspect.signature(cls).parameters.items():
            if param_name in self.params:
                params[param_name] = self.params[param_name]
                continue

            component_name, component_type = _parse_annotation(
                param_name, param.annotation
            )

            if component_name not in _components:
                raise PieceException(
                    f"Missing component `{component_name}` of type {component_type.__name__}"
                )

            params[param_name] = _find_existing_component(
                component_name, component_type
            )

        _components[self.name][cls] = cls(**params)

        return cls


def inject_pieces(fn: t.Callable[..., T]) -> t.Callable[..., T]:
    """Inject Annotated component and return partial function with component argument fixed.

    Args:
        fn (t.Callable[..., T]): Function to wrap

    Returns:
        t.Callable[..., T]: partial function with fixed components
    """
    if not callable(fn):
        raise PieceException(
            f"{fn.__name__} is not callable and cannot be decrater with @{inject_pieces.__name__}"
        )

    params = {}
    for param_name, param_type in t.get_type_hints(fn, include_extras=True).items():
        try:
            _check_annot_type(param_name, type_hint=param_type)
        except PieceException:
            continue

        component_name, component_type = _parse_annotation(param_name, param_type)

        params[param_name] = _find_existing_component(component_name, component_type)

    return partial(fn, **params)


def get_piece(component_name: str, component_type: t.Type[T]) -> T:
    """Retrieves a component if possible

    Args:
        component_name (str): Name of component
        component_type (t.Type[T]): Type of component

    Raises:
        ComponentException: If unable to retrieve component based on given parameters

    Returns:
        T: Object, the desired component
    """
    if component_name not in _components:
        raise PieceException(f"Component `{component_name}` does not exist.")

    return _find_existing_component(component_name, component_type)
