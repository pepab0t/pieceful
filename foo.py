from pieceful._swallower import swallow_exception
from pieceful import PieceException
from pieceful._components import _find_existing_component


def foo():
    with swallow_exception(Exception):
        return _find_existing_component("foo", object.__class__, {})

    print("a")


foo()


# if piece_name not in _register:
#     raise PieceException(
#         f"Piece `{piece_name}` not registered, use @Piece() to register component"
#     )

# cls_params_list: list[tuple[type, dict[str, t.Any]]] = list(
#     filter(
#         lambda item: issubclass(item[0], piece_type), _register[piece_name].items()
#     )
# )

# if len(cls_params_list) == 0:
#     raise PieceException(
#         f"Not found `{piece_name}` of type `{piece_type.__name__}`"
#     )

# if len(cls_params_list) > 1:
#     raise PieceException(
#         f"Found {len(cls_params_list)} components {piece_name}({piece_type.__name__})"
#     )
