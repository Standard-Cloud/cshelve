"""
Factory module to return the backend module to be used.
"""
from .cloud_mutable_mapping import CloudMutableMapping
from .exceptions import UnknownProviderError


def factory(provider: str) -> CloudMutableMapping:
    """
    Return the backend module to be used.
    """
    if provider == "azure-blob":
        from ._azure import AzureMutableMapping

        return AzureMutableMapping()

    raise UnknownProviderError(f"Cloud provider {provider} is not supported.")
