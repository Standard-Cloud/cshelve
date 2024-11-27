from unittest.mock import Mock
import pytest

from cshelve._factory import factory
from cshelve import KeyNotFoundError


def test_get_and_set():
    """
    Ensure we can set then retrieve a value from the database.
    """
    key, value = b"key", b"value"

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    provider.set(key, value)
    assert value == provider.get(key)


def test_do_not_persist():
    """
    Ensure the DB is by default purged between open operation.
    """
    key, value = b"key", b"value"

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    provider.set(key, value)
    # Ensure the element is persisted.
    assert provider.len() == 1

    # Re open the database to ensure the element is gone.
    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    assert provider.len() == 0


def test_get_and_set_persist():
    """
    Ensure we can set then retrieve a value from the database.
    """
    config = {"persist-key": "only-in-memory"}
    key, value = b"key", b"value"

    provider = factory(Mock(), "in-memory")
    provider.configure_default(config)

    provider.set(key, value)
    # Ensure the element is persisted.
    assert provider.len() == 1

    # Re open the database to ensure the element is still there.
    provider = factory(Mock(), "in-memory")
    provider.configure_default(config)

    assert provider.len() == 1


def test_get_key_error():
    """
    Ensure a key error is raised when the key is not found.
    """
    key = b"does-not-exist"

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    with pytest.raises(KeyNotFoundError):
        provider.get(key)


def test_close():
    """
    Ensure the close method can be called.
    """
    provider = factory(Mock(), "in-memory")
    provider.configure_default({})
    provider.close()


def test_delete():
    """
    Ensure the delete method can be called.
    """
    key, value = b"key", b"value"

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    provider.set(key, value)
    assert provider.contains(key)
    provider.delete(key)
    assert not provider.contains(key)


def test_iter():
    """
    Ensure the list of key is correctly returned.
    """
    keys = [b"key1", b"key2"]

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    for k in keys:
        provider.set(k, b"value")

    assert list(provider.iter()) == keys


def test_contains():
    """
    Ensure contains correctly works.
    """
    key = b"key"

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    assert not provider.contains(key)
    provider.set(key, b"value")
    assert provider.contains(key)


def test_len():
    """
    Ensure the calculation of the number of keys is correctly returned.
    """
    list_blob_names = [b"key1", b"key2"]

    provider = factory(Mock(), "in-memory")
    provider.configure_default({})

    for k in list_blob_names:
        provider.set(k, b"value")

    assert 2 == provider.len()


def test_exists():
    """
    Ensure the exists method can be called.
    """
    provider = factory(Mock(), "in-memory")
    provider.configure_default({})
    provider.exists()


def test_create():
    """
    Ensure the create method can be called.
    """
    provider = factory(Mock(), "in-memory")
    provider.configure_default({})
    provider.create()
