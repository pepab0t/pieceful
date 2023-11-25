from pytest import fixture
from pieceful._components import _register, _pieces
from collections import defaultdict


@fixture
def clear_register():
    global _register
    _register = defaultdict(dict)


@fixture
def clear_pieces():
    global _pieces
    _pieces = defaultdict(dict)
