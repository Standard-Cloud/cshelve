"""
Package entry point exposing the `open` function to open a cloud shelf and exceptions.

The `open` function is the main entry point of the package.
Based on the file extension, it will open a local or cloud shelf, but in any case, it will return a `shelve.Shelf` object.

If the file extension is `.ini`, the file is considered a configuration file and handled by `cshelve`; otherwise, it will be handled by the standard `shelve` module.
"""

from pathlib import Path
import shelve

from ._database import _Database
from ._factory import factory as _factory
from ._parser import load as _config_loader
from ._parser import use_local_shelf
from .exceptions import (
    AuthArgumentError,
    AuthTypeError,
    CanNotCreateDBError,
    ConfigurationError,
    DBDoesNotExistsError,
    KeyNotFoundError,
    ReadOnlyError,
    UnknownProviderError,
)

__all__ = [
    "AuthArgumentError",
    "AuthTypeError",
    "CanNotCreateDBError",
    "ConfigurationError",
    "DBDoesNotExistsError",
    "KeyNotFoundError",
    "open",
    "ReadOnlyError",
    "ResourceNotFoundError",
    "UnknownProviderError",
]


class CloudShelf(shelve.Shelf):
    """
    A cloud shelf is a shelf that is stored in the cloud. It is a subclass of `shelve.Shelf` and is used to store data in the cloud.

    The underlying storage provider is provided by the factory based on the provider name then abstract by the _Database facade.
    """

    def __init__(self, filename, flag, protocol, writeback, config_loader, factory):
        # Load the configuration file to retrieve the provider and its configuration.
        config = config_loader(filename)

        # Let the factory create the provider interface object based on the provider name then configure it.
        provider_interface = factory(config.provider)
        provider_interface.configure_default(config.default)

        # The CloudDatabase object is the class that interacts with the cloud storage backend.
        # This class doesn't perform or respect the shelve.Shelf logic and interface so we need to wrap it.
        database = _Database(provider_interface, flag)
        database._init()

        # Let the standard shelve.Shelf class handle the rest.
        super().__init__(database, protocol, writeback)


def open(
    filename,
    flag="c",
    protocol=None,
    writeback=False,
    *args,
    config_loader=_config_loader,
    factory=_factory,
) -> shelve.Shelf:
    """
    Open a cloud shelf or a local shelf based on the file extension.
    """
    # Ensure the filename is a Path object.
    filename = Path(filename)

    if use_local_shelf(filename):
        # The user requests a local and not a cloud shelf.
        # Dependending of the Python version, the shelve module doesn't accept Path objects.
        return shelve.open(str(filename), flag, protocol, writeback)

    return CloudShelf(
        filename, flag.lower(), protocol, writeback, config_loader, factory
    )
