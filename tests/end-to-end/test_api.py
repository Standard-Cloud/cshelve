"""
Ensure the standard behavior of the API works as expected in real scenarios.
"""
import os

import pytest

import cshelve

from helpers import write_data, unique_key, del_data


CONFIG_FILES = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
    "tests/configurations/azure-blob/compression.ini",
    "tests/configurations/in-memory/compression.ini",
]

CONFIG_FILES_ITER = [
    "tests/configurations/azure-blob/iter.ini",
    "tests/configurations/in-memory/iter.ini",
]

CONFIG_FILES_LEN = [
    "tests/configurations/azure-blob/len.ini",
    "tests/configurations/in-memory/len.ini",
]

CONFIG_FILES_DEL = [
    "tests/configurations/azure-blob/del.ini",
    "tests/configurations/in-memory/del.ini",
]

CONFIG_FILES_FLAG_N = [
    "tests/configurations/azure-blob/flag-n.ini",
    "tests/configurations/in-memory/flag-n.ini",
]


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_write_then_read(config_file: str):
    """
    Ensure we can read and write data to the DB.
    """
    with cshelve.open(config_file) as db:
        key_pattern = unique_key + "test_write_and_read"
        data_pattern = "test_write_and_read"

        for i in range(10):
            key = f"{key_pattern}{i}"

            # Write data to the DB.
            db[key] = f"{data_pattern}{i}"
            # Data must be present in the DB.
            assert db[key] == f"{data_pattern}{i}"
            # Delete the data from the DB.
            del db[key]

    db.close()


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_read_after_reopening(config_file: str):
    """
    Ensure the data is still present after reopening the DB.
    """
    key_pattern = unique_key + "test_read_after_reopening"
    data_pattern = "test_read_after_reopening"

    def read_data():
        db = cshelve.open(config_file)

        for i in range(10):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    read_data()


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_update_on_operator(config_file: str):
    """
    Ensure operator interface works as expected.
    """
    key_pattern = unique_key + "test_update_on_operator"
    str_data_pattern = "test_update_on_operator"
    list_data_pattern = [1]

    def write_data():
        db = cshelve.open(config_file)

        for i in range(10):
            db[f"{key_pattern}{i}"] = str_data_pattern
            db[f"{key_pattern}{i}-list"] = list_data_pattern

        db.close()

    def update_data():
        db = cshelve.open(config_file)

        for i in range(10):
            db[f"{key_pattern}{i}"] += f"{i}"
            db[f"{key_pattern}{i}-list"] += [i]

        db.close()

    def read_data():
        db = cshelve.open(config_file)

        for i in range(10):
            key = f"{key_pattern}{i}"
            key_list = f"{key_pattern}{i}-list"

            # Operator `+=` on string does not modify the original string.
            assert db[key] == f"{str_data_pattern}{i}"
            # Operator `+=` on list does modify the original list.
            assert db[key_list] == list_data_pattern + [i]

            del db[key]
            del db[key_list]

        db.close()

    write_data()
    update_data()
    read_data()


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_contains(config_file: str):
    """
    Ensure __contains__ works as expected.
    """
    db = cshelve.open(config_file)

    key_pattern = unique_key + "test_contains"
    data_pattern = "test_contains"

    db[key_pattern] = data_pattern

    assert key_pattern in db

    del db[key_pattern]


@pytest.mark.parametrize("config_file", CONFIG_FILES_FLAG_N)
def test_clear_db(config_file):
    """
    Ensure the database is cleared when using the 'n' flag.
    """
    key_pattern = "test_clear_db"
    data_pattern = "test_clear_db"

    def rewrite_db():
        db = cshelve.open(config_file, "n")

        assert len(db) == 0

        for i in range(10):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

        db.close()

    def read_data():
        db = cshelve.open(config_file, "r")

        for i in range(10):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    rewrite_db()
    read_data()
    del_data(config_file, key_pattern)


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES_DEL,
)
def test_del(config_file):
    """
    Ensure we can delete a record from the DB.
    """
    key_pattern = "test_del"
    data_pattern = "test_del"

    def _del_data():
        db = cshelve.open(config_file)

        for i in range(10):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

        assert len(db) == 0
        db.close()

    write_data(config_file, key_pattern, data_pattern)
    _del_data()


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES_LEN,
)
def test_len(config_file):
    """
    Ensure __len__ works as expected.
    """
    db = cshelve.open(config_file)

    key_pattern = "test_len"
    data_pattern = "test_len"

    del_data(config_file)

    for i in range(10):
        db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    assert len(db) == 10

    for i in range(10):
        del db[f"{key_pattern}{i}"]

    assert len(db) == 0


@pytest.mark.parametrize("config_file", CONFIG_FILES_ITER)
def test_iter(config_file):
    """
    Ensure the __iter__ method works as expected.
    """
    res = set()
    db = cshelve.open(config_file)

    key_pattern = "test_iter"
    data_pattern = "test_iter"
    del_data(config_file)

    for i in range(10):
        key = f"{key_pattern}{i}"
        db[key] = f"{data_pattern}{i}"
        res.add(key)

    keys = set(db)
    assert keys == res

    db.close()
    del_data(config_file)
