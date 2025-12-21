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
        self.folder_path: Path | None = None
        self.encoding: str = "utf-8"

    def close(self) -> None:
        """No-op for filesystem provider."""
        self.logger.debug("Closing filesystem provider (no-op)")

    def configure_default(self, config: Dict[str, Any]) -> None:
        # No op
        self._config = config

    def configure_logging(self, config: Dict[str, str]) -> None:
        """Filesystem provider does not require special logging configuration."""
        # Intentionally a no-op.
        return None

    def set_provider_params(self, provider_params: Dict[str, Any]) -> None:
        """
        Allow overriding parameters that can't be included in the config directly.
        Values from `configure_default` take precedence if provided.
        """
        config = {
            **provider_params,
            **self._config,
        }

        # Use the current folder path as default.
        self.folder_path = Path(config.get("folder_path", "."))
        # By default, use utf-8 encoding if not provided.
        self.encoding = config.get("encoding", "utf-8")

        self.logger.debug(
            f"Configured filesystem provider with folder_path='{self.folder_path}', "
            f"encoding='{self.encoding}'"
        )

    def contains(self, key: bytes) -> bool:
        """Check if the file for `key` exists."""
        path = self._key_to_path(key)
        exists = path.is_file()
        self.logger.debug(f"Contains check for '{path}': {exists}")
        return exists

    def create(self) -> None:
        """Create the root folder. No-op if it already exists and is a directory."""
        root = self.folder_path
        if root.exists():
            if root.is_dir():
                self.logger.debug(
                    f"Folder '{root}' already exists; create() is a no-op"
                )
                return
            # Path exists but is not a directory => configuration problem
            raise ConfigurationError(f"Path '{root}' exists and is not a directory")
        self.logger.debug(f"Creating folder '{root}'")
        root.mkdir(parents=True)
        self.logger.info(f"Folder '{root}' created")

    @key_access(FileNotFoundError)
    def delete(self, key: bytes) -> None:
        """Delete the file for `key`. Leaves empty parent directories intact."""
        path = self._key_to_path(key)
        self.logger.debug(f"Deleting file '{path}'")
        path.unlink()

    def exists(self) -> bool:
        """Check if the root folder exists."""
        root = self.folder_path
        if not root:
            return False
        exists = root.is_dir()
        self.logger.debug(f"Exists check for '{root}': {exists}")
        return exists

    @key_access(FileNotFoundError)
    def get(self, key: bytes) -> bytes:
        """Read and return the bytes stored for `key`."""
        path = self._key_to_path(key)
        self.logger.debug(f"Reading file '{path}'")
        return path.read_bytes()

    def iter(self) -> Iterator[bytes]:
        """Yield all keys (relative paths) as bytes, recursively."""
        for rel_path in self._list_files_recursive(self.folder_path):
            # Normalize to POSIX-style separators for keys, then encode.
            yield str(rel_path.relative_to(self.folder_path)).encode(self.encoding)

    def len(self) -> int:
        """Return the number of files (keys) recursively."""
        count = len(list(self._list_files_recursive(self.folder_path)))
        self.logger.debug(f"Len for '{self.folder_path}': {count}")
        return count

    def set(self, key: bytes, value: bytes) -> None:
        """Write bytes to the file represented by `key`, creating parent dirs as needed."""
        path = self._key_to_path(key)
        if not path.parent.exists():
            self.logger.debug(f"Creating parent directories '{path.parent}'")
            path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Writing file '{path}' ({len(value)} bytes)")
        path.write_bytes(value)

    def sync(self) -> None:
        """No-op for filesystem provider (writes are immediate)."""
        self.logger.debug("Sync called (no-op for filesystem)")
        return None

    # Helpers
    def _key_to_path(self, key: bytes) -> Path:
        return self.folder_path / Path(key.decode(self.encoding))

    def _list_files_recursive(self, root: Path) -> Iterator[Path]:
        """Return absolute file paths."""
        for item in root.iterdir():
            if item.is_file():
                yield item
            elif item.is_dir():
                # Recursively traverse subdirectories
                yield from self._list_files_recursive(item)
