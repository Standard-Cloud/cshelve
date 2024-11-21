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
        self.container_client = None

        # Cache the blob clients to avoid creating a new client for each operation.
        # As the class is not hashable, we can't use the lru_cache directly on the class method and so we wrap it.
        cache_fct = functools.partial(self._get_client_cache)
        self._get_client = functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE, typed=False)(
            cache_fct
        )

    def configure_default(self, config: Dict[str, str]) -> None:
        """
        Configure the Azure Blob Storage client based on the configuration file.
        """
        # Retrieve the configuration parameters.
        # The Azure Storage Account URL
        # Ex: https://<account_name>.blob.core.windows.net
        account_url = config.get("account_url")
        # The authentication type to use.
        # Can be either 'connection_string' or 'passwordless'.
        auth_type = config.get("auth_type")
        # The environment variable key that contains the connection string.
        environment_key = config.get("environment_key")
        # The name of the container to use.
        # It can be created if it does not exist depending on the flag parameter.
        self.container_name = config.get("container_name")

        if self.container_name is None:
            raise ConfigurationError("Missing container_name in the configuration file")

        # Create the BlobServiceClient and ContainerClient objects.
        self.blob_service_client = self.__create_blob_service(
            auth_type, account_url, environment_key
        )

        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

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
        self.container_client = self.blob_service_client.create_container(
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
                account_url, credential=self.__get_credentials(environment_key)
            ),
            "anonymous": lambda: BlobServiceClient(account_url),
            "connection_string": lambda: BlobServiceClient.from_connection_string(
                self.__get_credentials(environment_key)
            ),
            # Passwordless authentication is only available with the Azure CLI.
            "passwordless": lambda: BlobServiceClient(
                account_url, credential=DefaultAzureCredential()
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
