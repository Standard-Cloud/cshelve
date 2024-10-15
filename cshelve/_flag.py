import functools

from .cloud_mutable_mapping import CloudMutableMapping
from .exceptions import DBDoesNotExistsError, ReadOnlyError


def clear_db(flag: str) -> bool:
    return flag == "n"


def can_create(flag: str) -> bool:
    return flag in ("c", "n")


def can_write(func) -> bool:
    @functools.wraps(func)
    def can_write(obj: CloudMutableMapping, *args, **kwargs):
        if obj.flag == "r":
            raise ReadOnlyError("Reader can't store")
        return func(obj, *args, **kwargs)

    return can_write
