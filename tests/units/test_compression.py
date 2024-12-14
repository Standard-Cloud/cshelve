"""
Test the compression module.
"""
from unittest.mock import Mock
import zlib

import pytest

from cshelve import UnknownCompressionAlgorithmError
from cshelve._compression import configure
from cshelve.data_processing import DataProcessing


@pytest.fixture
def data_processing():
    return DataProcessing()


def test_no_compression(data_processing):
    """
    Ensure nothing si configure when the config is empty.
    """
    logger = Mock()
    config = {}

    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 0
    assert len(data_processing.pre_processing) == 0


def test_default_zlib_config(data_processing):
    """
    Ensure Zlib is configured when defined.
    If no level is provided, the default compression must be set.
    """
    logger = Mock()
    config = {"algorithm": "zlib"}

    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 1
    assert len(data_processing.pre_processing) == 1
    assert data_processing.pre_processing[0].func == zlib.compress
    assert data_processing.post_processing[0].func == zlib.decompress
    assert (
        data_processing.pre_processing[0].keywords["level"]
        == zlib.Z_DEFAULT_COMPRESSION
    )
    assert data_processing.post_processing[0].keywords == {}

    first_pre_processing_applied = id(data_processing.pre_processing[0])
    first_post_processing_applied = id(data_processing.post_processing[0])

    # Ensure the same behaviours and order if configured twice.
    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 2
    assert len(data_processing.pre_processing) == 2
    # Ensure the order is respected.
    assert first_pre_processing_applied == id(data_processing.pre_processing[0])
    assert first_post_processing_applied == id(data_processing.post_processing[0])


def test_zlib_level(data_processing):
    """
    Ensure the Zlib configuration level can be configured.
    """
    logger = Mock()
    compression_level = 5
    config = {"algorithm": "zlib", "level": compression_level}

    configure(logger, data_processing, config)

    assert data_processing.pre_processing[0].keywords["level"] == compression_level


def test_unknowned_algorithm(data_processing):
    """
    Ensure an exception is raised when an unknowed algorithm is provided.
    """
    logger = Mock()
    config = {"algorithm": "unknow"}

    with pytest.raises(UnknownCompressionAlgorithmError):
        configure(logger, data_processing, config)
