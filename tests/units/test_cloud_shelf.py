"""
The factory ensures that the correct backend is loaded based on the provider.
"""
import pickle
from unittest.mock import Mock

from cshelve import CloudShelf
from cshelve._parser import Config, ProviderConfig


def test_factory_usage():
    """
    End users may want to provide another factory to create the cloud database and not the default one.
    This test ensures that the factory provided is used.
    """
    provider = "fake"
    default_config = {42: 42}
    compression, encryption, provider_params = {}, {}, {}
    flag = "c"
    protocol = pickle.HIGHEST_PROTOCOL
    writeback = False

    cloud_database = Mock()
    factory = Mock()
    logger = Mock()

    provider_config = ProviderConfig(
        provider=provider,
        use_versionning=True,
        default=default_config,
        logging=default_config,
        compression=compression,
        encryption=encryption,
        provider_params=provider_params,
    )

    config = Config(
        providers=[provider_config],
        provider_routing="all",
        use_pickle=True,
    )
    factory.return_value = cloud_database
    cloud_database.exists.return_value = False

    with CloudShelf(
        flag,
        protocol,
        writeback,
        config=config,
        factory=factory,
        logger=logger,
        provider_params={},
    ) as cs:
        cloud_database.exists.assert_called_once()
        factory.assert_called_once_with(logger, provider)
        # The mock returned by the factory must be the MuttableMapping object used by the shelve.Shelf object.
        assert isinstance(cs.dict.databases[0].db, Mock)
