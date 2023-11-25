from typing import Annotated, Protocol, runtime_checkable

from pieceful._components import Piece, get_piece


@runtime_checkable
class AbstractLogger(Protocol):
    def log(self, a: int) -> None:
        ...


# @Piece("logger", number=3)
class Logger:
    def __init__(self, number: int) -> None:
        self.number = number

    def log(self, b: str) -> None:
        print(f"logging {self.number}")


@Piece("logger2", strategy=Piece.LAZY)
class Logger2:
    def __init__(self) -> None:
        print(f"{self.__class__.__name__} instantiated")

    def log(self, a: int) -> None:
        print("logging2")


@Piece("controller", a=2)
class Controller:
    def __init__(
        self, a, logger: Annotated[AbstractLogger, "logger2"], number: int = 1
    ):
        self.a = a
        self.logger = logger
        self.number = number

    def print(self):
        print(f"{self.a=}")
        print(f"{self.logger=}")
        print(f"{self.number=}")
        self.logger.log(1)


print("start")
obj: Controller = get_piece("controller", Controller)
obj.print()
