"""
Azure Blob Storage implementation.

This module provides an implementation of the ProviderInterface using Azure Blob Storage for storage.

This module uses an Azure container to store key/value data in blobs.
It creates a blob for each key/value pair, where the key is the blob name and the value is the blob content.
Operations such as iteration and length are performed using the container API.

# To use this module, you need to install:
# - The Azure SDK for Python: `pip install cshelve[azure-blob]`
# - If you want to use passwordless authentication, you also need to install the Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
"""
import functools
import io
import os
from typing import Dict, Iterator, Optional

try:
    from azure.core.exceptions import ResourceNotFoundError
    from azure.storage.blob import BlobType
except ImportError:
    raise ImportError(
        "The Azure SDK for Python is required to use the Azure Blob Storage implementation. "
        "You can install it with `pip install cshelve[azure-blob]`"
    )

from .provider_interface import ProviderInterface
from .exceptions import (
    AuthTypeError,
    AuthArgumentError,
    ConfigurationError,
    key_access,
)

# Max size of the LRU cache for the blob clients.
# Blob clients are cached to avoid creating a new client for each operation.
LRU_CACHE_MAX_SIZE = 2048


class AzureBlobStorage(ProviderInterface):
    """
    Implement the database based on the Azure Blob Storage technology.
    """

    def __init__(self) -> None:
        super().__init__()
        self.container_name = None

        # Azure Blob Storage clients.
        self._blob_service_client = None
        self._container_client = None

        # Azure Blob Storage client configuration.
        self._client_configuration = {}
        # Azure Credential configuration.
        self._credentials_configuration = {}

        # Cache the blob clients to avoid creating a new client for each operation.
        # As the class is not hashable, we can't use the lru_cache directly on the class method and so we wrap it.
        cache_fct = functools.partial(self._get_client_cache)
        self._get_client = functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE, typed=False)(
            cache_fct
        )

        # Default configuration parameters.
        self.account_url = None
        self.auth_type = None
        self.environment_key = None

    def configure_default(self, config: Dict[str, str]) -> None:
        """
        Configure the Azure Blob Storage client based on the configuration file.
        """
        # Retrieve the configuration parameters.
        # The Azure Storage Account URL
        # Ex: https://<account_name>.blob.core.windows.net
        self.account_url = config.get("account_url")
        # The authentication type to use.
        # Can be either 'connection_string' or 'passwordless'.
        self.auth_type = config.get("auth_type")
        # The environment variable key that contains the connection string.
        self.environment_key = config.get("environment_key")
        # The name of the container to use.
        # It can be created if it does not exist depending on the flag parameter.
        self.container_name = config.get("container_name")

        if self.container_name is None:
            raise ConfigurationError("Missing container_name in the configuration file")

    @property
    def blob_service_client(self):
        """
        Create the BlobServiceClient and ContainerClient objects when needed.
        """
        if self._blob_service_client is None:
            self._blob_service_client = self.__create_blob_service(
                self.auth_type, self.account_url, self.environment_key
            )
        return self._blob_service_client

    @property
    def container_client(self):
        """
        Only instantiate the container client when it is needed.
        """
        if self._container_client is None:
            self._container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
        return self._container_client

    def configure_logging(self, config: Dict[str, str]) -> None:
        """
        Configure the logging for the InMemory client based on the configuration dictionary.
        """
        if "http" in config:
            self._client_configuration["logging_enable"] = (
                config["http"].lower() == "true"
            )
        if "credentials" in config:
            self._credentials_configuration["logging_enable"] = (
                config["credentials"].lower() == "true"
            )
        if "level" in config:
            import logging

            logger = logging.getLogger("azure.storage.blob")

            # Log levels specific to the Azure SDK.
            # https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging#set-logging-levels
            azure_sdk_log_levels = {
                "CRITICAL": logging.CRITICAL,
                "DEBUG": logging.DEBUG,
                "ERROR": logging.ERROR,
                "INFO": logging.INFO,
                "NOTSET": logging.NOTSET,
                "WARNING": logging.WARNING,
            }
            # If the level is not valid, we ignore the configuration.
            if config["level"] in azure_sdk_log_levels:
                logger.setLevel(azure_sdk_log_levels[config["level"]])

    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def get(self, key: bytes) -> bytes:
        """
        Retrieve the value of the specified key on the Azure Blob Storage container.
        """
        # Azure Blob Storage must be string and not bytes.
        key = key.decode()
        # Init a stream to store the blob content.
        stream = io.BytesIO()

        # Retrieve the blob client.
        client = self._get_client(key)

        # Download the blob content into the stream then return it.
        # The retry pattern and error handling is done by the Azure SDK.
        client.download_blob().readinto(stream)
        return stream.getvalue()

    def close(self) -> None:
        """
        Close the Azure Blob Storage client.
        """
        self.container_client.close()
        self.blob_service_client.close()

    def sync(self) -> None:
        """
        Sync the Azure Blob Storage client.
        """
        # No sync operation is required for Azure Blob Storage.
        ...

    def set(self, key: bytes, value: bytes):
        """
        Create or update the blob with the specified key and value on the Azure Blob Storage container.
        """
        # Azure Blob Storage must be string and not bytes.
        key = key.decode()

        # Retrieve the blob client.
        client = self._get_client(key)

        # Upload the value to a blob named as the key.
        # The retry pattern and error handling is done by the Azure SDK.
        # The blob is overwritten if it already exists.
        # The BlockBlob type is used to store the value as a block blob.
        client.upload_blob(
            value, blob_type=BlobType.BLOCKBLOB, overwrite=True, length=len(value)
        )

    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def delete(self, key: bytes):
        # Azure Blob Storage must be string and not bytes.
        key = key.decode()

        # Retrieve the blob client.
        client = self._get_client(key)

        # Delete the blob.
        # The retry pattern and error handling is done by the Azure SDK.
        client.delete_blob()

    def contains(self, key: bytes) -> bool:
        """
        Return whether the specified key exists on the Azure Blob Storage container.
        """
        # Azure Blob Storage must be string and not bytes.
        return self._get_client(key.decode()).exists()

    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the Azure Blob Storage container.
        """
        for i in self.container_client.list_blob_names():
            # Azure blob names are strings and not bytes.
            # To respect the Shelf interface, we encode the string to bytes.
            yield i.encode()

    def len(self):
        """
        Return the number of objects stored in the database.
        """
        # The Azure SDK does not provide a method to get the number of blobs in a container.
        # We iterate over the blobs and count them.
        return sum(1 for _ in self.container_client.list_blob_names())

    def exists(self) -> bool:
        """
        Check if the container exists on the Azure Blob Storage account.
        """
        return self.blob_service_client.get_container_client(
            self.container_name
        ).exists()

    def create(self):
        """
        Create the container.
        The container must not exist before calling this method.
        """
        self._container_client = self.blob_service_client.create_container(
            self.container_name
        )

    def _get_client_cache(self, key: bytes):
        """
        Cache the blob clients to avoid creating a new client for each operation.
        Size of this object from getsizeof: 48 bytes
        """
        return self.blob_service_client.get_blob_client(self.container_name, key)

    def __create_blob_service(
        self, auth_type: str, account_url: Optional[str], environment_key: Optional[str]
    ):
        # BlobServiceClient and DefaultAzureCredential are imported here to avoid importing them in the module scope.
        # This also simplify the mocking of the Azure SDK in the tests even if it remove the typing information.
        # https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme?view=azure-python#types-of-credentials
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential

        # Create the BlobServiceClient based on the authentication type.
        # A lambda is used to avoid calling the method if the auth_type is not valid.
        supported_auth = {
            "access_key": lambda: BlobServiceClient(
                account_url,
                credential=self.__get_credentials(environment_key),
                **self._client_configuration,
            ),
            "anonymous": lambda: BlobServiceClient(
                account_url, **self._client_configuration
            ),
            "connection_string": lambda: BlobServiceClient.from_connection_string(
                self.__get_credentials(environment_key), **self._client_configuration
            ),
            # Passwordless authentication is only available with the Azure CLI.
            "passwordless": lambda: BlobServiceClient(
                account_url,
                credential=DefaultAzureCredential(**self._credentials_configuration),
                **self._client_configuration,
            ),
        }

        if auth_method := supported_auth.get(auth_type):
            return auth_method()

        raise AuthTypeError(
            f"Invalid auth_type: {auth_type}. Supported values are: {', '.join(supported_auth.keys())}"
        )

    def __get_credentials(self, environment_key: str) -> str:
        """
        Retrieve the credentials from the environment variable or raise the corresponding error.
        """
        if environment_key is None:
            raise AuthArgumentError(f"Missing environment_key parameter")

        if credential := os.environ.get(environment_key):
            return credential

        raise AuthArgumentError(f"Missing environment variable: {environment_key}")
