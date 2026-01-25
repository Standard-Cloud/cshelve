"""
Depending on the filename, either the native shelve module or the cloud shelve module is used.
The cloud shelve module is used when the filename has a specific extension, and we must ensure that the correct module is used.
"""
from pathlib import Path
import shelve
import tempfile
from unittest.mock import Mock

import cshelve
from cshelve._parser import Config, ProviderConfig


def test_load_cloud_shelf_config():
    """
    Based on the filename, the cloud shelve module must be used.
    At the same time, we test the parser injection functionality.
    """
    filename = "test.ini"
    provider = "myprovider"
    default_config = {
        "provider": provider,
        "auth_type": "passwordless",
        "container_name": "mycontainer",
    }
    logging_config = {"http": "true", "credentials": "false"}
    compression_config = {}
    encryption_config = {}
    provider_params_config = {}

    cloud_database = Mock()
    factory = Mock()
    loader = Mock()
    logger = Mock()
    attended_filename = Path(filename)

    factory.return_value = cloud_database

    provider_config = ProviderConfig(
        provider=provider,
        use_versionning=True,
        default=default_config,
        logging=logging_config,
        compression=compression_config,
        encryption=encryption_config,
        provider_params=provider_params_config,
    )

    loader.return_value = Config(
        providers=[provider_config],
        provider_routing="all",
        use_pickle=True,
    )
    cloud_database.exists.return_value = False

    # Replace the default parser with the mock parser.
    with cshelve.open(
        filename, config_loader=loader, factory=factory, logger=logger
    ) as cs:
        loader.assert_called_once_with(logger, attended_filename)
        assert isinstance(cs.dict.databases[0].db, Mock)
        cs.dict.databases[0].db.configure_default.assert_called_once_with(
            default_config
        )
        cs.dict.databases[0].db.configure_logging.assert_called_once_with(
            logging_config
        )


def test_load_cloud_shelf_config_memory():
    """
    Test the open function and the configuration.
    """
    filename = "tests/configurations/in-memory/not-persisted.ini"

    with cshelve.open(filename) as cs:
        # Ensure the default configuration is loaded.
        assert cs.dict.databases[0].db.persist_key is None
        # Ensure the logging is provided.
        # The memory database store it as it provided.
        assert cs.dict.databases[0].db._logging == {"enabled": "true", "level": "INFO"}
        # Ensure the database is created.
        assert cs.dict.databases[0].db._created is False


def test_load_cloud_shelf_config_as_dict_memory():
    """
    Test the open_from_dict function and the configuration.
    """
    config = {
        "default": {"provider": "in-memory", "exists": True},
        "logging": {"enabled": True, "level": "INFO"},
    }

    with cshelve.open_from_dict(config) as cs:
        # Ensure the default configuration is loaded.
        assert cs.dict.databases[0].db.persist_key is None
        # Ensure the logging is provided.
        # The memory database store it as it provided.
        assert cs.dict.databases[0].db._logging == {"enabled": True, "level": "INFO"}
        # Ensure the database is created.
        assert cs.dict.databases[0].db._created is False


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


def test_support_pathlib():
    """
    Provide a pathlib object to the open function and ensure the correct filename is used.
    """
    filepath = Path("tests/configurations/in-memory/persisted.ini")

    with cshelve.open(filepath) as cs:
        cs["key"] = "value"

    with cshelve.open(filepath) as cs:
        assert cs["key"] == "value"


def test_parameters():
    """
    Ensure users parameters are provided to the provider.
    """
    filepath = Path("tests/configurations/in-memory/persisted.ini")
    params = {"foo": "bar", "number": 42}

    with cshelve.open(filepath, provider_params=params) as cs:
        cs._user_parameters = params
