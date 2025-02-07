"""
This Interface defines the interface for storage provider supporting the `MutableMapping` interface.
This class is used by the `Shelf` class to interact with the cloud storage provider.
"""
from abc import abstractmethod
from typing import Any, Dict, Iterator


__all__ = ["ProviderInterface"]


class ProviderInterface:
    """
    This class defines the interface for storage provider to be used by `cshelve`.
    Some methods may be left empty if not needed by the storage provider.
    """

    def __init__(self, logger) -> None:
        self.logger = logger

    @abstractmethod
    def close(self) -> None:
        """
        Close the cloud storage provider.
        """
        raise NotImplementedError

    @abstractmethod
    def configure_default(self, config: Dict[str, str]) -> None:
        """
        Default configuration of the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def configure_logging(self, config: Dict[str, str]) -> None:
        """
        Logging configuration of the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def set_provider_params(self, provider_params: Dict[str, Any]) -> None:
        """
        This method allows the user to specify custom parameters that can't be included in the config.
        """
        raise NotImplementedError

    @abstractmethod
    def contains(self, key: bytes) -> bool:
        """
        Check if the key exists.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self) -> None:
        """
        Create the cloud storage provider.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: bytes) -> None:
        """
        Delete the key and its associated value.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self) -> bool:
        """
        Check if the cloud storage provider exists.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: bytes) -> bytes:
        """
        Get the value associated with the key.
        """
        raise NotImplementedError

    @abstractmethod
    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys.
        """
        raise NotImplementedError

    @abstractmethod
    def len(self) -> int:
        """
        Return the number of keys.
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key.
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self) -> None:
        """
        Sync the cloud storage provider.
        """
        raise NotImplementedError
