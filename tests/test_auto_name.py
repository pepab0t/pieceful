from pieceful import Piece, PieceFactory
from pieceful.registry import registry

from .models import AbstractEngine
from .setup import refresh_after  # noqa: F401


def test_register_class_with_decorator_without_name_spec():
    @Piece()
    class Engine(AbstractEngine):
        pass

    assert registry.get_object("Engine", AbstractEngine) is not None
    assert registry.get_object("Engine", Engine) is not None
    assert "Engine" in registry.registry
    assert len(registry.registry["Engine"]) == 1


def test_register_factory_with_decorator_without_name_spec():
    class Engine(AbstractEngine):
        pass

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    assert registry.get_object("engine_factory", AbstractEngine) is not None
    assert registry.get_object("engine_factory", Engine) is not None
    assert "engine_factory" in registry.registry
    assert len(registry.registry["engine_factory"]) == 1
