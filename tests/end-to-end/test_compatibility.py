"""
Ensure migration are possible and invisible for users.
"""
import pytest
import cshelve
from cshelve import DataProcessingSignatureError


def test_init_to_compression():
    """
    Ensure the smooth migration from standard to compression.
    """
    init = "tests/configurations/in-memory/compatibility/init.ini"
    compressed = "tests/configurations/in-memory/compatibility/compressed.ini"
    uncompressed = "tests/configurations/in-memory/compatibility/uncompressed.ini"

    key = "test_init_to_compression"
    data = "data that will be compressed."

    with cshelve.open(init) as db:
        db[key] = data

    with cshelve.open(compressed) as db:
        assert db[key] == data
        db[key] = data

    with cshelve.open(uncompressed) as db:
        assert db[key] == data
        db[key] = data


def test_error_compression_to_init():
    """
    Ensure the smooth migration from standard to compression.
    """
    init = "tests/configurations/in-memory/compatibility/init.ini"
    compressed = "tests/configurations/in-memory/compatibility/compressed.ini"

    key = "test_error_compression_to_init"
    data = "data can't be uncompressed."

    with cshelve.open(compressed) as db:
        db[key] = data

    with pytest.raises(DataProcessingSignatureError):
        with cshelve.open(init) as db:
            assert db[key] == data
            db[key] = data
