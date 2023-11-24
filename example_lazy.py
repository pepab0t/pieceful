from typing import Annotated, Protocol, runtime_checkable

from pieceful._components_lazy import Piece, create_object


@runtime_checkable
class AbstractLogger(Protocol):
    def log2(self, a: int, c) -> None:
        ...

    ...


@Piece("logger")
class Logger:
    def log(self, b: str) -> None:
        print("logging")


@Piece("controller", a=2)
class Controller:
    def __init__(self, a, logger: Annotated[AbstractLogger, "logger"], number: int = 1):
        self.a = a
        self.logger = logger
        self.number = number

    def print(self):
        print(f"{self.a=}")
        print(f"{self.logger=}")
        print(f"{self.number=}")
        self.logger.log(1)


obj: Controller = create_object("controller", Controller)
obj.print()
