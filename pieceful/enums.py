from enum import Enum, auto


class InitStrategy(Enum):
    LAZY = auto()
    EAGER = auto()


class Scope(Enum):
    ORIGINAL = auto()
    UNIVERSAL = auto()


class NotResolved: ...
