"""
Package entry point exposing the `open` function to open a cloud shelf and exceptions.

The `open` function is the main entry point of the package.
Based on the file extension, it will open a local or cloud shelf, but in any case, it will return a `shelve.Shelf` object.

If the file extension is `.ini`, the file is considered a configuration file and handled by `cshelve`; otherwise, it will be handled by the standard `shelve` module.
"""

import shelve

from ._database import _Database
from ._factory import factory as _factory
from ._parser import load as _loader
from ._parser import use_local_shelf
from .exceptions import (
    AuthArgumentError,
    AuthTypeError,
    CanNotCreateDBError,
    DBDoesNotExistsError,
    KeyNotFoundError,
    ReadOnlyError,
    UnknownProviderError,
)

__all__ = [
    "AuthArgumentError",
    "AuthTypeError",
    "CanNotCreateDBError",
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

    def __init__(self, filename, flag, protocol, writeback, loader, factory):
        # Load the configuration file to retrieve the provider and its configuration.
        provider, config = loader(filename)

        # Let the factory create the provider interface object based on the provider name then configure it.
        provider_interface = factory(provider)
        provider_interface.configure(config)

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
    loader=_loader,
    factory=_factory,
) -> shelve.Shelf:
    """
    Open a cloud shelf or a local shelf based on the file extension.
    """
    if use_local_shelf(filename):
        # The user requests a local and not a cloud shelf.
        return shelve.open(filename, flag, protocol, writeback)

    return CloudShelf(filename, flag.lower(), protocol, writeback, loader, factory)
