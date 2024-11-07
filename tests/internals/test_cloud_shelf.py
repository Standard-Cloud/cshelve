"""
The factory ensures that the correct backend is loaded based on the provider.
"""
import pickle
from unittest.mock import Mock

from cshelve import CloudShelf


def test_factory_usage():
    """
    Ensure the usage of the factory.
    """
    filename = "does_not_exists.ini"
    provider = "azure-blob"
    config = {42: 42}
    flag = "c"
    protocol = pickle.HIGHEST_PROTOCOL
    writeback = False

    factory = Mock()
    loader = Mock()
    cloud_database = Mock()

    loader.return_value = provider, config
    factory.return_value = cloud_database
    cloud_database.exists.return_value = False

    with CloudShelf(
        filename, flag, protocol, writeback, loader=loader, factory=factory
    ) as cs:
        cloud_database.exists.assert_called_once()
        factory.assert_called_once_with(provider)
        # The mock returned by the factory must be the MuttableMapping object used by the shelve.Shelf object.
        assert isinstance(cs.dict.db, Mock)


def test_loader_usage():
    """
    Ensure the usage of the loader.
    """
    filename = "does_not_exists.ini"
    provider = "azure-blob"
    config = {42: 42}
    flag = "c"
    protocol = pickle.HIGHEST_PROTOCOL
    writeback = False

    factory = Mock()
    loader = Mock()
    cloud_database = Mock()

    loader.return_value = provider, config
    factory.return_value = cloud_database
    cloud_database.exists.return_value = False

    with CloudShelf(
        filename, flag, protocol, writeback, loader=loader, factory=factory
    ) as cs:
        loader.assert_called_once_with(filename)


def test_provider_configuration():
    """
    Ensure the provider returns by the factory is configured.
    """
    filename = "does_not_exists.ini"
    provider = "azure-blob"
    config = {42: 42}
    flag = "c"
    protocol = pickle.HIGHEST_PROTOCOL
    writeback = False

    factory = Mock()
    loader = Mock()
    cloud_database = Mock()

    loader.return_value = provider, config
    factory.return_value = cloud_database
    cloud_database.exists.return_value = False

    with CloudShelf(
        filename, flag, protocol, writeback, loader=loader, factory=factory
    ) as _:
        cloud_database.configure.assert_called_once_with(config)
