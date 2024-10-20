import pytest

import cshelve

from helpers import write_data, del_data, unique_key
import sys


def test_read_only():
    config_file = "tests/configurations/azure-integration/flag.ini"
    key_pattern = unique_key + "test_read_only"
    data_pattern = "test_read_only"

    def cant_update():
        db = cshelve.open(config_file, "r")

        for i in range(100):
            key = f"{key_pattern}{i}"

            assert db[key] == f"{data_pattern}{i}"

            with pytest.raises(cshelve.ReadOnlyError):
                db[key] = data_pattern

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    cant_update()
    del_data(config_file, key_pattern)


def test_container_does_not_exists():
    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/azure-integration/error-handling/container-does-not-exists.ini",
            "w",
        )

    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/azure-integration/error-handling/container-does-not-exists.ini",
            "r",
        )
