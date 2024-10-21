"""
Package entry point exposing the `open` function to open a cloud shelf and exceptions.

The `open` function is the main entry point of the package.
Based on the file extension, it will open a local or cloud shelf, but in any case, it will return a `shelve.Shelf` object.

If the file extension is `.ini`, the file is considered a configuration file and handled by `cshelve`; otherwise, it will be handled by the standard `shelve` module.
"""

import shelve

from ._factory import factory as _factory
from ._flag import clear_db
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


class CloudShelf(shelve.Shelf):
    """
    A cloud shelf is a shelf that is stored in the cloud. It is a subclass of `shelve.Shelf` and is used to store data in the cloud.

    It main purpose is to load the configuration file, create a factory object, and configure the factory object based on the configuration file.
    """

    def __init__(self, filename, flag, protocol, writeback, loader, factory):
        # Ensure the flag format.
        flag = flag.lower()

        # Load the configuration file to retrieve the provider and its configuration.
        provider, config = loader(filename)

        # Based on the provider, create the corresponding object then configure it.
        cdict = factory(provider)
        cdict.configure(flag, config)

        # If the flag parameter indicates, clear the database.
        if clear_db(flag):
            for key in cdict.keys():
                del cdict[key]

        # Let the standard shelve.Shelf class handle the rest.
        super().__init__(cdict, protocol, writeback)


def open(
    filename, flag="c", protocol=None, writeback=False, loader=_loader, factory=_factory
) -> shelve.Shelf:
    """
    Open a cloud shelf or a local shelf based on the file extension.
    """
    if use_local_shelf(filename):
        # The user requests a local and not a cloud shelf.
        return shelve.open(filename, flag, protocol, writeback)

    return CloudShelf(filename, flag, protocol, writeback, loader, factory)


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
