"""
Factory module to return the correct module to be used.
"""
from logging import Logger
from .provider_interface import ProviderInterface
from .exceptions import UnknownProviderError


def factory(logger: Logger, provider: str) -> ProviderInterface:
    """
    Return the correct module to be used.
    """
    if provider == "azure-blob":
        from ._azure_blob_storage import AzureBlobStorage

        return AzureBlobStorage(logger)
    elif provider == "in-memory":
        from ._in_memory import InMemory

        return InMemory(logger)

    raise UnknownProviderError(f"Provider Interface '{provider}' is not supported.")
