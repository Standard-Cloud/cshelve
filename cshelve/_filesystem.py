import os
from pathlib import Path
from typing import Any, Dict, Iterator, List

from .exceptions import ConfigurationError, key_access
from .provider_interface import ProviderInterface


class FileSystem(ProviderInterface):
    """
    Local filesystem provider.

    Stores each key as a file under a configured `folder_path`.
    - Creates nested directories when setting values (e.g., key "a/b/c").
    - Deletes only the file for a given key; leaves empty directories in place
      by design to avoid extra parsing and to be safe with parallel access.
    - `exists()` checks the existence of the root folder, not individual files.
    - Supports configurable `encoding` for key decoding (default: 'utf-8').
    """

    def __init__(self, logger) -> None:
        super().__init__(logger)
        self._config: Dict[str, Any] = {}
        self.folder_path: str | None = None
        self.encoding: str = "utf-8"

    def close(self) -> None:
        """No-op for filesystem provider."""
        self.logger.debug("Closing filesystem provider (no-op)")

    def configure_default(self, config: Dict[str, Any]) -> None:
        """
        Default configuration of the provider.

        Required parameters:
        - folder_path: target folder. If starts with '/', treated as absolute.
                       Otherwise, treated as relative to current working dir.

        Optional parameters:
        - encoding: string encoding for keys (default: 'utf-8').
        """
        self._config = config or {}
        folder_path = self._config.get("folder_path")
        if not folder_path:
            raise ConfigurationError(
                "'folder_path' must be provided for filesystem provider"
            )

        # Respect absolute vs relative paths cross-platform.
        # If absolute (os.path.isabs), use as-is; else resolve relative to cwd.
        if os.path.isabs(folder_path) or folder_path.startswith("/"):
            self.folder_path = folder_path
        else:
            self.folder_path = str(Path.cwd() / folder_path)

        self.encoding = self._config.get("encoding", "utf-8")

        self.logger.debug(
            f"Configured filesystem provider: folder_path='{self.folder_path}', encoding='{self.encoding}'"
        )

    def configure_logging(self, config: Dict[str, str]) -> None:
        """Filesystem provider does not require special logging configuration."""
        # Intentionally a no-op.
        return None

    def set_provider_params(self, provider_params: Dict[str, Any]) -> None:
        """
        Allow overriding parameters that can't be included in the config directly.
        Values from `configure_default` take precedence if provided.
        """
        if self.folder_path is None:
            folder_path = provider_params.get("folder_path")
            if folder_path:
                if os.path.isabs(folder_path) or folder_path.startswith("/"):
                    self.folder_path = folder_path
                else:
                    self.folder_path = str(Path.cwd() / folder_path)

        # Encoding: default utf-8, config value wins over provider_params.
        if not self._config.get("encoding"):
            self.encoding = provider_params.get("encoding", self.encoding)

        if self.folder_path is None:
            raise ConfigurationError(
                "'folder_path' must be provided for filesystem provider"
            )

    def contains(self, key: bytes) -> bool:
        """Check if the file for `key` exists."""
        path = self._key_to_path(key)
        exists = os.path.isfile(path)
        self.logger.debug(f"Contains check for '{path}': {exists}")
        return exists

    def create(self) -> None:
        """Create the root folder. No-op if it already exists and is a directory."""
        assert (
            self.folder_path is not None
        ), "Provider not configured: folder_path is missing"
        root = self.folder_path
        if os.path.exists(root):
            if os.path.isdir(root):
                self.logger.debug(
                    f"Folder '{root}' already exists; create() is a no-op"
                )
                return
            # Path exists but is not a directory => configuration problem
            raise ConfigurationError(f"Path '{root}' exists and is not a directory")
        self.logger.debug(f"Creating folder '{root}'")
        os.makedirs(root, exist_ok=True)
        self.logger.info(f"Folder '{root}' created")

    @key_access(FileNotFoundError)
    def delete(self, key: bytes) -> None:
        """Delete the file for `key`. Leaves empty parent directories intact."""
        path = self._key_to_path(key)
        self.logger.debug(f"Deleting file '{path}'")
        os.remove(path)
        # Do not remove empty directories by design.

    def exists(self) -> bool:
        """Check if the root folder exists."""
        root = self.folder_path
        if not root:
            return False
        exists = os.path.isdir(root)
        self.logger.debug(f"Exists check for '{root}': {exists}")
        return exists

    @key_access(FileNotFoundError)
    def get(self, key: bytes) -> bytes:
        """Read and return the bytes stored for `key`."""
        path = self._key_to_path(key)
        self.logger.debug(f"Reading file '{path}'")
        with open(path, "rb") as f:
            return f.read()

    def iter(self) -> Iterator[bytes]:
        """Yield all keys (relative paths) as bytes, recursively."""
        assert (
            self.folder_path is not None
        ), "Provider not configured: folder_path is missing"
        root = self.folder_path
        for rel in self._list_files_recursive(root):
            # Normalize to POSIX-style separators for keys, then encode.
            yield rel.encode(self.encoding)

    def len(self) -> int:
        """Return the number of files (keys) recursively."""
        assert (
            self.folder_path is not None
        ), "Provider not configured: folder_path is missing"
        count = len(self._list_files_recursive(self.folder_path))
        self.logger.debug(f"Len for '{self.folder_path}': {count}")
        return count

    def set(self, key: bytes, value: bytes) -> None:
        """Write bytes to the file represented by `key`, creating parent dirs as needed."""
        path = self._key_to_path(key)
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            self.logger.debug(f"Creating parent directories '{parent}'")
            os.makedirs(parent, exist_ok=True)
        self.logger.debug(f"Writing file '{path}' ({len(value)} bytes)")
        with open(path, "wb") as f:
            f.write(value)

    def sync(self) -> None:
        """No-op for filesystem provider (writes are immediate)."""
        self.logger.debug("Sync called (no-op for filesystem)")
        return None

    # Helpers
    def _key_to_path(self, key: bytes) -> str:
        assert (
            self.folder_path is not None
        ), "Provider not configured: folder_path is missing"
        key_str = key.decode(self.encoding)
        # Split on POSIX '/' to support nested keys cross-platform.
        parts: List[str] = key_str.split("/") if key_str else []
        path = (
            os.path.join(self.folder_path, *parts)
            if parts
            else os.path.join(self.folder_path, "")
        )
        return path

    def _list_files_recursive(self, root: str) -> List[str]:
        """Return list of relative file paths (POSIX style) under `root`."""
        results: List[str] = []
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, root)
                # Normalize separators to POSIX for key representation
                rel_posix = Path(rel).as_posix()
                results.append(rel_posix)
        return results
