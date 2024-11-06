"""
In-memory storage implementation. Mainly for testing purposes.
"""
from typing import Dict, Iterator

from .provider_interface import ProviderInterface
from .exceptions import key_access


# Contains in-memory databases persisted between open/close during the same program execution.
DB_PERSISTED = {}


class InMemory(ProviderInterface):
    """
    Implements an in-memory database using a dictionary.
    This is mainly for the package and users tests.
    """

    def __init__(self) -> None:
        super().__init__()
        self.db = {}
        self.persist_key = None

    def configure(self, config: Dict[str, str]) -> None:
        """
        Configure the InMemory client based on the configuration dictionary.
        """
        # If the persist-key configuration is set, the database will be persisted in memory and reused.
        # This is useful when you open/close multiple times the same database (with the same 'persist-key' value).
        self.persist_key = config.get("persist-key")

        # If defined, retrieve the previous database value.
        if self.persist_key:
            # Save the local database pointer to the persisted database.
            if self.persist_key not in DB_PERSISTED:
                DB_PERSISTED[self.persist_key] = self.db
            else:
                self.db = DB_PERSISTED[self.persist_key]

    @key_access(KeyError)
    def get(self, key: bytes) -> bytes:
        """
        Retrieve the value of the specified key.

        Args:
            key (bytes): The key to retrieve the value for.

        Returns:
            bytes: The value associated with the key.
        """
        return self.db[key]

    def close(self) -> None:
        """
        Close the database by setting the internal dictionary to None.
        This ensures an error if the user tries to reuse the object.
        """
        self.db = None

    def sync(self) -> None:
        """
        Sync the database. This is a no-op for the in-memory implementation.
        """
        pass

    def set(self, key: bytes, value: bytes) -> None:
        """
        Add or update an entry in the database.

        Args:
            key (bytes): The key for the entry.
            value (bytes): The value for the entry.
        """
        self.db[key] = value

    @key_access(KeyError)
    def delete(self, key: bytes) -> None:
        """
        Delete an entry from the database.

        Args:
            key (bytes): The key to delete.
        """
        del self.db[key]

    def contains(self, key: bytes) -> bool:
        """
        Check if the specified key exists in the database.

        Args:
            key (bytes): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self.db

    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the database.

        Returns:
            Iterator[bytes]: An iterator over the keys.
        """
        # Convert in list to avoid RuntimeError: dictionary changed size during iteration
        keys = list(self.db.keys())
        yield from keys

    def len(self) -> int:
        """
        Return the number of objects stored in the database.

        Returns:
            int: The number of objects in the database.
        """
        return len(self.db)

    def exists(self) -> bool:
        """
        Check if the database exists. Always returns True for in-memory implementation.

        Returns:
            bool: True
        """
        return True

    def create(self) -> None:
        """
        Create the database. This is a no-op for the in-memory implementation.
        """
        pass
