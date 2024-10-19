import pickle
import shelve
import tempfile
from unittest.mock import Mock

import pytest

import cshelve


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


def test_use_protocol():
    """
    Provide the protocol argument and check if it is passed to the shelve module.
    """
    filename = "test.ini"
    provider = "myprovider"
    protocol = pickle.HIGHEST_PROTOCOL
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
    db = cshelve.open(filename, protocol=protocol, loader=loader, factory=factory)

    assert db._protocol == protocol


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
