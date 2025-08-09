"""
SFTP provider implementation for cshelve.
This module implements the SFTP provider interface using paramiko.
"""
# SFTP is a *nix-based protocol, so we use PurePosixPath for paths.
from pathlib import PurePosixPath
from socket import gaierror
from typing import Any, Dict, Iterator

from .exceptions import AuthError, ConfigurationError, key_access

from .provider_interface import ProviderInterface
import threading


DEFAULT_TIMEOUT = 10  # Default timeout for SFTP operations in seconds


class SFTP(ProviderInterface):
    """
    SFTP provider implementation using paramiko.
    This class implements the ProviderInterface for SFTP connections.
    """

    def __init__(self, logger) -> None:
        super().__init__(logger)
        # The SFTP protocol does not support using the same connection across multiple threads.
        # If multithreading is required, each thread should create its own SFTP connection.
        self._lock = threading.RLock()
        self._sftp_client = None
        self.accept_unknown_host_keys = False
        self.auth_type = None
        self.config = None
        self.hostname = None
        self.port = 22
        self.remote_path = None
        self.ssh_client = None
        self._provider_auth_parameters = {}

    @property
    def sftp_client(self):
        if not self._sftp_client:
            try:
                if not self.ssh_client:
                    # Lazy import paramiko.
                    paramiko = self._paramiko()

                    self.ssh_client = paramiko.client.SSHClient()
                    host_key_policy = (
                        paramiko.AutoAddPolicy()
                        if self.accept_unknown_host_keys
                        else paramiko.RejectPolicy()
                    )
                    self.ssh_client.set_missing_host_key_policy(host_key_policy)
                    self.logger.debug(
                        f"Connecting to SFTP server {self.hostname}:{self.port}"
                    )
                    self.ssh_client.connect(
                        hostname=self.hostname,
                        port=self.port,
                        **self._provider_auth_parameters,
                    )
                    self.logger.info(
                        f"Connected to SFTP server {self.hostname}:{self.port}"
                    )

                self.logger.debug("Creating SFTP client")
                self._sftp_client = self.ssh_client.open_sftp()
                self.logger.info("SFTP client created successfully")

            except gaierror as e:
                self.logger.error(f"Could not resolve hostname {self.hostname}: {e}")
                raise AuthError(f"Could not resolve hostname {self.hostname}")
            except Exception as e:
                self.logger.error(f"Authentication failed: {e}")
                raise AuthError("Authentication failed for SFTP connection") from e

        return self._sftp_client

    def _sftp_path(method):
        """
        Decorator that converts a key to the path on the SFTP before passing it to the method.
        """

        def wrapper(self, key: bytes, *args, **kwargs):
            key_str = key.decode("utf-8")
            full_path = f"{self.remote_path}/{key_str}"
            return method(self, full_path, *args, **kwargs)

        return wrapper

    def _lock(method):
        """
        Decorator that ensures the method is locked to prevent concurrent access.
        """

        def wrapper(self, *args, **kwargs):
            with self._lock:
                return method(self, *args, **kwargs)

        return wrapper

    @_lock
    def close(self) -> None:
        """
        Close the SFTP connection.
        """
        if self.ssh_client:
            self.logger.debug("Closing SSH connection")
            self.ssh_client.close()
            self.ssh_client = None

            if self._sftp_client:
                self.logger.debug("Closing SFTP connection")
                self._sftp_client.close()
                self._sftp_client = None

    def configure_default(self, config: Dict[str, str]) -> None:
        """
        Default configuration of the SFTP provider.

        Required parameters:
        - hostname: SFTP server hostname
        - username: SFTP username

        Optional parameters:
        - port: SFTP port (default: 22)
        - username: SFTP username
        - auth_type: Authentication type, either 'password' or 'key_filename'
        - accept_unknown_host_keys: Accept unknown host keys (default: False)
        """
        self.config = config
        self.hostname = config.get("hostname")
        self.port = int(config.get("port", 22))
        self.auth_type = config.get("auth_type")
        self.remote_path = config.get("remote_path")
        self._provider_auth_parameters["username"] = config.get("username")
        self.accept_unknown_host_keys = config.get("accept_unknown_host_keys")

    def configure_logging(self, config: Dict[str, str]) -> None:
        """
        The client doesn't support logging configuration.
        """
        pass

    def set_provider_params(self, provider_params: Dict[str, Any]) -> None:
        """
        This method allows the user to specify custom parameters that can't be included in the config.
        """
        # The configuration provided from the config overrides the configuration provided from the provider_params
        self.hostname = self.hostname or provider_params.get("hostname")
        self.port = self.port or int(provider_params.get("port", 22))

        # Take the value from the config if it exists, otherwise from the provider_params or default to False.
        if self.accept_unknown_host_keys is None:
            self.accept_unknown_host_keys = provider_params.get(
                "accept_unknown_host_keys", False
            )
        else:
            self.accept_unknown_host_keys = (
                self.accept_unknown_host_keys.lower() == "true"
            )

        # If remote_path is not provided, use the default path based on the username.
        self.remote_path = self.remote_path or provider_params.get("remote_path", "")

        self._provider_auth_parameters["timeout"] = provider_params.get(
            "timeout", DEFAULT_TIMEOUT
        )
        self._provider_auth_parameters["banner_timeout"] = provider_params.get(
            "banner_timeout", DEFAULT_TIMEOUT
        )
        self._provider_auth_parameters["auth_timeout"] = provider_params.get(
            "auth_timeout", DEFAULT_TIMEOUT
        )
        self._provider_auth_parameters["channel_timeout"] = provider_params.get(
            "channel_timeout", DEFAULT_TIMEOUT
        )

        # Handle authentication parameters for paramiko
        if self.auth_type == "password":
            password = self.config.get("password") or provider_params.get("password")

            if not password:
                raise ConfigurationError(
                    "The 'password' parameter must be provided for SFTP authentication"
                )
            self._provider_auth_parameters["password"] = password
        elif self.auth_type == "key_filename":
            key_filename = self.config.get("key_filename") or provider_params.get(
                "key_filename"
            )

            if not key_filename:
                raise ConfigurationError(
                    "The 'key_filename' parameter must be provided for SFTP authentication"
                )
            self._provider_auth_parameters["key_filename"] = key_filename
        else:
            raise ConfigurationError(
                "Unsupported authentication type. Use 'password' or 'key_filename'."
            )

        # Check if required parameters are defined
        if not self.hostname:
            raise ConfigurationError("SFTP hostname is required")
        if not self.port:
            raise ConfigurationError("SFTP port is required")

        username = self.config.get("username") or provider_params.get("username")
        if not username:
            raise ConfigurationError(
                "The 'username' parameter must be provided for SFTP authentication"
            )
        self._provider_auth_parameters["username"] = username

        self._provider_auth_parameters = {
            "look_for_keys": False,
            "allow_agent": False,
            **self._provider_auth_parameters,
        }

    @_sftp_path
    @_lock
    def contains(self, key: bytes) -> bool:
        """
        Check if the key exists in the SFTP server.
        """
        try:
            self.sftp_client.stat(key)
            return True
        except Exception as e:
            self.logger.error(f"File '{key}' does not exists")
            return False

    @_lock
    def create(self) -> None:
        """
        Create the remote directory if it doesn't exist.
        """
        self._mkdir(PurePosixPath(self.remote_path))

    @key_access(Exception)
    @_sftp_path
    @_lock
    def delete(self, key: bytes) -> None:
        """
        Delete the key and its associated value from the SFTP server.
        """
        # Recursive deletion of directories is not supported to maintain consistent behavior with other providers.
        self.logger.debug(f"Removing file {key}")
        self.sftp_client.remove(key)
        self.logger.debug(f"File {key} removed successfully")

    @_lock
    def exists(self) -> bool:
        """
        Check if the remote directory exists.
        """
        try:
            self.sftp_client.stat(self.remote_path)
        except FileNotFoundError:
            self.logger.info(f"Remote path '{self.remote_path}' does not exist.")
            return False
        return True

    @key_access(Exception)
    @_sftp_path
    @_lock
    def get(self, key: bytes) -> bytes:
        """
        Get the value associated with the key from the SFTP server.
        """
        self.logger.debug(f"Retrieving value for '{key}'")
        with self.sftp_client.open(key, "rb") as f:
            data = f.read()
        return data

    # The lock must be acquired inside.
    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the SFTP server.
        """
        yield from self._iter(self.remote_path)

    @_lock
    def len(self) -> int:
        """
        Return the number of keys in the SFTP server.
        """
        return sum(1 for _ in self.iter())

    @_sftp_path
    @_lock
    def set(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key in the SFTP server.
        Creates any parent directories if they don't exist.
        """
        try:
            self._mkdir(PurePosixPath(key).parent)
            with self.sftp_client.open(key, "wb") as f:
                f.write(value)
            self.logger.debug(f"Set value for key: {key}")
        except Exception as e:
            self.logger.error(f"Error setting value for key: {e}")
            raise

    def sync(self) -> None:
        """
        Sync the SFTP provider. This is a no-op for SFTP as changes are applied immediately.
        """
        # No specific sync operation needed for SFTP
        self.logger.debug("Sync called (no-op for SFTP)")
        pass

    def _mkdir(self, full_path) -> None:
        """
        Create a directory for the given key in the SFTP server.
        """
        _full_path = str(full_path)

        if self._exists(_full_path):
            self.logger.error(f"Folder {_full_path} already exists")
            return

        self._mkdir(full_path.parent)

        self.logger.error(f"Creating folder {_full_path}")
        self.sftp_client.mkdir(_full_path)
        self.logger.error(f"Folder {_full_path} created successfully")

    def _paramiko(self):
        """
        Lazy import of paramiko to avoid circular imports.
        """
        try:
            import paramiko
        except ImportError:
            raise ImportError(
                "The paramiko package is required to use the SFTP implementation. "
                "You can install it with `pip install cshelve[sftp]`"
            )
        return paramiko

    def _is_dir(self, key: bytes) -> bool:
        """
        Check if the key is a directory.
        """
        try:
            stat = self.sftp_client.stat(key)
            return stat.st_mode & 0o170000 == 0o040000
        except Exception as e:
            self.logger.error(f"Error checking if '{key}' is a directory: {e}")
            return False

    def _exists(self, key: bytes) -> bool:
        """
        Check if the key exists in the SFTP server.
        """
        try:
            self.sftp_client.stat(key)
            return True
        except Exception as e:
            self.logger.error(f"Error checking existence of '{key}': {e}")
            return False

    def _iter(self, folder):
        with self._lock:
            files = self.sftp_client.listdir(folder)

        for item in files:
            full_path = f"{folder}/{item}"

            with self._lock:
                is_dir = self._is_dir(full_path)

            if is_dir:
                yield from self._iter(full_path)
            else:
                self.logger.debug(f"Yielding key: {item}")

                # Remove the remote path prefix from the full path
                full_path = full_path.encode("utf-8")[len(self.remote_path) + 1 :]

                yield full_path
