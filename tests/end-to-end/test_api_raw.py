"""
Ensure the standard behavior of the API works as expected in real scenarios.
"""
import json

import pytest

import cshelve

from helpers import unique_key


CONFIG_FILES_RAW = [
    "tests/configurations/aws-s3/no_pickle.ini",
    "tests/configurations/azure-blob/no_pickle.ini",
    "tests/configurations/in-memory/no_pickle.ini",
]


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES_RAW,
)
def test_raw(config_file: str):
    """
    Ensure the mode 'raw' upload file without any processing.
    """
    with cshelve.open(config_file) as db:
        key_pattern = f"{unique_key}-test_raw-{config_file}"
        data_pattern = "test_raw"

        for i in range(10):
            key = f"{key_pattern}{i}"
            data = json.dumps(
                {
                    "my_value": f"{data_pattern}{i}",
                }
            ).encode()

            # Write data to the DB.
            db[key] = data
            # Data must be present in the DB.
            assert db[key] == data
            # Ensure data doesn't contains any processing.
            assert db.dict.db.get(key.encode()) == data
            # Delete the data from the DB.
            del db[key]

    db.close()
