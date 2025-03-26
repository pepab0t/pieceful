# Pieceful

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/pieceful/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)

## Description

Pieceful is a Python package that provides a collection of utility functions for working with dependency injection.

## Installation

Install with

```bash
pip install pieceful
```

## API reference

-   Piece
-   PieceFactory
-   get_piece
-   provide
-   get_piece_by_name
-   get_piece_by_supertype
-   register_piece
-   register_piece_factory
-   PieceException
-   PieceNotFound
-   ParameterNotAnnotatedException
-   AmbiguousPieceException
-   PieceIncorrectUseException
-   InitStrategy
-   Scope

## Register piece

This library provides 4 ways to register a dependency. Decorator versions are just wrappers and use `register_piece` or `register_piece_factory` internally.

```python
@Piece() # piece name autodetected by class name: "Car"
class Car:
    pass
```

```python
class Car:
    pass

@PieceFactory() # piece name autodetected by factory function name: "car"
def car() -> Car:
    return Car()
```

```python
class Car:
    pass

register_piece(Car) # piece name autodetected
```

```python
class Car:
    pass

def car() -> Car:
    return Car()

register_piece_factory(car) # piece name autodetected
```

## Piece that depends on something else

Class or factory function that define a depencency (piece) can require arguments, when every satisfies one of following conditions. Argument satisfies when:

-   has a default value `(arg=1)` (if specified takes priority over other possibilities). In that case default value is used within dependency creation.

```python
@Piece()
class Car:
    def __init__(self, wheels=4): ...
```

-   is typed with `typing.Annotated[t, name]` when `name` is the `str` specifying other registered dependency name.

```python
@Piece()
class Car:
    def __init__(
        self,
        engine: Annotated[Engine, "engine"], # target other piece
    ): ...
```

-   is typed with `typing.Annotated[t, factory]` when factory is a function with zero args that provide value for argument.

```python
@Piece()
class Car:
    def __init__(
        self,
        fuel_percent: Annotated[int, lambda: random.randint(0, 100)]
    ): ...
```

-   is typed `(arg: OtherPiece)` when `OtherPiece` is type of other registered dependency with name `"OtherPiece"` (autodetected).

```python
@Piece()
class Car:
    def __init__(
        self,
        engine: Engine, # other piece with name "Engine"
    ): ...
```

## Retrieve piece

Package provides several options to retrieve a registered piece.

```python
provide(Car, "my_car")
provide(Car) # get piece with name "Car" (autodetected)
get_piece("my_car", Car) # deprecated
get_pieces_by_supertype(Car) # get all pieces with Car supertype
get_pieces_by_name("^my_.*") # get all pieces with name matching pattern
```

## Tutorial

In this tutorial we explain basic usage of `pieceful` library on simple example.\
Let's describe composition problem on abstraction level.
When we have a `car` instance that has it's `driver` and `engine`.\
Car is an abstract vehicle concept that also depends on abstact driver and abstract engine.
First perform necessary import:

```python
from typing import Annotated
from pieceful import Piece, PieceFactor, get_piece
```

> **Note:** `pieceful`'s dependency injection specification relies on `typing.Annotated` annotation.

Abstraction can look like this:

```python
from abc import ABC, abstractmethod


class AbstractEngine(ABC):
    @abstractmethod
    def run(self) -> None:
        ...


class AbstractDriver(ABC):
    @abstractmethod
    def drive(self) -> None:
        ...


class AbstractVehicle(ABC):
    engine: AbstractEngine
    driver: AbstractDriver

    @abstractmethod
    def start(self) -> None:
        ...
```

Then we can define implementations and decorate them as dependencies with the `@Piece` of `@PieceFactory` decorator.\
This way pieces are added to the library registry.

```python
@Piece("engine")
class PowerfulEngine(AbstractEngine):
    def run(self):
        print("Powerful engine is running and ready to go.")

class ResponsibleDriver(AbstractDriver):
    def drive(self):
        print("Responsible driver starts driving.")

@PieceFactory("reponsible_driver")
def driver_factory() -> ResponsibleDriver:
    return ResponsibleDriver()

@Piece("car")
class Car(AbstractVehicle):
    def __init__(
        self,
        engine: Annotated[AbstractEngine, "engine"],
        driver: Annotated[AbstractDriver, "responsible_driver"]
    ):
        self.engine = engine
        self.driver = driver

    def start(self) -> None:
        self.engine.run()
        self.driver.drive()
```

> See that we are defining `name` of dependency in `@Piece` or `@PieceFactory` decorator.

> When using `@PieceFactory` name is optional, when not specified, decorated function's name is used.

> When using `@PieceFactory` factory function must declare a return type, otherwise exception is thrown.

Now components can be injected to other components (like `AbstractEngine` -> `Car`) by using `typing.Annotated` or they can be directly obtained with `get_piece` function.\
Example of `get_piece` function usage:

```python
def main():
    car = provide(AbstractVehicle, "car")
```

> Notice that `Car` depends on `engine` and a `driver`, that are injected in a constructor.

> To tell the framework what dependencies we want to inject to our `Car`, we use `typing.Annotated`, where first argument has a meaning of `type` of dependency and second represents `name` of our `Piece` (`Annotated[piece_type: Type[Any], piece_name: str]`). This way, framework will recognize what to inject.

> Notice that `main` function does not need to know anything about specific car implementation. Function depends only on abstract concept and _dependecy inversion_ principle is followed this way. Also see that, function `get_piece` can retrieve required dependency based on abstract type and dependency name. This framework also helps you following _dependency inversion_ principle.

Now let's assume, that we want to use other `driver` dependency in our `Car` definition. Another driver type must be registered as dependency. When done, all it takes is to change dependency name in `Car`'s constructor (`"responsible_driver"` -> `"impetuous_driver"`):

```python

@Piece("impetuous_driver")
class ImpetuousDriver(AbstractDriver):
    def drive(self):
        print("Impetuous driver starts driving, be careful!")

@Piece("car")
class Car(AbstractVehicle):
    def __init__(
        self,
        engine: t.Annotated[AbstractEngine, "engine"],
        driver: t.Annotated[AbstractDriver, "impetuous_driver"],
        wheels: int = 4,
    ) -> None:
        ...
```

> To repeat again, `Car` depends on abstract concepts, so both `ResponsibleDriver` and `ImpetuousDriver` match type `AbstractDriver` and can be injected as a `driver` parameter to `Car` constructor.
> Dependencies are resolved by their name and type (or super-type of any level).

## Other ways to register pieces

Registration is also possible through functions `register_piece` and `register_piece_factory`.

```python
from pieceful import register_piece, register_piece_factory

class OtherCar(AbstractVehicle):
    ... # omitted code

# first option
register_piece(OtherCar, "other_car")

# other option
def other_car_factory() -> AbstractVehicle:
    return OtherCar()

register_piece_factory(other_car_factory, "other_car")
```

## Other ways to obtain pieces

Besides `typing.Annotated` and `get_piece` function, registered dependencies could be retrieved in groups by specifiing dependency name pattern (regex pattern) or dependency supertype.\
For example:

```python
from pieceful import get_pieces_by_name

get_pieces_by_name(".*driver$")
```

returns iterator of all registered dependencies that's name end with `"driver"` and calling function `get_pieces_by_supertype`:

```python
from pieceful import get_pieces_by_supertype

get_pieces_by_supertype(AbstractDriver)
```

returns all registered pieces that's supertype is `AbstractDriver`.

> **Tip:** call `get_pieces_by_supertype(object)` to get all registered pieces.

## Eager vs. Lazy initialization

Library allows to choose from two strategies of object initialization. Strategy can be specified when decorating class with `@Piece` or `@PieceFactory` with help of enum type: `InitStrategy`.

```python
from pieceful import Piece, InitStrategy

@Piece("foo", strategy=InitStrategy.EAGER)
class Foo:
    pass

@Piece("bar", strategy=InitStrategy.LAZY)
class Bar:
    pass
```

### `InitStrategy.LAZY`

Object is initialized just when its needed for the first time. That means object is obtained by any get function (e. g. `get_piece`) or is injected to the component that is being initialized. This approach is default.

### `InitStrategy.EAGER`

Object is initialized at the same time interpreter reaches the registration. This approach is not recommended, because it's more tricky to understand when object is created inside library and depends on the order of imports.

> Imagine importing some module in other python file, code of whole module is executed and this way also `@Piece` object is created in library storage. This can lead to possible complications.

When registered many dependencies with **EAGER** strategies, all initializations may have impact on performance, because dependencies are created usually at application startup (usually, because for example with `importlib` behavior can be different).

## Scope

Framework provides `Scope` enum, that is used when registering dependencies.

```python
from pieceful import Piece, Scope

@Piece("baz", scope=Scope.UNIVERSAL)
class Baz:
    pass

@Piece("qux", scope=Scope.ORIGINAL)
class Qux:
    pass
```

### `Scope.UNIVERSAL`

Takes care of creating one instance of piece and injection references to the same object where requested.

```python
assert get_piece("baz", Baz) is get_piece("baz", Baz)
```

### `Scope.ORIGINAL`

Creates new instance for every place dependency is requested.

```python
assert get_piece("qux", Qux) is not get_piece("qux", Qux)
```
