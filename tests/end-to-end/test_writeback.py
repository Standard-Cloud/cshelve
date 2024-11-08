"""
This module contains the integration tests for the writeback functionality.
The `Shelf` object manages this feature but the `cshelve` module must provide all the necessary tools.
"""
import pytest
import cshelve

import sys
from helpers import unique_key

CONFIG_FILES = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
]


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_writeback(config_file):
    """
    Ensure the writeback functionality works as expected.
    """
    key_pattern = unique_key + "test_writeback"
    data_pattern = [1]

    def _write_data():
        db = cshelve.open(config_file)

        for i in range(10):
            db[f"{key_pattern}{i}"] = data_pattern

        db.close()

    def update_data(writeback):
        db = cshelve.open(config_file, writeback=writeback)

        for i in range(10):
            key = f"{key_pattern}{i}"
            value = db[key]
            value.append(i)

            if writeback:
                assert db[key] == data_pattern + [i]
            else:
                assert db[key] == data_pattern

        db.close()

    def read_data(contains_index):
        db = cshelve.open(config_file)

        for i in range(10):
            key = f"{key_pattern}{i}"
            if contains_index:
                assert db[key] == data_pattern + [i]
            else:
                assert db[key] == data_pattern

        db.close()

    def del_data():
        db = cshelve.open(config_file)

        for i in range(10):
            del db[f"{key_pattern}{i}"]

        db.close()

    # Write default data.
    _write_data()
    # Update data with writeback=False, so data must not be updated.
    update_data(writeback=False)
    # Ensure data was not updated.
    read_data(contains_index=False)
    # Update data with writeback=True, so data must be updated.
    update_data(writeback=True)
    # Ensure data was updated.
    read_data(contains_index=True)
    del_data()
