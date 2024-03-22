from collections import defaultdict
from typing import Any, Type, TypeVar

from .core import PieceData
from .exceptions import PieceException, PieceNotFound, _NeedCalculation

Storage = dict[str, dict[Type[Any], PieceData[Any]]]

_T = TypeVar("_T")


class Registry:
    def __init__(self):
        self.registry: Storage = defaultdict(dict)

    def add(self, piece_name: str, piece_data: PieceData[Any]):
        if self._get_piece_data(piece_name, piece_data.type):
            raise PieceException(f"Piece {piece_data.type} is already registered as a subclass of {piece_data.type}.")

        self.registry[piece_name][piece_data.type] = piece_data

    def _get_piece_data(self, piece_name: str, piece_type: Type[_T]) -> PieceData[_T] | None:
        for type_, pd in self.registry[piece_name].items():
            if issubclass(type_, piece_type):
                return pd
        return None

    def get_object(self, piece_name: str, piece_type: Type[_T]) -> _T:
        piece_data = self._get_piece_data(piece_name, piece_type)

        if piece_data is None:
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
