"""
Integration tests for the protocol parameter.
The `Shelf` object mainly manages this functionality, but we must ensure `cshelve` can handle it.
"""
import os
import pickle
import pytest

import cshelve

from helpers import unique_key


CONFIG_FILES = [
    "tests/configurations/azure-blob/simulator/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
]

if os.getenv("CI"):
    CONFIG_FILES.append("tests/configurations/azure-blob/real/standard.ini")


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_protocol(config_file):
    """
    Ensure cshelve works correctly with the non default protocol.
    """
    key_pattern = unique_key + "test_protocol"
    data_pattern = "test_protocol"
    protocol = pickle.HIGHEST_PROTOCOL

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(10):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(10):
            assert f"{data_pattern}{i}" == db[f"{key_pattern}{i}"]


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_change_protocol(config_file):
    """
    Ensure cshelve works correctly with the non default protocol.
    """
    key_pattern = unique_key + "test_protocol"
    data_pattern = "test_protocol"
    protocol = pickle.HIGHEST_PROTOCOL

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(10):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(10):
            assert f"{data_pattern}{i}" == db[f"{key_pattern}{i}"]
