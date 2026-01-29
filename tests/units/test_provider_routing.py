"""
Unit tests for provider routing strategies.
"""
import pytest
from unittest.mock import Mock
from logging import Logger

from cshelve._provider_routing import (
    create_provider_routing,
    AllProviderRouting,
    HashProviderRouting,
)
from cshelve.exceptions import UnknownProviderRoutingError


class TestAllProviderRouting:
    """Test the 'all' provider routing strategy."""

    def test_get_read_databases_returns_first_only(self):
        """All routing should read from first database only."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        result = routing.get_read_databases(b"any_key", databases)

        assert result == [db1]
        assert len(result) == 1

    def test_get_write_databases_returns_all(self):
        """All routing should write to all databases."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        result = routing.get_write_databases(b"any_key", databases)

        assert result == databases
        assert len(result) == 3

    def test_all_routing_consistent_across_keys(self):
        """All routing behavior should be consistent regardless of key."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2 = Mock(), Mock()
        databases = [db1, db2]

        # Test multiple different keys
        for key in [b"key1", b"key2", b"another_key", b"test"]:
            assert routing.get_read_databases(key, databases) == [db1]
            assert routing.get_write_databases(key, databases) == databases


class TestHashProviderRouting:
    """Test the 'hash' provider routing strategy."""

    def test_get_read_databases_returns_single_based_on_hash(self):
        """Hash routing should return single database based on hash."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        result = routing.get_read_databases(b"test_key", databases)

        assert len(result) == 1
        assert result[0] in databases

    def test_get_write_databases_returns_single_based_on_hash(self):
        """Hash routing should write to single database based on hash."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        result = routing.get_write_databases(b"test_key", databases)

        assert len(result) == 1
        assert result[0] in databases

    def test_hash_routing_consistent_for_same_key(self):
        """Same key should always route to same database."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        key = b"consistent_key"

        # Call multiple times
        result1 = routing.get_read_databases(key, databases)
        result2 = routing.get_read_databases(key, databases)
        result3 = routing.get_write_databases(key, databases)

        assert result1 == result2
        assert result1 == result3

    def test_hash_routing_distributes_across_databases(self):
        """Hash routing should distribute keys across databases."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        # Test many keys to ensure distribution
        results = {}
        for i in range(100):
            key = f"key_{i}".encode()
            db = routing.get_read_databases(key, databases)[0]
            db_index = databases.index(db)
            results[db_index] = results.get(db_index, 0) + 1

        # All databases should receive at least some keys
        assert len(results) == 3
        # Each should have received some keys (rough distribution)
        for count in results.values():
            assert count > 0

    def test_hash_routing_with_single_database(self):
        """Hash routing with single database should return that database."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1 = Mock()
        databases = [db1]

        result = routing.get_read_databases(b"any_key", databases)

        assert result == [db1]

    def test_hash_routing_read_write_symmetry(self):
        """Read and write should route to same database for hash strategy."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        databases = [db1, db2, db3]

        for i in range(20):
            key = f"key_{i}".encode()
            read_db = routing.get_read_databases(key, databases)
            write_db = routing.get_write_databases(key, databases)
            assert read_db == write_db


class TestCreateProviderRouting:
    """Test the factory function for creating routing instances."""

    def test_create_all_routing(self):
        """Factory should create AllProviderRouting for 'all'."""
        logger = Mock(spec=Logger)
        routing = create_provider_routing("all", logger)

        assert isinstance(routing, AllProviderRouting)

    def test_create_hash_routing(self):
        """Factory should create HashProviderRouting for 'hash'."""
        logger = Mock(spec=Logger)
        routing = create_provider_routing("hash", logger)

        assert isinstance(routing, HashProviderRouting)

    def test_create_unknown_routing_raises_error(self):
        """Factory should raise error for unknown routing type."""
        logger = Mock(spec=Logger)

        with pytest.raises(UnknownProviderRoutingError) as exc_info:
            create_provider_routing("unknown_routing", logger)

        assert "unknown_routing" in str(exc_info.value)

    def test_create_routing_case_insensitive(self):
        """Factory should handle case variations."""
        logger = Mock(spec=Logger)

        # Should work with different cases
        routing1 = create_provider_routing("ALL", logger)
        routing2 = create_provider_routing("All", logger)
        routing3 = create_provider_routing("HASH", logger)

        assert isinstance(routing1, AllProviderRouting)
        assert isinstance(routing2, AllProviderRouting)
        assert isinstance(routing3, HashProviderRouting)
