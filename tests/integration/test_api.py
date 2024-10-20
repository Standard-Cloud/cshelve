"""
Ensure the standard behavior of the API works as expected in real scenarios.
"""
import pytest

import cshelve

from helpers import write_data, unique_key
import sys


def test_write_and_read():
    """
    Ensure we can read and write data to the DB.
    """
    with cshelve.open("tests/configurations/azure-integration/standard.ini") as db:

        key_pattern = unique_key + "test_write_and_read"
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


def test_read_after_reopening():
    """
    Ensure the data is still present after reopening the DB.
    """
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = unique_key + "test_read_after_reopening"
    data_pattern = "test_read_after_reopening"

    def read_data():
        db = cshelve.open(config_file)

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    read_data()


@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/azure-integration/standard.ini",
        "tests/configurations/azure-integration/connection-string.ini",
    ],
)
def test_authentication(config_file):
    """
    Test authentication with password and connection string.
    """
    with cshelve.open(config_file) as db:
        key_pattern = unique_key + "test_authentication"
        data_pattern = "test_authentication"

        for i in range(100):
            key = f"{key_pattern}{i}"

            # Write data to the DB.
            db[key] = f"{data_pattern}{i}"
            # Data must be present in the DB.
            assert db[key] == f"{data_pattern}{i}"
            # Delete the data from the DB.
            del db[key]

    db.close()


def test_update_on_operator():
    """
    Ensure operator interface works as expected.
    """
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = unique_key + "test_update_on_operator"
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

    key_pattern = unique_key + "test_contains"
    data_pattern = "test_contains"

    db[key_pattern] = data_pattern

    assert key_pattern in db

    del db[key_pattern]
