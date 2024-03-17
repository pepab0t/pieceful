from collections import defaultdict
from typing import Any, Type

from .exceptions import PieceException, PieceNotFound

Storage = dict[str, dict[Type[Any], "PieceData"]]


class Registry:
    def __init__(self):
        self.registry: Storage = defaultdict(dict)

    def add(self, piece_name: str, piece_data: "PieceData"):
        # TODO piece data might be separated to UniversalPieceData and OriginalPieceData, and factory method should produce PieceData
        for type_ in self.registry[piece_name].keys():
            if issubclass(piece_data.type, type_):
                raise PieceException(
                    f"Piece {piece_data.type} is already registered as a subclass of {type_}."
                )
        self.registry[piece_name][piece_data.type] = piece_data

    def get_object(self, piece_name: str, piece_type: Type[Any]) -> Any:
        if (piece_data := self.registry[piece_name].get(piece_type)) is not None:
            return piece_data.get_instance()

        raise PieceNotFound(f"Piece {piece_type} not found in registry.")


registry: Registry = Registry()

from .core import PieceData  # noqa: E402
