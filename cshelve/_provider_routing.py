"""
Provider routing strategies for multi-provider support.

This module defines routing strategies that determine which providers
should handle operations for a given key. Routing strategies enable different
data distribution patterns across multiple providers.

Available Routing Strategies:
    - all: Write to all providers, read from first (replication/backup)
    - hash: Distribute keys across providers using hash-based sharding
"""
from abc import ABC, abstractmethod
from logging import Logger
from typing import TypeVar, Sequence

from .exceptions import UnknownProviderRoutingError


__all__ = [
    "ProviderRouting",
    "AllProviderRouting",
    "HashProviderRouting",
    "create_provider_routing",
]

T = TypeVar("T")  # Generic type for any provider/item


class ProviderRouting(ABC):
    """
    Abstract base class for provider routing strategies.

    A routing strategy determines which items should handle operations
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
    def get_read_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """
        Determine which target(s) to read from for the given key.

        Args:
            key: The key being read as bytes.
            targets: Sequence of available targets (providers, databases, etc.).

        Returns:
            Sequence of targets to read from (typically one target).
        """
        ...

    @abstractmethod
    def get_write_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """
        Determine which target(s) to write to for the given key.

        Args:
            key: The key being written as bytes.
            targets: Sequence of available targets (providers, databases, etc.).

        Returns:
            Sequence of targets to write to.
        """
        ...

    @abstractmethod
    def iter(self, targets: Sequence[T]) -> Sequence[T]:
        """
        Determine which target(s) to iterate from.

        Args:
            targets: Sequence of available targets.

        Returns:
            Sequence of targets to iterate from.
        """
        ...


class AllProviderRouting(ProviderRouting):
    """
    'All' routing strategy: replicate data to all targets.

    This strategy writes to all targets for redundancy and backup,
    while reading from the first target for performance.

    Use cases:
        - Data replication across multiple storage backends
        - Backup and disaster recovery
        - Multi-cloud redundancy

    Behavior:
        - Writes: All targets
        - Reads: First target only
        - Iteration: First target only
    """

    def get_read_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """Read from first target only."""
        return targets[:1]

    def get_write_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """Write to all targets."""
        return targets

    def iter(self, targets: Sequence[T]) -> Sequence[T]:
        """Iterate first target only (all targets are replicated)."""
        return targets[:1]


class HashProviderRouting(ProviderRouting):
    """
    'Hash' routing strategy: distribute keys across targets using hashing.

    This strategy uses hash-based sharding to distribute keys evenly across
    multiple targets. Each key is consistently routed to the same target.

    Use cases:
        - Load balancing across storage backends
        - Horizontal scaling for large datasets
        - Cost optimization by distributing data

    Behavior:
        - Writes: Single target based on hash(key) % num_targets
        - Reads: Same target as writes (consistent routing)
        - Iteration: All targets (keys are distributed)
    """

    def get_read_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """Read from hash-routed target."""
        index = self._hash_key(key, len(targets))
        return [targets[index]]

    def get_write_targets(self, key: bytes, targets: Sequence[T]) -> Sequence[T]:
        """Write to hash-routed target."""
        index = self._hash_key(key, len(targets))
        return [targets[index]]

    def iter(self, targets: Sequence[T]) -> Sequence[T]:
        """Iterate all targets (keys are distributed across them)."""
        return targets

    def _hash_key(self, key: bytes, num_targets: int) -> int:
        """
        Calculate target index for the given key.

        Uses Python's built-in hash function with modulo to ensure
        consistent routing of keys to the same target.

        Args:
            key: The key to hash as bytes.
            num_targets: Number of available targets.

        Returns:
            Target index (0 to num_targets-1).
        """
        return hash(key) % num_targets


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
