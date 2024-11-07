"""
Factory module to return the correct module to be used.
"""
from .provider_interface import ProviderInterface
from .exceptions import UnknownProviderError


def factory(provider: str) -> ProviderInterface:
    """
    Return the correct module to be used.
    """
    if provider == "azure-blob":
        from ._azure_blob_storage import AzureBlobStorage

        return AzureBlobStorage()
    elif provider == "in-memory":
        from ._in_memory import InMemory

        return InMemory()

    raise UnknownProviderError(f"Provider Interface '{provider}' is not supported.")
