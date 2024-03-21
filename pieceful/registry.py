from collections import defaultdict
from typing import Any, Type

from .core import PieceData
from .exceptions import PieceException, PieceNotFound, _NeedCalculation

Storage = dict[str, dict[Type[Any], PieceData]]


class Registry:
    def __init__(self):
        self.registry: Storage = defaultdict(dict)

    def add(self, piece_name: str, piece_data: "PieceData"):
        for type_ in self.registry[piece_name].keys():
            if issubclass(piece_data.type, type_):
                raise PieceException(f"Piece {piece_data.type} is already registered as a subclass of {type_}.")
        self.registry[piece_name][piece_data.type] = piece_data

    def get_object(self, piece_name: str, piece_type: Type[Any]) -> Any:
        piece_data: PieceData
        for type_, pd in self.registry[piece_name].items():
            if issubclass(type_, piece_type):
                piece_data = pd
                break
        else:
            raise PieceNotFound(f"Piece {piece_type} not found in registry.")

        if (instance := piece_data.get_instance()) is not None:
            return instance

        params: dict[str, Any] = {}
        for param in piece_data.parameters:
            try:
                param_val = param.get()
            except _NeedCalculation as e:
                param_val = self.get_object(e.piece_name, e.piece_type)
            params[param.name] = param_val

        return piece_data.initialize(params)


registry: Registry = Registry()
