from inspect import Parameter
from typing import Any, Type


class PieceException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class PieceIncorrectUseException(PieceException):
    pass


class PieceNotFound(PieceException):
    pass


class UnresolvableParameter(PieceException):
    def __init__(self, description: Parameter | str) -> None:
        super().__init__(
            description
            if isinstance(description, str)
            else f"Parameter `{description.name}` is not annotated with `typing.Annotated` (actual type: {description.annotation})"
        )


class AmbiguousPieceException(PieceException):
    pass


class _NeedCalculation(RuntimeError):
    def __init__(self, piece_name: str, piece_type: Type[Any]) -> None:
        self.piece_name = piece_name
        self.piece_type = piece_type
