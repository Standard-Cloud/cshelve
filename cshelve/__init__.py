import shelve

from .exceptions import UnknownProvider
from ._factory import factory as _factory
from ._parser import use_local_shelf, load as _loader


class CloudShelf(shelve.Shelf):
    def __init__(self, filename, protocol, writeback, loader, factory):
        provider, config = loader(filename)

        cdict = factory(provider)
        cdict.configure(config)

        super().__init__(cdict, protocol, writeback)


def open(filename, flag='c', protocol=None, writeback=False, loader=_loader, factory=_factory) -> shelve.Shelf:
    if use_local_shelf(filename):
        # The user requests a local and not a cloud shelf.
        return shelve.open(filename, flag, protocol, writeback)

    return CloudShelf(filename, protocol, writeback, loader, factory)


__all__ = ['open', 'UnknownProvider']
