# ruff: noqa

from random import randint
import time
from typing import Annotated, Protocol, runtime_checkable

import pytest

from pieceful import (
    AmbiguousPieceException,
    InitStrategy,
    UnresolvableParameter,
    Piece,
    PieceFactory,
    PieceNotFound,
    get_piece,
    Scope,
    PieceIncorrectUseException,
    register_piece,
    PieceException,
)
from pieceful.piece_data import PieceData
from pieceful.registry import registry

from .models import (
    AbstractBrakes,
    AbstractEngine,
    AbstractVehicle,
)
from .setup import (
    NameTypeTuple,
    decorate_eager_engine,
    decorate_lazy_engine,
    refresh_after,
)


def test_create_lazy_default():
    name: str = "lazy_engine_decorated"

    @Piece(name)
    class LazyEngineDecorated(AbstractEngine):
        pass

    assert LazyEngineDecorated in registry.registry[name]
    assert registry.registry[name][LazyEngineDecorated].get_instance() is None


def test_create_eager_nondefault():
    name = "eager_engine_decorated"

    @Piece(name, init_strategy=InitStrategy.EAGER)
    class EagerEngineDecorated(AbstractEngine):
        pass

    assert EagerEngineDecorated in registry[name]
    assert isinstance(registry[name][EagerEngineDecorated].get_instance(), EagerEngineDecorated)


def test_lazy_exists_in_pieces_after_instantiation(decorate_lazy_engine: NameTypeTuple):
    piece_name: str = decorate_lazy_engine.name
    piece_type: type = decorate_lazy_engine.type

    assert isinstance(registry[piece_name][piece_type], PieceData)
    assert registry[piece_name][piece_type].get_instance() is None

    piece = get_piece(piece_name, piece_type)

    piece_in_storage = registry[piece_name][piece_type].get_instance()

    assert piece_in_storage.__class__ is piece_type
    assert piece is piece_in_storage


def test_get_lazy_piece_same_class(decorate_lazy_engine: NameTypeTuple):
    N = decorate_lazy_engine.name
    T = decorate_lazy_engine.type
    assert get_piece(N, T).__class__ is T


def test_get_lazy_piece_subclass(decorate_lazy_engine: NameTypeTuple):
    assert get_piece(decorate_lazy_engine.name, AbstractEngine).__class__ is decorate_lazy_engine.type


def test_get_eager_piece_same_class(decorate_eager_engine: NameTypeTuple):
    piece_name: str = decorate_eager_engine.name
    piece_type: type = decorate_eager_engine.type
    assert isinstance(get_piece(piece_name, piece_type), piece_type)


def test_get_eager_piece_subclass(decorate_eager_engine: NameTypeTuple):
    piece_name: str = decorate_eager_engine.name
    piece_type: type = decorate_eager_engine.type
    assert isinstance(get_piece(piece_name, AbstractEngine), piece_type)


def test_ambiguous_register_error(decorate_lazy_engine: NameTypeTuple):
    with pytest.raises(AmbiguousPieceException):
        Piece(decorate_lazy_engine.name)(decorate_lazy_engine.type)


def test_ambiguous_eager_instantiation_error(decorate_eager_engine: NameTypeTuple):
    with pytest.raises(AmbiguousPieceException):
        Piece(decorate_eager_engine.name, InitStrategy.EAGER)(decorate_eager_engine.type)


def test_eagerly_instantiate_registered_piece_error(
    decorate_lazy_engine: NameTypeTuple,
):
    with pytest.raises(AmbiguousPieceException):
        Piece(decorate_lazy_engine.name, InitStrategy.EAGER)(decorate_lazy_engine.type)


def test_register_eagerly_instantiated_piece_error(
    decorate_eager_engine: NameTypeTuple,
):
    with pytest.raises(AmbiguousPieceException):
        Piece(decorate_eager_engine.name)(decorate_eager_engine.type)


def test_get_piece_with_dependencies_lazy(decorate_lazy_engine: NameTypeTuple):
    piece_name: str = "vehicle"

    @Piece("brakes")
    class Brakes(AbstractBrakes):
        pass

    @Piece(piece_name)
    class Vehicle(AbstractVehicle):
        def __init__(
            self,
            engine: decorate_lazy_engine.annotation,
            brakes: Annotated[Brakes, "brakes"],
        ):
            pass

    vehicle = get_piece(piece_name, Vehicle)

    assert vehicle.__class__ is Vehicle
    assert registry["brakes"][Brakes].get_instance().__class__ is Brakes


def test_get_piece_with_dependencies_eager(decorate_eager_engine: NameTypeTuple):
    piece_name: str = "vehicle"

    @Piece("brakes", InitStrategy.EAGER)
    class Brakes(AbstractBrakes):
        pass

    @Piece(piece_name, InitStrategy.EAGER)
    class Vehicle(AbstractVehicle):
        def __init__(
            self,
            engine: decorate_eager_engine.annotation,
            brakes: Annotated[Brakes, "brakes"],
        ):
            pass

    vehicle = get_piece(piece_name, Vehicle)

    assert vehicle.__class__ is Vehicle
    assert registry["brakes"][Brakes].get_instance().__class__ is Brakes


def test_dependency_inversion_abc(decorate_lazy_engine: NameTypeTuple):
    vehicle_name: str = "vehicle"

    @Piece(vehicle_name)
    class Vehicle(AbstractVehicle):
        def __init__(self, engine: Annotated[AbstractEngine, decorate_lazy_engine.name]) -> None:
            self.engine = engine

    vehicle = get_piece(vehicle_name, AbstractVehicle)

    assert isinstance(vehicle, AbstractVehicle)
    assert isinstance(vehicle.engine, decorate_lazy_engine.type)  # type: ignore


def test_dependency_inversion_protocol():
    vehicle_name: str = "car"
    engine_name: str = "super_engine"

    @Piece(engine_name)
    class SuperEngine:
        def run(self, speed_goal: int) -> bool:
            return True

    @runtime_checkable
    class EngineProtocol(Protocol):
        def run(self, _: int) -> bool: ...

    @Piece(vehicle_name)
    class Car(AbstractVehicle):
        engine: EngineProtocol

        def __init__(self, engine: Annotated[EngineProtocol, engine_name]):
            self.engine = engine

        def get_speed(self, unit: str) -> int: ...

    @runtime_checkable
    class CarProtocol(Protocol):
        def get_speed(self, _: str) -> int: ...

    vehicle = get_piece(vehicle_name, CarProtocol)

    assert isinstance(vehicle, Car)
    assert isinstance(vehicle.engine, SuperEngine)


def test_dependency_inversion_protocol_not_runtime_error():
    vehicle_name: str = "car"
    engine_name: str = "super_engine"

    @Piece(engine_name)
    class SuperEngine:
        def run(self, speed_goal: int) -> bool:
            return True

    class EngineProtocol(Protocol):
        def run(self, _: int) -> bool: ...

    @Piece(vehicle_name)
    class Car(AbstractVehicle):
        def __init__(self, engine: Annotated[EngineProtocol, engine_name]):
            self.engine2 = engine

        def get_speed(self, unit: str) -> int: ...

    with pytest.raises(PieceNotFound):
        get_piece(vehicle_name, Car)


def test_not_dep_injection_error(decorate_lazy_engine: NameTypeTuple):
    with pytest.raises(UnresolvableParameter):

        @Piece("car")
        class Car(AbstractVehicle):
            def __init__(self, engine) -> None:
                pass


def test_piece_not_found_error():
    with pytest.raises(PieceNotFound):
        get_piece("car_not_found", AbstractVehicle)


def test_piece_factory(decorate_lazy_engine: NameTypeTuple):
    class Car(AbstractVehicle):
        def __init__(self, engine: AbstractEngine):
            self.engine = engine

    @PieceFactory()
    def car_from_factory(engine: decorate_lazy_engine.annotation) -> Car:
        return Car(engine)

    car = get_piece("car_from_factory", AbstractVehicle)

    assert isinstance(car, (AbstractVehicle, Car))
    assert isinstance(car.engine, (AbstractEngine, decorate_lazy_engine.type))  # type: ignore


def test_piece_factory_inversion_return_error(decorate_lazy_engine: NameTypeTuple):
    class Car(AbstractVehicle):
        def __init__(self, engine: AbstractEngine):
            self.engine = engine

    @PieceFactory()
    def car_from_factory(engine: decorate_lazy_engine.annotation) -> AbstractVehicle:
        return Car(engine)

    assert get_piece("car_from_factory", AbstractVehicle).__class__ is Car


def test_piece_factory_injected():
    class PowerfulEngine(AbstractEngine):
        pass

    @PieceFactory()
    def powerful_engine() -> AbstractEngine:
        return PowerfulEngine()

    @Piece("car")
    class Car(AbstractVehicle):
        def __init__(self, engine: Annotated[AbstractEngine, "powerful_engine"]) -> None:
            super().__init__()
            self.engine = engine

    c = get_piece("car", AbstractVehicle)

    assert c.__class__ is Car
    assert c.engine.__class__ is PowerfulEngine


def test_original_scope_different_instances():
    @Piece("engine", scope=Scope.ORIGINAL)
    class Engine(AbstractEngine):
        def __init__(self, created: Annotated[int, time.perf_counter_ns]):
            self.created = created

    engines = set((get_piece("engine", Engine) for _ in range(10)))

    assert len(engines) == 10


def test_universal_scope_same_instances():
    @Piece("engine", scope=Scope.UNIVERSAL)
    class Engine(AbstractEngine):
        def __init__(self, created: Annotated[int, time.perf_counter_ns]):
            self.created = created

    engines = set(get_piece("engine", Engine) for _ in range(10))

    assert len(engines) == 1


def test_universal_scope_different_instances_with_factory():
    class Engine(AbstractEngine):
        pass

    @PieceFactory(scope=Scope.UNIVERSAL)
    def engine_factory() -> AbstractEngine:
        return Engine()

    assert get_piece("engine_factory", AbstractEngine) is get_piece("engine_factory", AbstractEngine)


def test_original_scope_different_instances_with_factory():
    class Engine(AbstractEngine):
        pass

    @PieceFactory("engine", scope=Scope.ORIGINAL)
    def engine_factory() -> AbstractEngine:
        return Engine()

    # fmt: off
    assert (get_piece("engine", AbstractEngine) is not\
            get_piece("engine", AbstractEngine))
    # fmt: on


def test_piece_factory_name_none():
    class Engine(AbstractEngine):
        pass

    @PieceFactory()
    def engine_factory() -> Engine:
        return Engine()

    engine = get_piece("engine_factory", AbstractEngine)

    assert engine is registry.get_object("engine_factory", Engine)


def test_piece_factory_name_specified():
    class Engine(AbstractEngine):
        pass

    @PieceFactory(name="engine")
    def engine_factory() -> AbstractEngine:
        return Engine()

    engine = get_piece("engine", AbstractEngine)
    assert engine is engine

    with pytest.raises(PieceNotFound):
        get_piece("engine_factory", AbstractEngine)


def test_eager_piece_with_original_scope_error():
    with pytest.raises(PieceIncorrectUseException):

        @Piece("engine", InitStrategy.EAGER, Scope.ORIGINAL)
        class Engine(AbstractEngine):
            pass


def test_piece_with_default_parameter_instantiation():
    @Piece("engine")
    class Engine(AbstractEngine):
        def __init__(self, power: int = 100):
            self.power = power

    engine = get_piece("engine", Engine)
    assert engine.power == 100


def test_piece_with_default_factory_parameter_instantiation():
    class Engine(AbstractEngine):
        def __init__(self, power: int):
            self.power = power

    random_power = randint(0, 100)

    tracker = []

    @PieceFactory("Engine")
    def engine_factory(
        power: Annotated[int, lambda: random_power],
    ) -> Engine:
        tracker.append(power)
        return Engine(power)

    engine = get_piece("Engine", Engine)
    assert engine.power == random_power
    assert len(tracker) == 1
    assert tracker[0] == random_power


def test_register_supertype_when_subtype_registered():
    class Engine:
        pass

    @Piece("engine")
    class PowerfulEngine(Engine):
        pass

    register_piece(Engine, "engine")

    assert get_piece("engine", Engine).__class__ is Engine
    assert get_piece("engine", PowerfulEngine).__class__ is PowerfulEngine


def test_register_subtype_when_supertype_registered():
    @Piece("engine")
    class Engine:
        pass

    @Piece("engine")
    class PowerfulEngine(Engine):
        pass

    assert get_piece("engine", Engine).__class__ is Engine
    assert get_piece("engine", PowerfulEngine).__class__ is PowerfulEngine


def test_retrive_all_pieces_by_supertype():
    @Piece("engine")
    class PowerfulEngine:
        pass

    @Piece("wheel")
    class Wheel:
        pass

    @Piece("lights")
    class Lights:
        pass

    @Piece("transmition")
    class Transmition:
        pass

    pieces = list(registry.get_all_objects_by_supertype(object))
    assert len(pieces) == 4
    assert all(class_ in {p.__class__ for p in pieces} for class_ in (PowerfulEngine, Wheel, Lights, Transmition))


def test_name_cannot_be_empty_string():
    with pytest.raises(PieceException):

        @Piece("")
        class Engine(AbstractEngine):
            pass


def test_parameter_default_factory_accepts_nonzero_args():
    def get_health_by_name(name: str) -> int:
        return 1

    with pytest.raises(PieceIncorrectUseException) as e:

        @Piece("warrior")
        class Warrior:
            def __init__(self, health: Annotated[int, get_health_by_name]):
                self.health = health

        assert e.getrepr() == "Factory function must not have non-default parameters."
