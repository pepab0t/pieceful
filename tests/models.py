from abc import ABC, abstractmethod


class AbstractVehicle(ABC):
    pass


class AbstractBrakes(ABC):
    pass


class AbstractEngine(ABC):
    pass


class EagerEngine(AbstractEngine):
    pass


class LazyEngine(AbstractEngine):
    pass


# class
