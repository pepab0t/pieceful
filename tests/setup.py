from typing import Annotated, NamedTuple

from pytest import fixture

from pieceful import AmbiguousPieceException, CreationType, Piece
from pieceful.registry import registry

from .models import EagerEngine, LazyEngine


class NameTypeTuple(NamedTuple):
    name: str
    type: type

    @property
    def annotation(self):
        return Annotated[self.type, self.name]


@fixture
def refresh_after():
    yield
    registry.clear()


@fixture
def decorate_lazy_engine():
    name = "lazy_engine"
    try:
        Piece(name)(LazyEngine)
    except AmbiguousPieceException:
        pass

    return NameTypeTuple(name, LazyEngine)


@fixture
def decorate_eager_engine():
    name = "eager_engine"
    try:
        Piece(name, CreationType.EAGER)(EagerEngine)
    except AmbiguousPieceException:
        pass

    return NameTypeTuple(name, EagerEngine)
