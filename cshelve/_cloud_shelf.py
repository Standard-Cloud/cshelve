import shelve

from ._compression import configure as _configure_compression
from ._encryption import configure as _configure_encryption
from ._database import _Database
from ._parser import load_from_file as Config
from ._data_processing import DataProcessing


class CloudShelf(shelve.Shelf):
    """
    A cloud shelf is a shelf that is stored in the cloud. It is a subclass of `shelve.Shelf` and is used to store data in the cloud.

    The underlying storage provider is provided by the factory based on the provider name then abstract by the _Database facade.
    """

    def __new__(
        cls,
        flag,
        protocol,
        writeback,
        config: Config,
        factory,
        logger,
        provider_params,
    ):
        """
        Depending on the configuration, the CloudShelf object can be a BytesShelf or a CloudShelf.
        A BytesShelf is simply a CloudShelf that doesn't use the Pickle protocol.
        """
        if config.use_pickle:
            logger.info("Using BytesShelf as the Pickle format is not required.")
            return super(CloudShelf, cls).__new__(CloudShelf)
        return super(CloudShelf, cls).__new__(_BytesShelf)

    def __init__(
        self,
        flag,
        protocol,
        writeback,
        config: Config,
        factory,
        logger,
        provider_params,
    ):
        # Let the factory create the provider interface object based on the provider name then configure it.
        provider_interface = factory(logger, config.provider)
        provider_interface.configure_logging(config.logging)
        provider_interface.configure_default(config.default)
        provider_interface.set_provider_params(
            {**provider_params, **config.provider_params}
        )

        # If Pickle is not used, the data is neither signed nor versioned.
        # Consequently, the user takes responsibility for the format of the data in the storage.
        # This also allows the user to use the cloud shelf as a simple wrapper around cloud storage.
        data_signed_or_versionned = config.use_versionning

        # Data processing object used to apply pre and post processing to the data.
        data_processing = DataProcessing(logger, data_signed_or_versionned)
        _configure_compression(logger, data_processing, config.compression)
        _configure_encryption(logger, data_processing, config.encryption)

        # The CloudDatabase object is the class that interacts with the cloud storage backend.
        # This class doesn't perform or respect the shelve.Shelf logic and interface so we need to wrap it.
        database = _Database(
            logger, provider_interface, flag, data_processing, data_signed_or_versionned
        )
        database._init()

        # Let the standard shelve.Shelf class handle the rest.
        super().__init__(database, protocol, writeback)


class _BytesShelf(CloudShelf):
    """
    BytesShelf is a subclass of CloudShelf that provides methods for
    getting and setting items overriding the behaviours of the Shelf class.
    This overriding is necessary to remove the Pickle conversion.
    """

    def __getitem__(self, key: str) -> bytes:
        try:
            value = self.cache[key]
        except KeyError:
            value = self.dict[key.encode(self.keyencoding)]
            if self.writeback:
                self.cache[key] = value
        return value

    def __setitem__(self, key: str, value: bytes):
        if self.writeback:
            self.cache[key] = value
        self.dict[key.encode(self.keyencoding)] = value
