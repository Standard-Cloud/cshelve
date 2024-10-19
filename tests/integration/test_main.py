import pytest

import cshelve

from helpers import write_data, del_data


def test_write_and_read():
    """
    Ensure we can read and write data to the DB.
    """
    db = cshelve.open("tests/configurations/azure-integration/standard.ini")

    key_pattern = "test_write_and_read"
    data_pattern = "test_write_and_read"

    for i in range(100):
        key = f"{key_pattern}{i}"

        # Write data to the DB.
        db[key] = f"{data_pattern}{i}"
        # Data must be present in the DB.
        assert db[key] == f"{data_pattern}{i}"
        # Delete the data from the DB.
        del db[key]

    db.close()


def test_write_and_read():
    """
    Ensure we can read and write data to the DB.
    """
    with cshelve.open("tests/configurations/azure-integration/standard.ini") as db:

        key_pattern = "test_write_and_read"
        data_pattern = "test_write_and_read"

        for i in range(100):
            key = f"{key_pattern}{i}"

            # Write data to the DB.
            db[key] = f"{data_pattern}{i}"
            # Data must be present in the DB.
            assert db[key] == f"{data_pattern}{i}"
            # Delete the data from the DB.
            del db[key]

    db.close()


def test_del():
    """
    Ensure we can delete data from the DB.
    """
    config_file = "tests/configurations/azure-integration/del.ini"
    key_pattern = "test_del"
    data_pattern = "test_del"

    def _del_data():
        db = cshelve.open(config_file)

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[f"{key_pattern}{i}"]

        assert len(db) == 0
        db.close()

    write_data(config_file, key_pattern, data_pattern)
    _del_data()


def test_read_after_reopening():
    """
    Ensure the data is still present after reopening the DB.
    """
    config_file_passwordless = "tests/configurations/azure-integration/standard.ini"
    config_file_connection_string = (
        "tests/configurations/azure-integration/connection-string.ini"
    )
    key_pattern = "test_read_after_reopening"
    data_pattern = "test_read_after_reopening"

    def read_data(config_file):
        db = cshelve.open(config_file)

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

        db.close()

    for config_file in [config_file_passwordless, config_file_connection_string]:
        write_data(config_file, key_pattern, data_pattern)
        read_data(config_file)


def test_update_on_operator():
    """
    Ensure operator interface works as expected.
    """
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = "test_update_on_operator"
    str_data_pattern = "test_update_on_operator"
    list_data_pattern = [1]

    def write_data():
        db = cshelve.open(config_file)

        for i in range(100):
            db[f"{key_pattern}{i}"] = str_data_pattern
            db[f"{key_pattern}{i}-list"] = list_data_pattern

        db.close()

    def update_data():
        db = cshelve.open(config_file)

        for i in range(100):
            db[f"{key_pattern}{i}"] += f"{i}"
            db[f"{key_pattern}{i}-list"] += [i]

        db.close()

    def read_data():
        db = cshelve.open(config_file)

        for i in range(100):
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


def test_contains():
    """
    Ensure __contains__ works as expected.
    """
    db = cshelve.open("tests/configurations/azure-integration/standard.ini")

    key_pattern = "test_contains"
    data_pattern = "test_contains"

    db[key_pattern] = data_pattern

    assert key_pattern in db

    del db[key_pattern]


def test_len():
    """
    Ensure __len__ works as expected.
    """
    config = "tests/configurations/azure-integration/len.ini"
    db = cshelve.open(config)

    key_pattern = "test_len"
    data_pattern = "test_len"

    del_data(config)

    for i in range(100):
        db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    assert len(db) == 100

    for i in range(100):
        del db[f"{key_pattern}{i}"]

    assert len(db) == 0


def test_iter():
    config = "tests/configurations/azure-integration/iter.ini"
    res = set()
    db = cshelve.open(config)

    key_pattern = "test_iter"
    data_pattern = "test_iter"
    del_data(config)

    for i in range(100):
        key = f"{key_pattern}{i}"
        db[key] = f"{data_pattern}{i}"
        res.add(key)

    keys = set(db)
    assert keys == res

    db.close()
    del_data(config)
