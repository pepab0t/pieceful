import random
from typing import Annotated, Protocol, runtime_checkable

from pieceful import Piece, get_piece


@runtime_checkable
class AbstractLogger(Protocol):
    def log(self, obj) -> None: ...


@Piece("logger")
class Logger:
    def __init__(self, number: int = 3) -> None:
        self.number = number

    def log(self, obj) -> None:
        print(f"logging{self.number}: {obj}")

    def __repr__(self) -> str:
        return f"logger{self.number}"


@Piece("logger2")
class Logger2:
    def __init__(self) -> None:
        print(f"{self.__class__.__name__} instantiated")

    def log(self, obj) -> None:
        print(f"logging2: {obj}")

    def __repr__(self) -> str:
        return "logger2"


@Piece("controller")
class Controller:
    def __init__(
        self,
        a: Annotated[int, lambda: random.randint(1, 100)],
        logger: Annotated[AbstractLogger, "logger2"],
        number: int = 1,
    ):
        print(f"{self.__class__.__name__} instantiated")
        self.a = a
        self.logger = logger
        self.number = number

    def print(self):
        print(f"{self.a=}")
        print(f"{self.logger=}")
        print(f"{self.number=}")
        self.logger.log(1)


print("----- start -----")

obj: Controller = get_piece("controller", Controller)
obj.print()
