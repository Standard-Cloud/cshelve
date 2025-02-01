"""
Ensure the library can handle large data.
"""
import pytest
import numpy as np
import pandas as pd

import cshelve

from helpers import unique_key

CONFIG_FILES = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
    "tests/configurations/azure-blob/encryption.ini",
    "tests/configurations/in-memory/encryption.ini",
    "tests/configurations/in-memory/compression.ini",
    "tests/configurations/azure-blob/compression.ini",
    "tests/configurations/in-memory/encryption-and-compression.ini",
    "tests/configurations/azure-blob/encryption-and-compression.ini",
]


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_large(config_file):
    """
    Update a relative large DataFrame in the DB to verify it is possible.
    """
    db = cshelve.open(config_file)

    key_pattern = unique_key + "test_large"

    # 167.46 MiB
    df = pd.DataFrame(
        np.random.randint(0, 100, size=(844221, 26)),
        columns=list("ABCDEFGHIGKLMNOPQRSTUVWXYZ"),
    )

    db[key_pattern] = df
    new_df = db[key_pattern]

    assert id(new_df) != id(df)
    assert new_df.equals(df)


@pytest.mark.azure
@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
@pytest.mark.skip(
    reason="Standard GitHub Runner for Open Source project can't run this test."
)
def test_very_large(config_file):
    """
    Update a relative large DataFrame in the DB to verify it is possible.
    """
    db = cshelve.open(config_file, protocol=4)

    key_pattern = unique_key + "test_very_large"

    # 5.62 GiB
    df = pd.DataFrame(
        np.random.randint(0, 100, size=(13507536, 52)),
        columns=list("ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    )

    db[key_pattern] = df
    new_df = db[key_pattern]

    assert id(new_df) != id(df)
    assert new_df.equals(df)
