from unittest.mock import Mock

import pytest
from cshelve._database import _Database
from cshelve.exceptions import CanNotCreateDBError, DBDoesNotExistsError


def test_setitem():
    """
    Ensure that the __getitem__ method returns the value associated with the key from the database.
    """
    provider_db = Mock()
    flag = "c"
    key, value = b"key", b"value"

    db = _Database(provider_db, flag)

    db[key] = value

    provider_db.set.assert_called_once_with(key, value)


def test_getitem():
    """
    Ensure that the __getitem__ method returns the value associated with the key from the database.
    """
    provider_db = Mock()
    flag = "c"
    key, value = b"key", b"value"

    provider_db.get.return_value = value
    db = _Database(provider_db, flag)

    db[key] = value
    assert value == db[key]

    provider_db.get.assert_called_once_with(key)


def test_delitem():
    """
    Ensure that the __delitem__ method deletes the key from the database.
    """
    provider_db = Mock()
    flag = "c"
    key, value = b"key", b"value"

    db = _Database(provider_db, flag)

    db[key] = value
    del db[key]

    provider_db.delete.assert_called_once_with(key)


def test_iter():
    """
    Ensure that the __iter__ method iterates over the keys in the database.
    """
    provider_db = Mock()
    flag = "c"
    key, value = b"key", b"value"

    provider_db.iter.return_value = iter([key])
    db = _Database(provider_db, flag)

    db[key] = value
    assert list(db) == [key]

    provider_db.iter.assert_called_once()


def test_len():
    """
    Ensure that the __len__ method returns the number of elements in the database.
    """
    provider_db = Mock()
    flag = "c"
    key, value = b"key", b"value"

    provider_db.len.return_value = 1
    db = _Database(provider_db, flag)

    db[key] = value
    assert len(db) == 1

    provider_db.len.assert_called_once()


def test_close():
    """
    Ensure that the close method closes the database.
    """
    provider_db = Mock()
    flag = "c"

    db = _Database(provider_db, flag)

    db.close()

    provider_db.close.assert_called_once()


def test_sync():
    """
    Ensure that the sync method syncs the database.
    """
    provider_db = Mock()
    flag = "c"

    db = _Database(provider_db, flag)

    db.sync()

    provider_db.sync.assert_called_once()


def test_doesnt_create_database_if_exists():
    """
    Ensure the database is not created if it already exists.
    """
    provider_db = Mock()
    flag = "c"

    provider_db.exists.return_value = True
    db = _Database(provider_db, flag)
    db._init()

    provider_db.exists.assert_called_once()
    provider_db.create.assert_not_called()


def test_create_database_if_not_exists():
    """
    Ensure the database is created if it doesn't exist.
    """
    provider_db = Mock()
    flags = "c", "n"

    for flag in flags:
        provider_db.exists.reset_mock()
        provider_db.create.reset_mock()
        provider_db.exists.return_value = False

        db = _Database(provider_db, flag)
        db._init()

        provider_db.exists.assert_called_once()
        provider_db.create.assert_called_once()


def test_cant_create_database_if_not_exists_and_not_allowed():
    """
    Ensure exception is raised if the database doesn't exist and the flag doesn't allow it.
    """
    provider_db = Mock()
    flags = "r", "w"

    for flag in flags:
        provider_db.exists.reset_mock()
        provider_db.create.reset_mock()
        provider_db.exists.return_value = False

        db = _Database(provider_db, flag)

        with pytest.raises(DBDoesNotExistsError) as _:
            db._init()


def test_error_database_creation():
    """
    Ensure an internal exception is raised if the database can't be created.
    """
    provider_db = Mock()
    flag = "c"

    provider_db.exists.return_value = False
    provider_db.create.side_effect = Exception
    db = _Database(provider_db, flag)

    with pytest.raises(CanNotCreateDBError) as _:
        db._init()


def test_database_clear_if_asked():
    """
    Ensure the database is cleared if the flag allows it.
    """
    provider_db = Mock()
    flag = "n"

    provider_db.exists.return_value = True
    provider_db.iter.return_value = iter([])
    db = _Database(provider_db, flag)
    db._init()

    provider_db.iter.assert_called_once()


def test_do_not_clear_database():
    """
    Ensure the database is not cleared if the flag doesn't allow it.
    """
    provider_db = Mock()
    flags = "r", "w", "c"

    for flag in flags:
        provider_db.exists.reset_mock()
        provider_db.create.reset_mock()
        provider_db.exists.return_value = True
        provider_db.iter.return_value = iter([])

        db = _Database(provider_db, flag)
        db._init()

        provider_db.iter.assert_not_called()
