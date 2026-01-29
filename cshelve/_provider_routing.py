"""
Provider routing strategies for multi-provider support.

This module defines routing strategies that determine which storage providers
should handle operations for a given key. Routing strategies enable different
data distribution patterns across multiple providers.

Available Routing Strategies:
    - all: Write to all providers, read from first (replication/backup)
    - hash: Distribute keys across providers using hash-based sharding
"""
from abc import ABC, abstractmethod
from logging import Logger
from typing import Iterable

from .exceptions import UnknownProviderRoutingError


__all__ = [
    "ProviderRouting",
    "AllProviderRouting",
    "HashProviderRouting",
    "create_provider_routing",
]


class ProviderRouting:
    """
    Abstract base class for provider routing strategies.

    A routing strategy determines which provider should handle operations
    for a given key in a multi-provider configuration.
    """

    def __init__(self, logger: Logger):
        """
        Initialize the routing strategy.

        Args:
            logger: Logger instance for logging routing decisions.
        """
        self.logger = logger

    @abstractmethod
    def get_read_databases(self, key: bytes, databases: list) -> Iterable:
        """
        Determine which database(s) to read from for the given key.

        Args:
            key: The key being read as bytes.
            databases: List of available database instances.

        Returns:
            List of databases to read from (typically one database).
        """
        ...

    @abstractmethod
    def get_write_databases(self, key: bytes, databases: list) -> Iterable:
        """
        Determine which database(s) to write to for the given key.

        Args:
            key: The key being written as bytes.
            databases: List of available database instances.

        Returns:
            List of databases to write to.
        """
        ...


class AllProviderRouting(ProviderRouting):
    """
    'All' routing strategy: replicate data to all providers.

    This strategy writes to all providers for redundancy and backup,
    while reading from the first provider for performance.

    Use cases:
        - Data replication across multiple storage backends
        - Backup and disaster recovery
        - Multi-cloud redundancy

    Behavior:
        - Writes: All providers
        - Reads: First provider only
        - Iteration: First provider only
        - Length: First provider only
    """

    def get_read_databases(self, key: bytes, databases: list):
        """Read from first database only."""
        return [databases[0]]

    def get_write_databases(self, key: bytes, databases: list):
        """Write to all databases."""
        return databases


class HashProviderRouting(ProviderRouting):
    """
    'Hash' routing strategy: distribute keys across providers using hashing.

    This strategy uses hash-based sharding to distribute keys evenly across
    multiple providers. Each key is consistently routed to the same provider.

    Use cases:
        - Load balancing across storage backends
        - Horizontal scaling for large datasets
        - Cost optimization by distributing data

    Behavior:
        - Writes: Single provider based on hash(key) % num_providers
        - Reads: Same provider as writes (consistent routing)
        - Iteration: All providers (aggregate keys)
        - Length: All providers (sum counts)
    """

    def get_read_databases(self, key: bytes, databases: list):
        """Read from hash-routed database."""
        index = self._hash_key(key, len(databases))
        return [databases[index]]

    def get_write_databases(self, key: bytes, databases: list):
        """Write to hash-routed database."""
        index = self._hash_key(key, len(databases))
        return [databases[index]]

    def _hash_key(self, key: bytes, num_databases: int) -> int:
        """
        Calculate database index for the given key.

        Uses Python's built-in hash function with modulo to ensure
        consistent routing of keys to the same database.

        Args:
            key: The key to hash as bytes.
            num_databases: Number of available databases.

        Returns:
            Database index (0 to num_databases-1).
        """
        return hash(key) % num_databases


def create_provider_routing(routing_type: str, logger: Logger) -> ProviderRouting:
    """
    Factory function to create a provider routing instance.

    Args:
        routing_type: Type of routing strategy ('all' or 'hash').
        logger: Logger instance.

    Returns:
        A ProviderRouting instance of the requested type.

    Raises:
        UnknownProviderRoutingError: If routing_type is not recognized.
    """
    routing_type = routing_type.lower()

    logger.debug(f"Creating provider routing: {routing_type}")

    if routing_type == "all":
        return AllProviderRouting(logger)
    elif routing_type == "hash":
        return HashProviderRouting(logger)
    else:
        raise UnknownProviderRoutingError(
            f"Unknown provider routing type: '{routing_type}'. "
            f"Supported types are: 'all', 'hash'"
        )
