from .models import AbstractEngine
from .setup import refresh_after
from pieceful import Piece


def test_register_class_with_decorator_without_name_spec():
    @Piece()
    class Engine(AbstractEngine):
        pass

    assert Engine in refresh_after()
    assert refresh_after()[Engine].name == "Engine"
