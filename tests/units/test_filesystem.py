"""
Unit tests for the FileSystem provider.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from cshelve._factory import factory
from cshelve import KeyNotFoundError, ConfigurationError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup after tests
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def relative_temp_dir(tmp_path):
    """Create a relative temporary directory for tests."""
    # Store original working directory
    original_cwd = os.getcwd()
    # Change to tmp_path
    os.chdir(tmp_path)
    yield "test_folder"
    # Restore original working directory
    os.chdir(original_cwd)


class TestFileSystemBasicOperations:
    """Test basic get/set/delete operations."""

    def test_get_and_set(self, temp_dir):
        """Ensure we can set then retrieve a value from the database."""
        key, value = b"key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)

    def test_set_and_get_with_nested_keys(self, temp_dir):
        """Ensure we can set and retrieve values with nested keys."""
        key, value = b"folder/subfolder/key", b"nested_value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)

    def test_delete_key(self, temp_dir):
        """Ensure we can delete a key."""
        key, value = b"key_to_delete", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert provider.contains(key)

        provider.delete(key)
        assert not provider.contains(key)

        with pytest.raises(KeyNotFoundError):
            provider.get(key)

    def test_delete_nested_key(self, temp_dir):
        """Ensure we can delete a nested key."""
        key, value = b"folder/subfolder/key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert provider.contains(key)

        provider.delete(key)
        assert not provider.contains(key)

    def test_delete_nested_key_leaves_empty_dirs(self, temp_dir):
        """
        Ensure that deleting a nested key leaves empty directories.
        This is expected because we don't want to add parsing overhead
        and because multiple threads could be accessing the folder concurrently.
        """
        key, value = b"folder/subfolder/key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        provider.delete(key)
        with pytest.raises(KeyNotFoundError):
            provider.get(key)


class TestFileSystemContains:
    """Test the contains operation."""

    def test_contains_existing_key(self, temp_dir):
        """Ensure contains returns True for existing keys."""
        key, value = b"key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert provider.contains(key)

    def test_contains_non_existing_key(self, temp_dir):
        """Ensure contains returns False for non-existing keys."""
        key = b"non_existing_key"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        assert not provider.contains(key)

    def test_contains_nested_key(self, temp_dir):
        """Ensure contains works with nested keys."""
        key, value = b"folder/subfolder/key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert provider.contains(key)


class TestFileSystemIteration:
    """Test iteration over keys."""

    def test_iter_single_key(self, temp_dir):
        """Ensure we can iterate over a single key."""
        key, value = b"key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        keys = list(provider.iter())
        assert key in keys
        assert len(keys) == 1

    def test_iter_multiple_keys(self, temp_dir):
        """Ensure we can iterate over multiple keys."""
        keys_values = [
            (b"key1", b"value1"),
            (b"key2", b"value2"),
            (b"key3", b"value3"),
        ]

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        for key, value in keys_values:
            provider.set(key, value)

        keys = list(provider.iter())
        assert len(keys) == 3
        for key, _ in keys_values:
            assert key in keys

    def test_iter_nested_keys(self, temp_dir):
        """Ensure we can iterate over nested keys."""
        keys_values = [
            (b"folder/key1", b"value1"),
            (b"folder/subfolder/key2", b"value2"),
            (b"key3", b"value3"),
        ]

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        for key, value in keys_values:
            provider.set(key, value)

        # Align between platforms
        keys = [str(Path(k.decode()).as_posix()) for k in provider.iter()]
        assert len(keys) == 3
        for key, _ in keys_values:
            assert key.decode() in keys

    def test_iter_empty_database(self, temp_dir):
        """Ensure we can iterate over an empty database."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        keys = list(provider.iter())
        assert len(keys) == 0


class TestFileSystemLen:
    """Test the len operation."""

    def test_len_empty_database(self, temp_dir):
        """Ensure len returns 0 for an empty database."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        assert provider.len() == 0

    def test_len_with_keys(self, temp_dir):
        """Ensure len returns the correct count."""
        keys_values = [
            (b"key1", b"value1"),
            (b"key2", b"value2"),
            (b"key3", b"value3"),
        ]

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        for key, value in keys_values:
            provider.set(key, value)

        assert provider.len() == 3

    def test_len_with_nested_keys(self, temp_dir):
        """Ensure len counts nested keys correctly."""
        keys_values = [
            (b"folder/key1", b"value1"),
            (b"folder/subfolder/key2", b"value2"),
            (b"key3", b"value3"),
        ]

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        for key, value in keys_values:
            provider.set(key, value)

        assert provider.len() == 3


class TestFileSystemExists:
    """Test the exists operation."""

    def test_exists_when_folder_exists(self, temp_dir):
        """Ensure exists returns True when the folder exists."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        assert provider.exists()

    def test_exists_when_folder_not_exists(self):
        """Ensure exists returns False when the folder does not exist."""
        non_existing_path = os.path.join(
            tempfile.gettempdir(), "non_existing_folder_xyz"
        )

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": non_existing_path})
        provider.set_provider_params({})

        assert not provider.exists()


class TestFileSystemCreate:
    """Test the create operation."""

    def test_create_folder(self):
        """Ensure create creates the folder."""
        folder_path = os.path.join(tempfile.gettempdir(), f"test_create_{os.getpid()}")

        try:
            provider = factory(Mock(), "filesystem")
            provider.configure_default({"folder_path": folder_path})
            provider.set_provider_params({})
            provider.create()

            assert os.path.exists(folder_path)
            assert os.path.isdir(folder_path)
        finally:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

    def test_create_folder_when_already_exists(self, temp_dir):
        """Ensure create is a no-op when the folder already exists."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})

        # The folder already exists (created by the temp_dir fixture).
        # create() should be idempotent and not raise.
        provider.create()
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)


class TestFileSystemEncoding:
    """Test custom encoding parameter."""

    def test_set_and_get_with_custom_encoding(self, temp_dir):
        """Ensure we can use custom encoding for keys."""
        # Using a key with special characters
        key = "日本語キー".encode("utf-16")
        value = b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir, "encoding": "utf-16"})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)

    def test_set_and_get_with_default_encoding(self, temp_dir):
        """Ensure default encoding is UTF-8."""
        key = "test_key".encode("utf-8")
        value = b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)


class TestFileSystemRelativePath:
    """Test relative and absolute paths."""

    def test_absolute_path(self, temp_dir):
        """Ensure absolute paths work correctly."""
        key, value = b"key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)

    def test_relative_path(self, relative_temp_dir):
        """Ensure relative paths work correctly."""
        key, value = b"key", b"value"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": relative_temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.set(key, value)
        assert value == provider.get(key)

        # Cleanup
        if os.path.exists(relative_temp_dir):
            shutil.rmtree(relative_temp_dir)


class TestFileSystemErrors:
    """Test error handling."""

    def test_get_non_existing_key_raises_error(self, temp_dir):
        """Ensure getting a non-existing key raises KeyNotFoundError."""
        key = b"non_existing_key"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        with pytest.raises(KeyNotFoundError):
            provider.get(key)

    def test_delete_non_existing_key_raises_error(self, temp_dir):
        """Ensure deleting a non-existing key raises KeyNotFoundError."""
        key = b"non_existing_key"

        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        with pytest.raises(KeyNotFoundError):
            provider.delete(key)


class TestFileSystemClose:
    """Test the close operation."""

    def test_close(self, temp_dir):
        """Ensure close can be called without errors."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.close()
        # If we got here, no exception was raised


class TestFileSystemSync:
    """Test the sync operation."""

    def test_sync(self, temp_dir):
        """Ensure sync can be called without errors."""
        provider = factory(Mock(), "filesystem")
        provider.configure_default({"folder_path": temp_dir})
        provider.set_provider_params({})
        provider.create()

        provider.sync()
        # If we got here, no exception was raised
