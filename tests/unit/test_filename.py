"""
Depending on the filename, either the native shelve module or the cloud shelve module is used.
The cloud shelve module is used when the filename has a specific extension, and we must ensure that the correct module is used.
"""
import pickle
import shelve
import tempfile
from unittest.mock import Mock

import cshelve
from cshelve._parser import load, use_local_shelf


def test_use_cloud_shelf():
    """
    Based on the filename, the cloud shelve module must be used.
    At the same time, we test the parser injection functionality.
    """
    filename = "test.ini"
    provider = "myprovider"
    flag = "c"
    config = {
        "provider": provider,
        "auth_type": "passwordless",
        "container_name": "mycontainer",
    }

    cdit = Mock()
    factory = Mock()
    loader = Mock()

    factory.return_value = cdit
    loader.return_value = provider, config

    # Replace the default parser with the mock parser.
    cshelve.open(filename, loader=loader, factory=factory)

    loader.assert_called_once_with(filename)
    factory.assert_called_once_with(provider)
    cdit.configure.assert_called_once_with(flag, config)


def test_use_local_shelf():
    """
    Based on the filename, the default shelve module must be used.
    """
    local_shelf_suffix = ["sqlite3", "db", "dat"]

    for suffix in local_shelf_suffix:
        # When instanciate, shelf modules create the file with the provided name.
        # So we create a temporary file to garbage collect it after the test.
        with tempfile.NamedTemporaryFile(suffix=suffix) as fp:
            fp.close()
            default = cshelve.open(fp.name)
            assert isinstance(default, shelve.DbfilenameShelf)


def test_use_local_shelf():
    """
    If the filename is not finishing by '.ini', the default shelve module must be used.
    """
    fallback_default_module = ["test.sqlite3", "test.db", "test.dat"]

    for filename in fallback_default_module:
        assert use_local_shelf(filename) is True
        # assert use_local_shelf(Path(filename)) is True


def test_use_cloud_shelf():
    """
    If the filename is finishing by '.ini', the cloud shelve module must be used.
    """
    cloud_module = ["test.ini", "cloud.ini", "test.cloud.ini"]

    for filename in cloud_module:
        assert use_local_shelf(filename) is False


def test_azure_configuration():
    """
    Load the Azure configuration file and return it as a dictionary.
    """
    provider, config = load("tests/configurations/azure.ini")

    assert provider == "azure-blob"
    assert config["auth_type"] == "passwordless"
    assert config["account_url"] == "https://myaccount.blob.core.windows.net"
    assert config["container_name"] == "mycontainer"
