"""
Depending on the filename, either the native shelve module or the cloud shelve module is used.
The cloud shelve module is used when the filename has a specific extension, and we must ensure that the correct module is used.
"""
from pathlib import Path
from unittest.mock import Mock, patch
import configparser
import os
import pytest

from cshelve._parser import (
    _load_multi_provider_configuration,
    _load_single_provider_configuration,
    _load_configuration,
    _parse_ini_to_nested_dict,
    load_from_file,
    use_local_shelf,
)
from cshelve.exceptions import ConfigurationError


def test_use_local_shelf():
    """
    If the filename is not finishing by '.ini', the default shelve module must be used.
    """
    fallback_default_module = [Path("test.sqlite3"), Path("test.db"), Path("test.dat")]

    for filename in fallback_default_module:
        assert use_local_shelf(filename) is True
        # assert use_local_shelf(Path(filename)) is True


def test_use_cloud_shelf():
    """
    If the filename is finishing by '.ini', the cloud shelve module must be used.
    """
    cloud_module = [Path("test.ini"), Path("cloud.ini"), Path("test.cloud.ini")]

    for filename in cloud_module:
        assert use_local_shelf(filename) is False


def test_azure_configuration():
    """
    Load the Azure configuration file and return it as a dictionary.
    Ensure backward compatibility: single-provider configs should work as before.
    """
    config = load_from_file(
        Mock(), Path("tests/configurations/azure-blob/standard.ini")
    )

    # Single provider mode: should have provider set
    assert config.provider == "azure-blob"

    assert config.default["auth_type"] == "connection_string"
    assert config.default["environment_key"] == "AZURE_STORAGE_CONNECTION_STRING"
    assert config.default["container_name"] == "standard"

    assert config.logging["http"] == "true"
    assert config.logging["credentials"] == "false"
    assert config.logging["level"] == "INFO"

    # Single provider mode: should not have multi-provider fields set
    assert config.strategy is None
    assert config.providers is None


def test_multi_provider_configuration():
    """
    Load a multi-provider configuration file and verify all providers and settings are parsed correctly.
    Each provider should be a Config object maintaining the same structure as a single-provider config.
    """
    with patch.dict(
        os.environ,
        {
            "AWS_KEY_ID": "ID123",
            "AWS_KEY_SECRET": "SECRET456",
        },
    ):
        config = load_from_file(
            Mock(), Path("tests/configurations/config/multi-providers.ini")
        )

    # Should detect multi-provider mode
    assert config.strategy == "all"
    assert config.providers is not None
    assert len(config.providers) == 3

    # Check fast-local provider (should be a Config object)
    fast_local = config.providers[0]
    assert fast_local.provider == "filesystem"
    assert fast_local.default["path"] == "/tmp/cache"
    # Should have provider_params
    assert fast_local.provider_params["whatever"] == "value"
    # Should inherit global compression
    assert fast_local.compression["algorithm"] == "zlib"
    assert fast_local.compression["level"] == "1"
    # Should inherit global encryption
    assert fast_local.encryption["algorithm"] == "aes256"
    assert fast_local.encryption["environment_key"] == "ENCRYPTION_KEY"

    # Check aws-remote provider (should be a Config object)
    aws_remote = config.providers[1]
    assert aws_remote.provider == "aws-s3"
    assert aws_remote.default["bucket_name"] == "cshelve"
    assert aws_remote.default["auth_type"] == "access_key"
    assert aws_remote.default["key_id"] == "ID123"
    assert aws_remote.default["key_secret"] == "SECRET456"
    # Should have overridden compression
    assert aws_remote.compression["algorithm"] == "zlib"
    assert aws_remote.compression["level"] == "9"
    # Should inherit global encryption
    assert aws_remote.encryption["algorithm"] == "aes256"

    # Check azure provider (should be a Config object)
    azure = config.providers[2]
    assert azure.provider == "azure-blob"
    assert azure.default["auth_type"] == "connection_string"
    assert azure.default["environment_key"] == "AZURE_STORAGE_CONNECTION_STRING"
    assert azure.default["container_name"] == "cshelve"
    # Should inherit global compression
    assert azure.compression["algorithm"] == "zlib"
    assert azure.compression["level"] == "1"
    # Should have overridden encryption (disabled)
    assert azure.encryption["algorithm"] == "None"


def test_provider_and_providers_conflict_raises_configuration_error():
    cfg = configparser.ConfigParser()
    cfg.read_string(
        """
[default]
provider = aws-s3
providers = one, two
"""
    )

    with pytest.raises(ConfigurationError):
        _load_configuration(Mock(), cfg)


def test_parse_ini_to_nested_dict():
    """
    Test the INI to nested dict converter handles dot notation sections.
    """
    cfg = configparser.ConfigParser()
    cfg.read_string(
        """
[default]
provider = aws-s3
bucket_name = my-bucket

[compression]
algorithm = zlib
level = 1

[azure]
provider = azure-blob
container_name = mycontainer

[azure.compression]
algorithm = zlib
level = 9

[azure.encryption]
algorithm = aes256
key = secret
"""
    )

    result = _parse_ini_to_nested_dict(cfg)

    # Top-level sections
    assert "default" in result
    assert result["default"]["provider"] == "aws-s3"
    assert result["default"]["bucket_name"] == "my-bucket"

    assert "compression" in result
    assert result["compression"]["algorithm"] == "zlib"
    assert result["compression"]["level"] == "1"

    # Nested sections
    assert "azure" in result
    assert result["azure"]["provider"] == "azure-blob"
    assert result["azure"]["container_name"] == "mycontainer"
    # Overrides should be nested dicts
    assert "compression" in result["azure"]
    assert result["azure"]["compression"]["algorithm"] == "zlib"
    assert result["azure"]["compression"]["level"] == "9"
    assert "encryption" in result["azure"]
    assert result["azure"]["encryption"]["algorithm"] == "aes256"
    assert result["azure"]["encryption"]["key"] == "secret"
