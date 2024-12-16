"""
This module test data processing modules.
"""
import pickle
import zlib
import cshelve

from helpers import unique_key


def test_compression():
    """
    Ensure the data is compressed.
    """
    compressed_configuration = "tests/configurations/in-memory/compression.ini"
    key_pattern = unique_key + "test_writeback"
    data = "this must be compressed"

    with cshelve.open(compressed_configuration) as db:
        db[key_pattern] = data

        assert (
            pickle.loads(zlib.decompress(db.dict.db.db[key_pattern.encode()])) == data
        )
