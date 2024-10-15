import shelve

from ._factory import factory as _factory
from ._flag import clear_db
from ._parser import load as _loader
from ._parser import use_local_shelf
from .exceptions import DBDoesnotExistsError, ReadonlyError, UnknownProvider


class CloudShelf(shelve.Shelf):
    def __init__(self, filename, flag, protocol, writeback, loader, factory):
        provider, config = loader(filename)

        cdict = factory(provider)
        cdict.configure(flag, config)

        if clear_db(flag):
            for key in cdict.keys():
                del cdict[key]

        super().__init__(cdict, protocol, writeback)


def open(
    filename, flag="c", protocol=None, writeback=False, loader=_loader, factory=_factory
) -> shelve.Shelf:
    if use_local_shelf(filename):
        # The user requests a local and not a cloud shelf.
        return shelve.open(filename, flag, protocol, writeback)

    return CloudShelf(filename, flag, protocol, writeback, loader, factory)


__all__ = ["open", "UnknownProvider", "ReadonlyError", "DBDoesnotExistsError"]
