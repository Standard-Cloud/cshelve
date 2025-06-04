"""
SFTP provider implementation for cshelve.
This module implements the SFTP provider interface using paramiko.
"""
from pathlib import Path
from socket import gaierror
from typing import Any, Dict, Iterator

from .exceptions import AuthError, ConfigurationError, key_access

from .provider_interface import ProviderInterface
import threading


class SFTP(ProviderInterface):
    """
    SFTP provider implementation using paramiko.
    This class implements the ProviderInterface for SFTP connections.
    """

    # The SFTP connection from paramiko is not thread-safe.
    IS_THREAD_SAFE = False

    def __init__(self, logger) -> None:
        self._lock = threading.RLock()
        self.logger = logger
        self._sftp_client = None
        self.ssh_client = None
        self.hostname = None
        self.port = 22
        self.username = None
        self.password = None
        self.key_filename = None
        self.remote_path = None
        self.accept_unknown_host_keys = False
        self._provider_parameters = {}

    @property
    def sftp_client(self):
        if not self._sftp_client:
            if not self.ssh_client:
                # Lazy import paramiko.
                paramiko = self._paramiko

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
                try:
                    self.ssh_client.connect(
                        hostname=self.hostname,
                        port=self.port,
                        username=self.username,
                        password=self.password,
                        # key_filename=self.key_filename
                        look_for_keys=False,
                    )
                except paramiko.AuthenticationException as e:
                    self.logger.error(f"Authentication failed: {e}")
                    raise AuthError("Authentication failed for SFTP connection")
                except gaierror as e:
                    self.logger.error(
                        f"Could not resolve hostname {self.hostname}: {e}"
                    )
                    raise AuthError(f"Could not resolve hostname {self.hostname}")
                self.logger.info(
                    f"Connected to SFTP server {self.hostname}:{self.port}"
                )

            self.logger.debug("Creating SFTP client")
            self._sftp_client = self.ssh_client.open_sftp()
            self.logger.info("SFTP client created successfully")

        return self._sftp_client

    def _sftp_path(method):
        """
        Decorator that converts a key to the path on the SFTP before passing it to the method.
        """

        def wrapper(self, key: bytes, *args, **kwargs):
            key_str = key.decode("utf-8")
            # Use forward slash explicitly for SFTP paths regardless of local OS
            full_path = f"{self.remote_path}/{key_str}"
            return method(self, full_path, *args, **kwargs)

        return wrapper

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
        - password: SFTP password (either password or key_filename must be provided)
        - key_filename: SSH private key path (either password or key_filename must be provided)
        - remote_path: Remote directory path, the default is /home/{username}
        - accept_unknown_host_keys: Accept unknown host keys (default: False)
        """
        self.hostname = config.get("hostname")
        self.port = int(config.get("port", "22"))
        self.username = config.get("username")
        self.password = config.get("password")
        self.key_filename = config.get("key_filename")
        self.remote_path = config.get("remote_path")
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
        self.port = self.port or int(provider_params.get("port", "22"))
        self.username = self.username or provider_params.get("username")
        self.password = self.password or provider_params.get("password")
        self.key_filename = self.key_filename or provider_params.get("key_filename")

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

        self._provider_parameters = provider_params

        # Check if required parameters are defined
        if not self.hostname:
            raise ConfigurationError("SFTP hostname is required")
        if not self.port:
            raise ConfigurationError("SFTP port is required")
        if not self.username:
            raise ConfigurationError("SFTP username is required")
        if not (self.password or self.key_filename):
            raise ConfigurationError(
                "Either password or key_filename must be provided for SFTP authentication"
            )

    @_sftp_path
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

    def create(self) -> None:
        """
        Create the remote directory if it doesn't exist.
        """
        self._mkdir(Path(self.remote_path))

    @key_access(Exception)
    @_sftp_path
    def delete(self, key: bytes) -> None:
        """
        Delete the key and its associated value from the SFTP server.
        """
        # Use a lock to prevent concurrent SFTP delete operations
        with self._lock:
            self._rmdir(key)

    def exists(self) -> bool:
        """
        Check if the remote directory exists.
        """
        try:
            self.sftp_client.stat(self.remote_path)
            return True
        except Exception as e:
            try:
                self.sftp_client.listdir(self.remote_path)
            except Exception as e:
                print(e)
                self.logger.error(f"Folder '{self.remote_path}' does not exist")
                return False

    @key_access(Exception)
    @_sftp_path
    def get(self, key: bytes) -> bytes:
        """
        Get the value associated with the key from the SFTP server.
        """
        self.logger.debug(f"Retrieving value for '{key}'")
        with self.sftp_client.open(key, "rb") as f:
            data = f.read()
        return data

    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the SFTP server.
        """
        try:
            files = self.sftp_client.listdir(self.remote_path)
            for filename in files:
                self.logger.debug(f"Yielding key: {filename}")
                yield filename.encode("utf-8")
        except Exception as e:
            self.logger.error(f"Error iterating over keys: {e}")
            raise

    def len(self) -> int:
        """
        Return the number of keys in the SFTP server.
        """
        try:
            files = self.sftp_client.listdir(self.remote_path)
            length = len(files)
            self.logger.debug(f"Number of keys: {length}")
            return length
        except Exception as e:
            self.logger.error(f"Error getting number of keys: {e}")
            raise

    @_sftp_path
    def set(self, key: bytes, value: bytes) -> None:
        """
        Set the value associated with the key in the SFTP server.
        Creates any parent directories if they don't exist.
        """
        try:
            self._mkdir(Path(key).parent)
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
        try:
            # Check if the directory already exists
            self.sftp_client.stat(_full_path)
            self.logger.debug(f"Folder {_full_path} already exists")
            return
        except:
            self.logger.debug(f"Folder {_full_path} does not exists")
        try:
            self.sftp_client.mkdir(_full_path)
            self.logger.debug(f"Folder {_full_path} created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directory {_full_path}: {e}")
            self._mkdir(full_path.parent)
            self.sftp_client.mkdir(_full_path)

    def _rmdir(self, full_path) -> None:
        try:
            # raise Exception(f"list? {full_path}. It may not exist or is not empty.")
            for item in self.sftp_client.listdir(full_path):
                print("listdir item:", item)
                # raise Exception(f"Error removing {full_path}. It may not exist or is not empty.")
                self._rmdir(f"{full_path}/{item}")
            # raise Exception(f"no loop removing {full_path}. It may not exist or is not empty.")
            self.sftp_client.rmdir(full_path)
        except:
            print("Removing file:", full_path, "-------------")
            # raise Exception(f"removing {full_path}. It may not exist or is not empty.")
            self.sftp_client.remove(full_path)

    @property
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
