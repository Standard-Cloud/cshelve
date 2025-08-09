"""
Package entry point exposing the `open` function to open a cloud shelf and exceptions.

The `open` function is the main entry point of the package.
Based on the file extension, it will open a local or cloud shelf, but in any case, it will return a `shelve.Shelf` object.

If the file extension is `.ini`, the file is considered a configuration file and handled by `cshelve`; otherwise, it will be handled by the standard `shelve` module.
"""
import logging
from pathlib import Path
import shelve
from typing import Any

from ._cloud_shelf import CloudShelf
from ._factory import factory as _factory
from ._parser import (
    load_from_file as _config_loader_from_file,
    load_from_dict as _config_loader_from_dict,
)
from ._parser import use_local_shelf
from .exceptions import (
    AuthArgumentError,
    AuthError,
    AuthTypeError,
    CanNotCreateDBError,
    ConfigurationError,
    DataProcessingSignatureError,
    DBDoesNotExistsError,
    EncryptedDataCorruptionError,
    KeyNotFoundError,
    MissingEncryptionKeyError,
    ReadOnlyError,
    UnknownCompressionAlgorithmError,
    UnknownEncryptionAlgorithmError,
    UnknownProviderError,
)


__all__ = [
    "AuthArgumentError",
    "AuthError",
    "AuthTypeError",
    "CanNotCreateDBError",
    "ConfigurationError",
    "DataProcessingSignatureError",
    "DBDoesNotExistsError",
    "EncryptedDataCorruptionError",
    "KeyNotFoundError",
    "MissingEncryptionKeyError",
    "open",
    "ReadOnlyError",
    "ResourceNotFoundError",
    "UnknownCompressionAlgorithmError",
    "UnknownEncryptionAlgorithmError",
    "UnknownProviderError",
]


# CShelve uses the following pickle protocol instead of the default one used by shelve to support
# very large objects and improve performance (https://docs.python.org/3/library/pickle.html#data-stream-format).
DEFAULT_PICKLE_PROTOCOL = 5


def open(
    filename,
    flag="c",
    protocol=DEFAULT_PICKLE_PROTOCOL,
    writeback=False,
    config_loader=_config_loader_from_file,
    factory=_factory,
    logger=logging.getLogger("cshelve"),
    provider_params={},
) -> shelve.Shelf:
    """
    Open a cloud shelf or a local shelf based on the file extension.
    """
    # Ensure the filename is a Path object.
    filename = Path(filename)

    if use_local_shelf(filename):
        logger.debug("Opening a local shelf.")
        # The user requests a local and not a cloud shelf.
        # Dependending of the Python version, the shelve module doesn't accept Path objects.
        return shelve.open(str(filename), flag, protocol, writeback)

    # Load the configuration file to retrieve the provider and its configuration.
    config = config_loader(logger, filename)

    logger.debug("Opening a cloud shelf.")
    return CloudShelf(
        flag.lower(),
        protocol,
        writeback,
        config,
        factory,
        logger,
        provider_params,
    )


def open_from_dict(
    config: dict[str, Any],
    flag="c",
    protocol=DEFAULT_PICKLE_PROTOCOL,
    writeback=False,
    config_loader=_config_loader_from_dict,
    factory=_factory,
    logger=logging.getLogger("cshelve"),
    provider_params={},
) -> shelve.Shelf:
    """
    Open and configure a Cloud Shelve database from a configuration dictionary.
    """
    # Load the configuration to retrieve the provider and its configuration.
    config = config_loader(logger, config)
    logger.debug("Opening a cloud shelf.")

    return CloudShelf(
        flag.lower(),
        protocol,
        writeback,
        config,
        factory,
        logger,
        provider_params,
    )
