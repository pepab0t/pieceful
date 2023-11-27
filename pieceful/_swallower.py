from contextlib import contextmanager
import typing as t

T_exc = t.TypeVar("T_exc", bound=Exception)


@contextmanager
def swallow_exception(exc_type: t.Type[T_exc]):
    try:
        yield
    except exc_type as e:
        print(e)
