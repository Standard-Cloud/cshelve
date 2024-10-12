from typing import Dict

from .exceptions import UnknownProvider
from .cloud_mutable_mapping import CloudMutableMapping


def factory(provider: str) -> CloudMutableMapping:
    """
    Return the backend module to be used.
    """
    if provider == 'azure':
        from ._azure import AzureMutableMapping
        return AzureMutableMapping()

    raise UnknownProvider(f'Cloud provider {provider} is not supported.')
