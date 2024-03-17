from inspect import Parameter


class PieceException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class PieceIncorrectUseException(PieceException):
    pass


class PieceNotFound(PieceException):
    pass


class ParameterNotAnnotatedException(PieceException):
    def __init__(self, parameter: Parameter) -> None:
        super().__init__(
            f"Parameter `{parameter.name}` is not annotated with typing.Annotated (actual type: {parameter.annotation})"
        )


class AmbiguousPieceException(PieceException):
    pass
