"""
Test the encryption module.
"""
from unittest.mock import Mock, patch

import pytest

from cshelve import UnknownEncryptionAlgorithmError, MissingEncryptionKeyError
from cshelve._encryption import configure
from cshelve._data_processing import DataProcessing


@pytest.fixture
def data_processing():
    return DataProcessing(Mock())


def test_no_encryption(data_processing):
    """
    Ensure nothing si configure when the config is empty.
    """
    logger = Mock()
    config = {}

    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 0
    assert len(data_processing.pre_processing) == 0


def test_default_aes256_config(data_processing):
    """
    Ensure AES256 is configured when defined.
    """
    logger = Mock()
    config = {"algorithm": "aes256", "key": "Sixteen byte key"}

    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 1
    assert len(data_processing.pre_processing) == 1

    first_pre_processing_applied = id(data_processing.pre_processing[0])
    first_post_processing_applied = id(data_processing.post_processing[0])

    # Ensure the same behaviours and order if configured twice.
    configure(logger, data_processing, config)

    assert len(data_processing.post_processing) == 2
    assert len(data_processing.pre_processing) == 2
    # Ensure the order is respected.
    assert first_pre_processing_applied == id(data_processing.pre_processing[0])
    assert first_post_processing_applied == id(data_processing.post_processing[-1])


def test_unknowned_algorithm(data_processing):
    """
    Ensure an exception is raised when an unknowed algorithm is provided.
    """
    logger = Mock()
    config = {"algorithm": "unknow", "key": "Sixteen byte key"}

    with pytest.raises(UnknownEncryptionAlgorithmError):
        configure(logger, data_processing, config)


def test_no_key_provided(data_processing):
    """
    Ensure an exception is raised when no key is provided.
    """
    logger = Mock()
    config = {"algorithm": "aes256"}

    with pytest.raises(MissingEncryptionKeyError):
        configure(logger, data_processing, config)


def test_key_as_env_variable(data_processing):
    """
    Retrieve the key from an environment variable.
    """
    logger = Mock()
    key = "Sixteen byte key"
    config = {"algorithm": "aes256", "environment_key": "KEY_IN_ENV"}

    with patch.dict("os.environ", {"KEY_IN_ENV": key}):
        configure(logger, data_processing, config)


def test_key_not_in_env_var(data_processing):
    """
    Ensure an exception is raised when no key is provided in env var.
    """
    logger = Mock()
    config = {"algorithm": "aes256", "environment_key": "KEY_IN_MISSING_ENV"}

    with pytest.raises(MissingEncryptionKeyError):
        configure(logger, data_processing, config)
