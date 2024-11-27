"""
Ensure that the flag parameter is correctly handled and permissions are correctly set.

The [official documentation](https://docs.python.org/3/library/dbm.html#dbm.open) for the flag parameter is as follows:
- 'r' (default): Open existing database for reading only.
- 'w': Open existing database for reading and writing.
- 'c': Open database for reading and writing, creating it if it doesn't exist.
- 'n': Always create a new, empty database, open for reading and writing.
"""
from unittest.mock import Mock

import pytest

import cshelve
from cshelve._flag import can_create, can_write, clear_db


def test_read_only():
    """
    # The `shelve` module raises an exception when trying to write to a read-only database.
    # The exception is raised by the module used by `shelve` and not `shelve` itself, so it is a `cshelve` exception that we have to catch.
    """
    mock = Mock()
    mock.flag = "r"

    with pytest.raises(cshelve.ReadOnlyError):
        can_write(lambda x: x)(mock)


def test_can_write():
    """
    As explain in the official doc, the 'w', 'c', and 'n' flags should allow writing to the database.
    """
    mock = Mock()

    for flag in ("w", "c", "n"):
        mock.flag = flag
        assert can_write(lambda x: True)(mock) == True


def test_can_create():
    """
    As explain in the official doc, the 'c' and 'n' flags should allow creating a new database.
    """
    for flag in ("c", "n"):
        assert can_create(flag) == True


def test_can_not_create():
    """
    Creating a new database is not allowed with the 'w' and 'r' flags.
    """
    for flag in ("w", "r"):
        assert can_create(flag) == False


def test_do_not_clear_db():
    """
    A database open with the 'n' flag empty it before using it.
    """
    assert clear_db("n") == True


def test_do_not_clear_db():
    """
    Enure that the database is not cleared when the 'n' flags is not used.
    """
    for flag in ("w", "r", "c"):
        assert clear_db(flag) == False
