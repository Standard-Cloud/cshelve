"""
Depending on the filename, either the native shelve module or the cloud shelve module is used.
The cloud shelve module is used when the filename has a specific extension, and we must ensure that the correct module is used.
"""
from pathlib import Path
import shelve
import tempfile
from unittest.mock import Mock

import cshelve


def test_load_cloud_shelf_config():
    """
    Based on the filename, the cloud shelve module must be used.
    At the same time, we test the parser injection functionality.
    """
    filename = "test.ini"
    provider = "myprovider"
    config = {
        "provider": provider,
        "auth_type": "passwordless",
        "container_name": "mycontainer",
    }

    cloud_database = Mock()
    factory = Mock()
    loader = Mock()
    attended_filename = Path(filename)

    factory.return_value = cloud_database
    loader.return_value = provider, config
    cloud_database.exists.return_value = False

    # Replace the default parser with the mock parser.
    with cshelve.open(filename, loader=loader, factory=factory) as cs:
        loader.assert_called_once_with(attended_filename)
        factory.assert_called_once_with(provider)
        assert isinstance(cs.dict.db, Mock)


def test_load_local_shelf_config():
    """
    Based on the filename, the default shelve module must be used.
    """
    local_shelf_suffix = [".sqlite3", ".db", ".dat"]

    for suffix in local_shelf_suffix:
        # When instanciate, shelf modules create the file with the provided name.
        # So we create a temporary file to garbage collect it after the test.
        with tempfile.NamedTemporaryFile(suffix=suffix) as fp:
            fp.close()
            with cshelve.open(fp.name) as db:
                assert isinstance(db, shelve.DbfilenameShelf)


def test_pathlib_not_support_on_all_python_version():
    """
    The pathlib object is not supported on all Python versions with the shelve module.
    We must ensure that the filename is converted to a string before being used.
    """
    my_path = Mock()

    my_path.__str__.return_value = "test.db"
    with cshelve.open(my_path) as db:
        assert isinstance(db, shelve.DbfilenameShelf)
    my_path.__str__.assert_called_once()


def test_support_pathlib():
    """
    Provide a pathlib object to the open function and ensure the correct filename is used.
    """
    filepath = Path("tests/configurations/in-memory/persisted.ini")

    with cshelve.open(filepath) as cs:
        cs["key"] = "value"

    with cshelve.open(filepath) as cs:
        assert cs["key"] == "value"
