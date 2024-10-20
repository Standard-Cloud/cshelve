import pickle

import cshelve

import sys


unique = sys.platform + str(sys.version_info.minor)


def test_protocol():
    """
    Ensure cshelve works correctly with the non default protocol.
    """
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = unique + "test_protocol"
    data_pattern = "test_protocol"
    protocol = pickle.HIGHEST_PROTOCOL

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(100):
            assert f"{data_pattern}{i}" == db[f"{key_pattern}{i}"]


def test_change_protocol():
    """
    Ensure cshelve works correctly with the non default protocol.
    """
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = unique + "test_protocol"
    data_pattern = "test_protocol"
    protocol = pickle.HIGHEST_PROTOCOL

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    with cshelve.open(config_file, protocol=protocol) as db:
        for i in range(100):
            assert f"{data_pattern}{i}" == db[f"{key_pattern}{i}"]
