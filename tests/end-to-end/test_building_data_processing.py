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

        # Data must be compressed so it should be smaller than the original data (+ metadata).
        assert len(db) < len(data)
        assert data == db[key_pattern]


def test_encryption():
    """
    Ensure the data is encrypted.
    """
    wrapper_size = 17  # Database Record + Data Processing Metadata
    standard_configuration = "tests/configurations/in-memory/not-persisted.ini"
    encryption_configuration = "tests/configurations/in-memory/encryption.ini"
    key_pattern = unique_key + "test_encryption"
    data = "this must be encrypted"

    # Ensure the data is not encrypted.
    with cshelve.open(standard_configuration) as db:
        db[key_pattern] = data

        assert data == pickle.loads(db.dict.db.db[key_pattern.encode()][wrapper_size:])

    # Ensure the data is encrypted.
    with cshelve.open(encryption_configuration) as db:
        db[key_pattern] = data

        with pytest.raises(Exception):
            assert data != pickle.loads(
                db.dict.db.db[key_pattern.encode()][wrapper_size:]
            )
