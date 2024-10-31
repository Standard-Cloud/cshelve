"""
Based on the [official doc](https://docs.python.org/3/library/dbm.html#dbm.open), flags must be one of the following:
- 'r' (default): Open existing database for reading only.
- 'w': Open existing database for reading and writing.
- 'c': Open database for reading and writing, creating it if it doesn't exist.
- 'n': Always create a new, empty database, open for reading and writing.

The module must adapt its behavior based on the flag provided by the user and restrict or process some operations based on the flag.
"""
import functools

from ._database import _Database
from .exceptions import ReadOnlyError


def clear_db(flag: str) -> bool:
    """
    Returns True if the user requests to clear the database.
    """
    return flag == "n"


def can_create(flag: str) -> bool:
    """
    Returns True if a new database can be created.
    """
    return flag in ("c", "n")


def can_write(func) -> bool:
    """
    This decorator restricts write operations based on the flag.
    If the operation is not allowed, it raises a `ReadOnlyError`.
    """

    @functools.wraps(func)
    def can_write(obj: _Database, *args, **kwargs):
        if obj.flag == "r":
            raise ReadOnlyError("Reader can't store")
        return func(obj, *args, **kwargs)

    return can_write
