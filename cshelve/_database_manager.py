"""
Database Manager for Multi-Provider Support.

This module provides the _DatabaseManager class, which wraps multiple _Database instances
to enable multi-provider functionality. It allows cshelve to write data to multiple storage
backends simultaneously while serving reads from a single provider.

Key Features:
    - Write-all provider routing: All write operations are replicated across all configured databases
    - Read-first provider routing: Read operations use only the first database for performance
    - Transparent interface: Implements MutableMapping for dict-like usage
    - Lifecycle management: Handles synchronization, and closing of all databases

The DatabaseManager is the core component that enables redundancy and backup provider routing
in cshelve's multi-provider architecture.
"""
from logging import Logger
from collections.abc import MutableMapping

from ._database import _Database


__all__ = ["_DatabaseManager"]


class _DatabaseManager(MutableMapping):
    """
    Manager that wraps multiple _Database instances and delegates operations to all of them.

    This class enables multi-provider support where data is written to multiple backends simultaneously
    while reads are served from a single (first) provider. This is useful for:
    - Data replication across multiple storage providers
    - Backup provider routing where data is written to primary and backup locations
    - Multi-cloud deployments for redundancy

    Read Provider Routing:
        All read operations (__getitem__, __iter__, __len__) are performed on the first database only.
        This avoids consistency issues and performance overhead of reading from multiple sources.

    Write Provider Routing:
        All write operations (__setitem__, __delitem__, sync) are applied to ALL databases.
        Each database is updated sequentially in the order they were provided.

    Lifecycle Operations:
        - close(): Closes all managed databases
        - sync(): Syncs all managed databases
    """

    def __init__(self, logger: Logger, databases: list[_Database]) -> None:
        """
        Initialize the DatabaseManager with a list of _Database instances.

        Args:
            logger: Logger instance for logging operations across all databases.
            databases: List of _Database objects to manage. Must contain at least one database.
                      The first database in the list is used for all read operations.
        """
        if not databases:
            raise ValueError("DatabaseManager requires at least one database.")

        self.logger = logger
        self.databases = databases
        self.logger.debug(
            f"DatabaseManager initialized with {len(databases)} database(s)."
        )

    def __getitem__(self, key: bytes) -> bytes:
        """
        Retrieve the value associated with the key from the first database.

        Args:
            key: The key to retrieve as bytes.

        Returns:
            The value associated with the key as bytes.
        """
        return self.databases[0][key]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key in all databases.

        This operation writes to all managed databases sequentially.
        If any database write fails, the exception is propagated and subsequent
        databases may not be updated.

        Args:
            key: The key to set as bytes.
            value: The value to associate with the key as bytes.
        """
        for db in self.databases:
            db[key] = value

    def __delitem__(self, key: bytes) -> None:
        """
        Delete the key from all databases.

        This operation removes the key from all managed databases sequentially.
        If the key doesn't exist in a database, the deletion is silently ignored
        (following standard provider behavior).

        Args:
            key: The key to delete as bytes.
        """
        for db in self.databases:
            del db[key]

    def __iter__(self):
        """
        Iterate over the keys in the first database only.

        Returns:
            An iterator over the keys in the first database.

        Note:
            Only keys from the first database are iterated. This assumes all databases
            contain the same keys (by design of the write-all strategy).
        """
        return iter(self.databases[0])

    def __len__(self) -> int:
        """
        Return the number of elements in the first database.

        Returns:
            The count of keys in the first database.

        Note:
            Only the first database's count is returned. This assumes all databases
            contain the same number of keys (by design of the write-all strategy).
        """
        return len(self.databases[0])

    def close(self) -> None:
        """
        Close all databases.
        """
        self.logger.debug("Closing all databases...")
        for db in self.databases:
            db.close()
        self.logger.debug("All databases closed.")

    def sync(self) -> None:
        """
        Sync all databases.
        """
        self.logger.debug("Syncing all databases...")
        for db in self.databases:
            db.sync()
        self.logger.debug("All databases synced.")
