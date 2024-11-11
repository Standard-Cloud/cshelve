"""
Ensure the library can handle large data.
"""
import os
import pytest
import numpy as np
import pandas as pd

import cshelve

from helpers import unique_key

CONFIG_FILES = [
    "tests/configurations/azure-blob/simulator/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
]


if os.getenv("CI"):
    CONFIG_FILES.append("tests/configurations/azure-blob/real/standard.ini")


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
