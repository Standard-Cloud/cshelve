"""
Database Manager for Multi-Provider Support.

This module provides the _DatabaseManager class, which wraps multiple _Database instances to enable multi-provider functionality with configurable routing strategies.

Key Features:
    - Configurable provider routing: Support different routing strategies (all, hash, etc.)
    - All routing: Replicate writes to all providers, read from first (redundancy/backup)
    - Hash routing: Distribute keys across providers using hash-based sharding (load balancing)
    - Transparent interface: Implements MutableMapping for dict-like usage
    - Lifecycle management: Handles synchronization and closing of all databases

The DatabaseManager uses provider routing strategies to determine which backend(s) should handle operations for each key, enabling flexible data distribution patterns.
"""
from logging import Logger
from collections.abc import MutableMapping

from ._database import _Database
from ._provider_routing import ProviderRouting


__all__ = ["_DatabaseManager"]


class _DatabaseManager(MutableMapping):
    """
    Manager that wraps multiple _Database instances with configurable routing strategies.

    This class enables multi-provider support where routing strategies determine how
    operations are distributed across storage backends.

    Provider Routing:
        The routing strategy determines which database(s) handle each operation.
        Strategies can route to a single database (hash) or all databases (all).

    Lifecycle Operations:
        - close(): Closes all managed databases
        - sync(): Syncs all managed databases
    """

    def __init__(
        self, logger: Logger, databases: list[_Database], routing: ProviderRouting
    ) -> None:
        """
        Initialize the DatabaseManager with databases and a routing strategy.

        Args:
            logger: Logger instance for logging operations across all databases.
            databases: List of _Database objects to manage. Must contain at least one database.
            routing: ProviderRouting instance that determines how operations are distributed.
        """

    def __init__(
        self, logger: Logger, databases: list[_Database], routing: ProviderRouting
    ) -> None:
        """
        Initialize the DatabaseManager with databases and a routing strategy.

        Args:
            logger: Logger instance for logging operations across all databases.
            databases: List of _Database objects to manage. Must contain at least one database.
            routing: ProviderRouting instance that determines how operations are distributed.
        """
        if not databases:
            raise ValueError("DatabaseManager requires at least one database.")

        self.logger = logger
        self.databases = databases
        self.routing = routing
        self.logger.debug(
            f"DatabaseManager initialized with {len(databases)} database(s) "
            f"using '{routing}' routing."
        )

    def __getitem__(self, key: bytes) -> bytes:
        """
        Retrieve the value associated with the key using the routing strategy.

        Args:
            key: The key to retrieve as bytes.

        Returns:
            The value associated with the key as bytes.
        """
        targets = self.routing.get_read_targets(key, self.databases)
        return targets[0][key]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key using the routing strategy.

        The routing strategy determines which database(s) receive the write.

        Args:
            key: The key to set as bytes.
            value: The value to associate with the key as bytes.
        """
        targets = self.routing.get_write_targets(key, self.databases)
        for db in targets:
            db[key] = value

    def __delitem__(self, key: bytes) -> None:
        """
        Delete the key using the routing strategy.

        The routing strategy determines which database(s) to delete from.

        Args:
            key: The key to delete as bytes.
        """
        targets = self.routing.get_write_targets(key, self.databases)
        for db in targets:
            del db[key]

    def __iter__(self):
        """
        Iterate over the keys based on the routing strategy.

        Returns:
            An iterator over the keys.
        """
        seen = set()
        for t in self.routing.iter(self.databases):
            for key in t.keys():
                if key not in seen:
                    seen.add(key)
                    yield key

    def __len__(self) -> int:
        """
        Return the number of keys based on the routing strategy.

        Returns:
            The count of keys.
        """
        return sum(len(d) for d in self.routing.iter(self.databases))

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
