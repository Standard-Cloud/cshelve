"""
This module test data processing modules.
"""
import pickle
import zlib

import pytest

import cshelve

from helpers import unique_key


def test_compression():
    """
    Ensure the data is compressed.
    """
    compressed_configuration = "tests/configurations/in-memory/compression.ini"
    key_pattern = unique_key + "test_compression"
    data = "this must be compressed"

    with cshelve.open(compressed_configuration) as db:
        db[key_pattern] = data

        assert (
            pickle.loads(zlib.decompress(db.dict.db.db[key_pattern.encode()])) == data
        )


def test_encryption():
    """
    Ensure the data is encrypted.
    """
    encryption_configuration = "tests/configurations/in-memory/encryption.ini"
    key_pattern = unique_key + "test_encryption"
    data = "this must be encrypted"

    with cshelve.open(encryption_configuration) as db:
        db[key_pattern] = data

        with pytest.raises(Exception):
            # Can't unpickled an encrypted data.
            pickle.loads(db.dict.db.db[key_pattern.encode()])
