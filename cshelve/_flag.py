import functools

from .cloud_mutable_mapping import CloudMutableMapping
from .exceptions import DBDoesnotExistsError, ReadonlyError


def clear_db(flag: str) -> bool:
    return flag == "n"


def can_write(func) -> bool:
    @functools.wraps(func)
    def can_write(obj: CloudMutableMapping, *args, **kwargs):
        if obj.flag == "r":
            raise ReadonlyError("Reader can't store")
        return func(obj, *args, **kwargs)

    return can_write


def can_create(func) -> bool:
    @functools.wraps(func)
    def can_write(obj: CloudMutableMapping, *args, **kwargs):
        if obj.flag not in ("c", "n"):
            raise DBDoesnotExistsError("Can't create store")
        return func(obj, *args, **kwargs)

    return can_write
