"""Unit tests for _DatabaseManager class."""
import pytest
from unittest.mock import Mock
from logging import Logger

from cshelve._database_manager import _DatabaseManager


class TestDatabaseManagerInit:
    """Tests for _DatabaseManager initialization."""

    def test_init_with_empty_list_raises_value_error(self):
        """Test that initialization with empty list raises ValueError."""
        logger = Mock(spec=Logger)

        with pytest.raises(ValueError, match="requires at least one database"):
            _DatabaseManager(logger, [])


class TestDatabaseManagerGetItem:
    """Tests for _DatabaseManager.__getitem__ method."""

    def test_getitem_reads_from_first_database_only(self):
        """Test that __getitem__ only reads from the first database."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__getitem__ = Mock(return_value=b"value1")
        db2 = Mock()
        db2.__getitem__ = Mock(return_value=b"value2")

        manager = _DatabaseManager(logger, [db1, db2])
        result = manager[b"key"]

        assert result == b"value1"
        db1.__getitem__.assert_called_once_with(b"key")
        db2.__getitem__.assert_not_called()

    def test_getitem_with_single_database(self):
        """Test __getitem__ with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.__getitem__ = Mock(return_value=b"test_value")

        manager = _DatabaseManager(logger, [db])
        result = manager[b"test_key"]

        assert result == b"test_value"
        db.__getitem__.assert_called_once_with(b"test_key")


class TestDatabaseManagerSetItem:
    """Tests for _DatabaseManager.__setitem__ method."""

    def test_setitem_writes_to_all_databases(self):
        """Test that __setitem__ writes to all databases."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__setitem__ = Mock()
        db2 = Mock()
        db2.__setitem__ = Mock()
        db3 = Mock()
        db3.__setitem__ = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager[b"key"] = b"value"

        db1.__setitem__.assert_called_once_with(b"key", b"value")
        db2.__setitem__.assert_called_once_with(b"key", b"value")
        db3.__setitem__.assert_called_once_with(b"key", b"value")

    def test_setitem_with_single_database(self):
        """Test __setitem__ with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.__setitem__ = Mock()

        manager = _DatabaseManager(logger, [db])
        manager[b"key"] = b"value"

        db.__setitem__.assert_called_once_with(b"key", b"value")

    def test_setitem_calls_databases_sequentially(self):
        """Test that __setitem__ calls databases in order."""
        logger = Mock(spec=Logger)
        call_order = []

        db1 = Mock()
        db1.__setitem__ = Mock(side_effect=lambda k, v: call_order.append("db1"))
        db2 = Mock()
        db2.__setitem__ = Mock(side_effect=lambda k, v: call_order.append("db2"))
        db3 = Mock()
        db3.__setitem__ = Mock(side_effect=lambda k, v: call_order.append("db3"))

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager[b"key"] = b"value"

        assert call_order == ["db1", "db2", "db3"]

    def test_setitem_propagates_exception_on_failure(self):
        """Test that __setitem__ propagates exception when a database fails."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__setitem__ = Mock()
        db2 = Mock()
        db2.__setitem__ = Mock(side_effect=IOError("Database write failed"))
        db3 = Mock()
        db3.__setitem__ = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])

        with pytest.raises(IOError, match="Database write failed"):
            manager[b"key"] = b"value"

        # Verify first database was called before failure
        db1.__setitem__.assert_called_once_with(b"key", b"value")
        # Verify second database failed
        db2.__setitem__.assert_called_once_with(b"key", b"value")
        # Verify third database was not called after failure
        db3.__setitem__.assert_not_called()


class TestDatabaseManagerDelItem:
    """Tests for _DatabaseManager.__delitem__ method."""

    def test_delitem_deletes_from_all_databases(self):
        """Test that __delitem__ deletes from all databases."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__delitem__ = Mock()
        db2 = Mock()
        db2.__delitem__ = Mock()
        db3 = Mock()
        db3.__delitem__ = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])
        del manager[b"key"]

        db1.__delitem__.assert_called_once_with(b"key")
        db2.__delitem__.assert_called_once_with(b"key")
        db3.__delitem__.assert_called_once_with(b"key")

    def test_delitem_with_single_database(self):
        """Test __delitem__ with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.__delitem__ = Mock()

        manager = _DatabaseManager(logger, [db])
        del manager[b"key"]

        db.__delitem__.assert_called_once_with(b"key")

    def test_delitem_calls_databases_sequentially(self):
        """Test that __delitem__ calls databases in order."""
        logger = Mock(spec=Logger)
        call_order = []

        db1 = Mock()
        db1.__delitem__ = Mock(side_effect=lambda k: call_order.append("db1"))
        db2 = Mock()
        db2.__delitem__ = Mock(side_effect=lambda k: call_order.append("db2"))
        db3 = Mock()
        db3.__delitem__ = Mock(side_effect=lambda k: call_order.append("db3"))

        manager = _DatabaseManager(logger, [db1, db2, db3])
        del manager[b"key"]

        assert call_order == ["db1", "db2", "db3"]

    def test_delitem_propagates_exception_on_failure(self):
        """Test that __delitem__ propagates exception when a database fails."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__delitem__ = Mock()
        db2 = Mock()
        db2.__delitem__ = Mock(side_effect=KeyError("Key not found"))
        db3 = Mock()
        db3.__delitem__ = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])

        with pytest.raises(KeyError, match="Key not found"):
            del manager[b"key"]

        # Verify first database was called before failure
        db1.__delitem__.assert_called_once_with(b"key")
        # Verify second database failed
        db2.__delitem__.assert_called_once_with(b"key")
        # Verify third database was not called after failure
        db3.__delitem__.assert_not_called()


class TestDatabaseManagerIter:
    """Tests for _DatabaseManager.__iter__ method."""

    def test_iter_iterates_first_database_only(self):
        """Test that __iter__ only iterates the first database."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__iter__ = Mock(return_value=iter([b"key1", b"key2"]))
        db2 = Mock()
        db2.__iter__ = Mock(return_value=iter([b"key3", b"key4"]))

        manager = _DatabaseManager(logger, [db1, db2])
        result = list(manager)

        assert result == [b"key1", b"key2"]
        db1.__iter__.assert_called_once()
        db2.__iter__.assert_not_called()

    def test_iter_with_single_database(self):
        """Test __iter__ with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.__iter__ = Mock(return_value=iter([b"a", b"b", b"c"]))

        manager = _DatabaseManager(logger, [db])
        result = list(manager)

        assert result == [b"a", b"b", b"c"]
        db.__iter__.assert_called_once()

    def test_iter_with_empty_first_database(self):
        """Test __iter__ when first database is empty."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__iter__ = Mock(return_value=iter([]))
        db2 = Mock()
        db2.__iter__ = Mock(return_value=iter([b"key"]))

        manager = _DatabaseManager(logger, [db1, db2])
        result = list(manager)

        assert result == []
        db1.__iter__.assert_called_once()


class TestDatabaseManagerLen:
    """Tests for _DatabaseManager.__len__ method."""

    def test_len_returns_first_database_length_only(self):
        """Test that __len__ only returns the first database's length."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__len__ = Mock(return_value=5)
        db2 = Mock()
        db2.__len__ = Mock(return_value=10)

        manager = _DatabaseManager(logger, [db1, db2])
        result = len(manager)

        assert result == 5
        db1.__len__.assert_called_once()
        db2.__len__.assert_not_called()

    def test_len_with_single_database(self):
        """Test __len__ with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.__len__ = Mock(return_value=42)

        manager = _DatabaseManager(logger, [db])
        result = len(manager)

        assert result == 42
        db.__len__.assert_called_once()

    def test_len_with_empty_first_database(self):
        """Test __len__ when first database is empty."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__len__ = Mock(return_value=0)
        db2 = Mock()
        db2.__len__ = Mock(return_value=100)

        manager = _DatabaseManager(logger, [db1, db2])
        result = len(manager)

        assert result == 0


class TestDatabaseManagerClose:
    """Tests for _DatabaseManager.close method."""

    def test_close_closes_all_databases(self):
        """Test that close() closes all databases."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.close = Mock()
        db2 = Mock()
        db2.close = Mock()
        db3 = Mock()
        db3.close = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager.close()

        db1.close.assert_called_once()
        db2.close.assert_called_once()
        db3.close.assert_called_once()

    def test_close_with_single_database(self):
        """Test close() with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.close = Mock()

        manager = _DatabaseManager(logger, [db])
        manager.close()

        db.close.assert_called_once()

    def test_close_calls_databases_sequentially(self):
        """Test that close() calls databases in order."""
        logger = Mock(spec=Logger)
        call_order = []

        db1 = Mock()
        db1.close = Mock(side_effect=lambda: call_order.append("db1"))
        db2 = Mock()
        db2.close = Mock(side_effect=lambda: call_order.append("db2"))
        db3 = Mock()
        db3.close = Mock(side_effect=lambda: call_order.append("db3"))

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager.close()

        assert call_order == ["db1", "db2", "db3"]

    def test_close_propagates_exception_on_failure(self):
        """Test that close() propagates exception when a database fails."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.close = Mock()
        db2 = Mock()
        db2.close = Mock(side_effect=RuntimeError("Failed to close database"))
        db3 = Mock()
        db3.close = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])

        with pytest.raises(RuntimeError, match="Failed to close database"):
            manager.close()

        # Verify first database was called before failure
        db1.close.assert_called_once()
        # Verify second database failed
        db2.close.assert_called_once()
        # Verify third database was not called after failure
        db3.close.assert_not_called()


class TestDatabaseManagerSync:
    """Tests for _DatabaseManager.sync method."""

    def test_sync_syncs_all_databases(self):
        """Test that sync() syncs all databases."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.sync = Mock()
        db2 = Mock()
        db2.sync = Mock()
        db3 = Mock()
        db3.sync = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager.sync()

        db1.sync.assert_called_once()
        db2.sync.assert_called_once()
        db3.sync.assert_called_once()
        assert logger.debug.call_count == 3  # init + 2 debug messages

    def test_sync_with_single_database(self):
        """Test sync() with a single database."""
        logger = Mock(spec=Logger)
        db = Mock()
        db.sync = Mock()

        manager = _DatabaseManager(logger, [db])
        manager.sync()

        db.sync.assert_called_once()

    def test_sync_calls_databases_sequentially(self):
        """Test that sync() calls databases in order."""
        logger = Mock(spec=Logger)
        call_order = []

        db1 = Mock()
        db1.sync = Mock(side_effect=lambda: call_order.append("db1"))
        db2 = Mock()
        db2.sync = Mock(side_effect=lambda: call_order.append("db2"))
        db3 = Mock()
        db3.sync = Mock(side_effect=lambda: call_order.append("db3"))

        manager = _DatabaseManager(logger, [db1, db2, db3])
        manager.sync()

        assert call_order == ["db1", "db2", "db3"]

    def test_sync_propagates_exception_on_failure(self):
        """Test that sync() propagates exception when a database fails."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.sync = Mock()
        db2 = Mock()
        db2.sync = Mock(side_effect=IOError("Sync operation failed"))
        db3 = Mock()
        db3.sync = Mock()

        manager = _DatabaseManager(logger, [db1, db2, db3])

        with pytest.raises(IOError, match="Sync operation failed"):
            manager.sync()

        # Verify first database was called before failure
        db1.sync.assert_called_once()
        # Verify second database failed
        db2.sync.assert_called_once()
        # Verify third database was not called after failure
        db3.sync.assert_not_called()


class TestDatabaseManagerMutableMapping:
    """Tests for MutableMapping interface compliance."""

    def test_implements_mutable_mapping_protocol(self):
        """Test that _DatabaseManager implements MutableMapping protocol."""
        from collections.abc import MutableMapping

        logger = Mock(spec=Logger)
        db = Mock()
        manager = _DatabaseManager(logger, [db])

        assert isinstance(manager, MutableMapping)

    def test_keys_returns_first_database_keys(self):
        """Test that keys() returns keys from first database."""
        logger = Mock(spec=Logger)
        db1 = Mock()
        db1.__iter__ = Mock(return_value=iter([b"key1", b"key2"]))
        db2 = Mock()

        manager = _DatabaseManager(logger, [db1, db2])
        keys = list(manager.keys())

        assert keys == [b"key1", b"key2"]
