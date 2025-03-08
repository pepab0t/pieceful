from pieceful import Piece, PieceFactory, provide
from pieceful.registry import registry

from .models import AbstractEngine
from .setup import refresh_after  # noqa: F401


def test_register_class_with_decorator_without_name_spec():
    @Piece()
    class Engine(AbstractEngine):
        pass

    assert registry.get_object("Engine", AbstractEngine) is not None
    assert registry.get_object("Engine", Engine) is not None
    assert registry.get_object("Engine", Engine) is registry.get_object(
        "Engine", AbstractEngine
    )
    assert "Engine" in registry.registry
    assert len(registry.registry["Engine"]) == 1


def test_register_factory_with_decorator_without_name_spec():
    class Engine(AbstractEngine):
        pass

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    assert registry.get_object("Engine", AbstractEngine) is not None
    assert registry.get_object("Engine", Engine) is not None
    assert registry.get_object("Engine", Engine) is registry.get_object(
        "Engine", AbstractEngine
    )
    assert "Engine" in registry.registry
    assert len(registry.registry["Engine"]) == 1


def test_get_class_piece_auto_name():
    @Piece()  # registers piece with name "Engine"
    class Engine(AbstractEngine):
        pass

    engine = provide(Engine)  # retrieves piece with name "Engine"
    assert isinstance(engine, AbstractEngine)
    assert registry.get_object("Engine", AbstractEngine) is engine


def test_get_factory_piece_auto_name():
    class Engine(AbstractEngine):
        pass

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    engine = provide(Engine)
    assert registry.get_object("Engine", Engine) is engine


def test_inject_class_piece_auto_name():
    @Piece()
    class Engine(AbstractEngine):
        pass

    @Piece()
    class Car:
        def __init__(self, engine: Engine):
            self.engine = engine

    assert provide(Car).engine is provide(Engine)
    assert len(registry["Engine"]) == 1
    assert len(registry["Car"]) == 1


def test_inejct_factory_piece_auto_name():
    class Engine(AbstractEngine):
        pass

    class Car:
        def __init__(self, engine: Engine):
            self.engine = engine

    @PieceFactory()
    def car_factory(engine: Engine) -> Car:
        return Car(engine)

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    assert provide(Car).engine is provide(Engine)
    assert len(registry["Engine"]) == 1
    assert len(registry["Car"]) == 1
