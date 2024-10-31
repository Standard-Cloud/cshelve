"""
The `_CloudDatabase` class is an abstract class that defines the interface for cloud storage backends supporting the `MutableMapping` interface.
This class is used by the `Shelf` class to interact with the cloud storage backend.
"""
from abc import abstractmethod
from typing import Dict


class CloudDatabase:
    """
    This class defines the interface for cloud storage backends that support the MutableMapping interface.
    Except for the custom configure method, all methods are inherited from the MutableMapping class.
    """

    @abstractmethod
    def configure(self, config: Dict[str, str]) -> None:
        """
        Configure the cloud storage backend.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close the cloud storage backend.
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self) -> None:
        """
        Sync the cloud storage backend.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: bytes) -> bytes:
        """
        Get the value associated with the key.
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: bytes) -> None:
        """
        Delete the key and its associated value.
        """
        raise NotImplementedError

    @abstractmethod
    def iter(self) -> bytes:
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
    def contains(self, key: bytes) -> bool:
        """
        Check if the key exists.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self) -> bool:
        """
        Check if the cloud storage backend exists.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self) -> None:
        """
        Create the cloud storage backend.
        """
        raise NotImplementedError


__all__ = ["CloudDatabase"]
