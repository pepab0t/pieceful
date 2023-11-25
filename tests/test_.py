from numpy import isin
from pieceful import Piece, get_piece
from pieceful._components import _register, _pieces
from .setup import clear_pieces, clear_register


def test_lazy_default():
    name: str = "foo"

    global Foo_lazy

    @Piece(name)
    class Foo_lazy:
        pass

    assert Foo_lazy in _register[name]
    assert name not in _pieces


def test_eager_nondefault():
    name = "foo"

    @Piece(name, Piece.EAGER)
    class Foo_eager:
        pass

    assert Foo_eager in _pieces[name]
    assert isinstance(_pieces[name][Foo_eager], Foo_eager)
    assert Foo_eager not in _register[name]


def test_instantiate_piece():
    name = "foo"
    piece = get_piece(name, Foo_lazy)

    assert isinstance(piece, Foo_lazy)
    assert Foo_lazy not in _register[name]
    assert Foo_lazy in _pieces[name]
    assert piece is _pieces[name][Foo_lazy]
