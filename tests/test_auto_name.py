from pieceful import Piece, PieceFactory, need
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
    assert registry.get_object("engine_factory", Engine) is registry.get_object(
        "engine_factory", AbstractEngine
    )
    assert "engine_factory" in registry.registry
    assert len(registry.registry["engine_factory"]) == 1


def test_get_class_piece_auto_name():
    @Piece()  # registers piece with name "Engine"
    class Engine(AbstractEngine):
        pass

    engine = need(Engine)  # retrieves piece with name "Engine"
    assert isinstance(engine, AbstractEngine)


def test_get_factory_piece_auto_name():
    class Engine(AbstractEngine):
        pass

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    engine = need(Engine)
    assert False


def test_inject_class_piece_auto_name():
    assert False


def test_inejct_factory_piece_auto_name():
    assert False
