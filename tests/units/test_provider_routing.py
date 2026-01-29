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

    def test_get_read_targets_returns_first_only(self):
        """All routing should read from first target only."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        result = routing.get_read_targets(b"any_key", targets)

        assert result == [db1]
        assert len(result) == 1

    def test_get_write_targets_returns_all(self):
        """All routing should write to all targets."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        result = routing.get_write_targets(b"any_key", targets)

        assert result == targets
        assert len(result) == 3

    def test_all_routing_consistent_across_keys(self):
        """All routing behavior should be consistent regardless of key."""
        logger = Mock(spec=Logger)
        routing = AllProviderRouting(logger)

        db1, db2 = Mock(), Mock()
        targets = [db1, db2]

        # Test multiple different keys
        for key in [b"key1", b"key2", b"another_key", b"test"]:
            assert routing.get_read_targets(key, targets) == [db1]
            assert routing.get_write_targets(key, targets) == targets


class TestHashProviderRouting:
    """Test the 'hash' provider routing strategy."""

    def test_get_read_targets_returns_single_based_on_hash(self):
        """Hash routing should return single target based on hash."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        result = routing.get_read_targets(b"test_key", targets)

        assert len(result) == 1
        assert result[0] in targets

    def test_get_write_targets_returns_single_based_on_hash(self):
        """Hash routing should write to single target based on hash."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        result = routing.get_write_targets(b"test_key", targets)

        assert len(result) == 1
        assert result[0] in targets

    def test_hash_routing_consistent_for_same_key(self):
        """Same key should always route to same target."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        key = b"consistent_key"

        # Call multiple times
        result1 = routing.get_read_targets(key, targets)
        result2 = routing.get_read_targets(key, targets)
        result3 = routing.get_write_targets(key, targets)

        assert result1 == result2
        assert result1 == result3

    def test_hash_routing_with_different_provider_counts(self):
        """Test hash routing with 1, 3, and 5 providers by calculating hash directly."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        # Test with 5 sample keys
        sample_keys = [b"key1", b"key2", b"key3", b"key4", b"key5"]

        for num_providers in [1, 3, 5]:
            targets = [Mock() for _ in range(num_providers)]

            for key in sample_keys:
                # Calculate expected index using same hash function
                expected_index = hash(key) % num_providers
                expected_target = targets[expected_index]

                # Verify routing returns the expected target
                result = routing.get_read_targets(key, targets)
                assert result == [expected_target]

                write_result = routing.get_write_targets(key, targets)
                assert write_result == [expected_target]

    def test_hash_routing_with_single_target(self):
        """Hash routing with single target should return that target."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1 = Mock()
        targets = [db1]

        result = routing.get_read_targets(b"any_key", targets)

        assert result == [db1]

    def test_hash_routing_read_write_symmetry(self):
        """Read and write should route to same target for hash strategy."""
        logger = Mock(spec=Logger)
        routing = HashProviderRouting(logger)

        db1, db2, db3 = Mock(), Mock(), Mock()
        targets = [db1, db2, db3]

        for i in range(20):
            key = f"key_{i}".encode()
            read_target = routing.get_read_targets(key, targets)
            write_target = routing.get_write_targets(key, targets)
            assert read_target == write_target


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
