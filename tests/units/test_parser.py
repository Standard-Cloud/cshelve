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
    _load_configuration,
    _parse_ini_to_nested_dict,
    load_from_file,
    load_from_dict,
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
        assert use_local_shelf(Path(filename)) is True


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
    Single-provider configs are now transformed into a providers list with one item.
    """
    config = load_from_file(
        Mock(), Path("tests/configurations/azure-blob/standard.ini")
    )

    # Config should only have strategy, providers, and use_pickle
    assert config.use_pickle == True
    assert config.strategy == "all"  # Default strategy for single provider
    assert config.providers is not None
    assert len(config.providers) == 1

    # Access provider details through providers list
    provider = config.providers[0]
    assert provider.provider == "azure-blob"
    assert provider.default["auth_type"] == "connection_string"
    assert provider.default["environment_key"] == "AZURE_STORAGE_CONNECTION_STRING"
    assert provider.default["container_name"] == "standard"

    assert provider.logging["http"] == "true"
    assert provider.logging["credentials"] == "false"
    assert provider.logging["level"] == "INFO"


def _assert_multi_provider_config(config):
    """
    Helper function to validate multi-provider configuration structure.
    Used by both load_from_file and load_from_dict tests.
    """
    # Should detect multi-provider mode
    assert config.strategy == "all"
    assert config.providers is not None
    assert len(config.providers) == 3

    # Check fast-local provider
    fast_local = config.providers[0]
    assert fast_local.provider == "filesystem"
    assert fast_local.default["path"] == "/tmp/cache"
    assert fast_local.use_versionning == True
    # Verify provider_params are set
    assert fast_local.provider_params["whatever"] == "value"
    # Verify global compression is inherited
    assert fast_local.compression["algorithm"] == "zlib"
    assert fast_local.compression["level"] == "1"
    # Verify global encryption is inherited
    assert fast_local.encryption["algorithm"] == "aes256"
    assert fast_local.encryption["environment_key"] == "ENCRYPTION_KEY"

    # Check aws-remote provider
    aws_remote = config.providers[1]
    assert aws_remote.provider == "aws-s3"
    assert aws_remote.default["bucket_name"] == "cshelve"
    assert aws_remote.default["auth_type"] == "access_key"
    assert aws_remote.default["key_id"] == "ID123"
    assert aws_remote.default["key_secret"] == "SECRET456"
    assert aws_remote.use_versionning == True
    # Verify provider_params are empty (not set for this provider)
    assert aws_remote.provider_params == {}
    # Verify compression override is applied
    assert aws_remote.compression["algorithm"] == "zlib"
    assert aws_remote.compression["level"] == "9"
    # Verify global encryption is inherited (not overridden)
    assert aws_remote.encryption["algorithm"] == "aes256"
    assert aws_remote.encryption["environment_key"] == "ENCRYPTION_KEY"

    # Check azure provider
    azure = config.providers[2]
    assert azure.provider == "azure-blob"
    assert azure.default["auth_type"] == "connection_string"
    assert azure.default["environment_key"] == "AZURE_STORAGE_CONNECTION_STRING"
    assert azure.default["container_name"] == "cshelve"
    assert azure.use_versionning == True
    # Verify provider_params are empty
    assert azure.provider_params == {}
    # Verify global compression is inherited (not overridden)
    assert azure.compression["algorithm"] == "zlib"
    assert azure.compression["level"] == "1"
    # Verify encryption override is applied
    assert azure.encryption["algorithm"] == "None"


def test_multi_provider_configuration():
    """
    Load a multi-provider configuration from INI file and verify all providers and settings.
    """
    with patch.dict(
        os.environ,
        {
            "AWS_KEY_ID": "ID123",
            "AWS_KEY_SECRET": "SECRET456",
            "ENCRYPTION_KEY": "key12345",
            "AZURE_STORAGE_CONNECTION_STRING": "azure_conn_str",
        },
    ):
        config = load_from_file(
            Mock(), Path("tests/configurations/config/multi-providers.ini")
        )

    _assert_multi_provider_config(config)


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


def test_load_from_dict_multi_provider():
    """
    Load a multi-provider configuration from a dict and verify all providers and settings.
    Uses the same configuration structure as test_multi_provider_configuration but in dict format.
    """
    config_dict = {
        "default": {
            "providers": "fast-local, aws-remote, azure",
            "strategy": "all",
            "use_pickle": "true",
            "use_versionning": "true",
        },
        "compression": {
            "algorithm": "zlib",
            "level": "1",
        },
        "encryption": {
            "algorithm": "aes256",
            "environment_key": "ENCRYPTION_KEY",
        },
        "fast-local": {
            "provider": "filesystem",
            "path": "/tmp/cache",
            "provider_params": {
                "whatever": "value",
            },
        },
        "aws-remote": {
            "provider": "aws-s3",
            "bucket_name": "cshelve",
            "auth_type": "access_key",
            "key_id": "$AWS_KEY_ID",
            "key_secret": "$AWS_KEY_SECRET",
            "compression": {
                "algorithm": "zlib",
                "level": "9",
            },
        },
        "azure": {
            "provider": "azure-blob",
            "auth_type": "connection_string",
            "environment_key": "AZURE_STORAGE_CONNECTION_STRING",
            "container_name": "cshelve",
            "encryption": {
                "algorithm": "None",
            },
        },
    }

    with patch.dict(
        os.environ,
        {
            "AWS_KEY_ID": "ID123",
            "AWS_KEY_SECRET": "SECRET456",
            "ENCRYPTION_KEY": "key12345",
            "AZURE_STORAGE_CONNECTION_STRING": "azure_conn_str",
        },
    ):
        config = load_from_dict(Mock(), config_dict)

    _assert_multi_provider_config(config)
