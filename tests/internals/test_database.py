from unittest.mock import Mock

import pytest
from cshelve._database import _Database
from cshelve._in_memory import InMemory
from cshelve.exceptions import CanNotCreateDBError, DBDoesNotExistsError, ReadOnlyError


@pytest.fixture
def database() -> _Database:
    flag = "c"
    provider_db = InMemory()
    db = _Database(provider_db, flag)
    db._init()
    return db


def test_setitem(database):
    """
    Ensure that the __setitem__ method returns the value associated with the key from the database.
    """
    key, value = b"key", b"value"
    database[key] = value

    assert value == database.db.get(key)


def test_getitem(database):
    """
    Ensure that the __getitem__ method returns the value associated with the key from the database.
    """
    key, value = b"key", b"value"
    database.db.set(key, value)

    assert value == database[key]


def test_delitem(database):
    """
    Ensure that the __delitem__ method deletes the key from the database.
    """
    key, value = b"key", b"value"
    database.db.set(key, value)

    del database[key]

    assert False == database.db.contains(key)


def test_iter(database):
    """
    Ensure that the __iter__ method iterates over the keys in the database.
    """
    key, value = b"key", b"value"
    key2, value2 = b"key2", b"value2"

    database.db.set(key, value)
    database.db.set(key2, value2)

    assert list(database) == [key, key2]


def test_len(database):
    """
    Ensure that the __len__ method returns the number of elements in the database.
    """
    database.db.set("key", "value")
    database.db.set("key2", "value2")

    assert len(database) == 2


def test_close(database):
    """
    Ensure that the close method closes the database.
    """
    database.close()

    assert database.db.db is None


def test_sync(database):
    """
    Ensure that the sync method syncs the database.
    """
    assert database.db._synced == False

    database.sync()

    assert database.db._synced == True


def test_doesnt_create_database_if_exists():
    """
    Ensure the database is not created if it already exists.
    """
    flag = "c"
    provider_db = InMemory()
    provider_db.configure({"exists": "True"})

    assert provider_db._created == False

    db = _Database(provider_db, flag)
    db._init()

    assert provider_db._created == False


def test_create_database_if_not_exists():
    """
    Ensure the database is created if it doesn't exist.
    """
    flag = "c"
    provider_db = InMemory()

    assert provider_db._created == False
    assert provider_db._exists == False

    db = _Database(provider_db, flag)
    db._init()

    assert provider_db._created == True


def test_cant_create_database_if_not_exists_and_not_allowed():
    """
    Ensure exception is raised if the database doesn't exist and the flag doesn't allow it.
    """
    flags = "r", "w"

    for flag in flags:
        provider_db = InMemory()

        assert provider_db._created == False
        assert provider_db._exists == False

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
    flag = "n"
    provider_db = InMemory()
    provider_db.configure({"exists": "True"})

    provider_db.set("key", "value")
    provider_db.set("key2", "value2")

    assert provider_db.len() == 2
    db = _Database(provider_db, flag)
    db._init()
    assert provider_db.len() == 0


def test_do_not_clear_database():
    """
    Ensure the database is not cleared if the flag doesn't allow it.
    """
    flags = "r", "w", "c"

    for flag in flags:
        provider_db = InMemory()
        provider_db.configure({"exists": "True"})

        provider_db.set("key", "value")
        provider_db.set("key2", "value2")

        assert provider_db.len() == 2
        db = _Database(provider_db, flag)
        db._init()
        assert provider_db.len() == 2


def test_read_only():
    """
    Ensure the database is not cleared if the flag doesn't allow it.
    """
    flag = "r"
    key, value = b"key", b"value"
    new_key, new_value = b"key-new", b"value-new"

    provider_db = InMemory()
    provider_db.configure({"exists": "True"})

    provider_db.set(key, value)

    db = _Database(provider_db, flag)
    db._init()

    with pytest.raises(ReadOnlyError) as _:
        db[new_key] = new_value

    with pytest.raises(ReadOnlyError) as _:
        del db[key]

    assert db[key] == value
