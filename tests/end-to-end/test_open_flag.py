"""
This file contains the integration tests for the open flag.
The `n` flag is tested in the [sequential tests](../sequential/test_sequential.py) due to its global impact.
"""
import os
import pytest

import cshelve

from helpers import write_data, del_data, unique_key


CONFIG_FILES = [
    "tests/configurations/azure-blob/simulator/flag.ini",
    "tests/configurations/in-memory/persisted.ini",
]


if os.getenv("CI"):
    CONFIG_FILES.append("tests/configurations/azure-blob/real/standard.ini")


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_read_only(config_file):
    """
    A read-only database should not allow writing and must raise an exception if we try to do so.
    The exception is raised by the implementation of the `dbm` module and not by `shelve` itself, so a custom exception is raised.
    """
    key_pattern = unique_key + "test_read_only"
    data_pattern = "test_read_only"

    def cant_update():
        db = cshelve.open(config_file, "r")

        for i in range(10):
            key = f"{key_pattern}{i}"

            assert db[key] == f"{data_pattern}{i}"

            with pytest.raises(cshelve.ReadOnlyError):
                db[key] = data_pattern

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    cant_update()
    del_data(config_file, key_pattern)


@pytest.mark.azure_blob
def test_container_does_not_exists():
    """
    Depending of the flag, the database must already exists otherwise an exception is raised.
    The exception is raised by the implementation of the `dbm` module and not by `shelve` itself, so a custom exception is raised.
    """
    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/azure-blob/real/container-does-not-exists.ini",
            "w",
        )

    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/azure-blob/real/container-does-not-exists.ini",
            "r",
        )
