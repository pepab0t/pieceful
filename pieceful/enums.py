from enum import Enum, auto


class CreationType(Enum):
    LAZY = auto()
    EAGER = auto()


class Scope(Enum):
    ORIGINAL = auto()
    UNIVERSAL = auto()
