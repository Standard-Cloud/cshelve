"""
Azure Mutable Mapping Module

This module provides an implementation of the CloudMutableMapping interface based on Azure Blob Storage.

This module uses an Azure container to store key/value data in blobs.
It creates a blob for each key/value pair, where the key is the blob name and the value is the blob content.
Operations such as iteration and length are performed using the container API.
"""
import functools
import io
import os
from typing import Dict, Iterator, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobType

from ._flag import can_create, can_write
from .cloud_mutable_mapping import CloudMutableMapping
from .exceptions import (
    AuthTypeError,
    CanNotCreateDBError,
    DBDoesNotExistsError,
    AuthArgumentError,
    key_access,
)

# Max size of the LRU cache for the blob clients.
# Blob clients are cached to avoid creating a new client for each operation.
LRU_CACHE_MAX_SIZE = 2048


class AzureMutableMapping(CloudMutableMapping):
    """
    Azure implementation of the MutableMapping interface used by the Shelf module.
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

    def configure(self, flag: str, config: Dict[str, str]) -> None:
        """
        Configure the Azure Blob Storage client based on the configuration file.
        """
        # The flag parameter is used to verify permissions but is not directly utilized by this class.
        self.flag = flag

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

        # Create the BlobServiceClient and ContainerClient objects.
        self.blob_service_client = self.__create_blob_service(
            account_url, auth_type, environment_key
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        # Create container if not exists and it is configured or if the flag allow it.
        if not self.__container_exists():
            if can_create(flag):
                self.__create_container_if_not_exists()
            else:
                raise DBDoesNotExistsError(
                    f"Can't create database: {self.container_name}"
                )

    def __create_blob_service(
        self, account_url: str, auth_type: str, environment_key: Optional[str]
    ) -> BlobServiceClient:
        if auth_type == "connection_string":
            if environment_key is None:
                raise AuthArgumentError(f"Missing environment_key parameter")
            if connect_str := os.environ.get(environment_key):
                return BlobServiceClient.from_connection_string(connect_str)
            raise AuthArgumentError(f"Missing environment variable: {environment_key}")
        elif auth_type == "passwordless":
            return BlobServiceClient(account_url, credential=DefaultAzureCredential())
        raise AuthTypeError(f"Invalid auth_type: {auth_type}")

    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def __getitem__(self, key: bytes) -> bytes:
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

    # Write permission is required to perform this operation.
    @can_write
    def __setitem__(self, key, value):
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

    # Write permission is required to perform this operation.
    @can_write
    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def __delitem__(self, key):
        # Azure Blob Storage must be string and not bytes.
        key = key.decode()

        # Retrieve the blob client.
        client = self._get_client(key)

        # Delete the blob.
        # The retry pattern and error handling is done by the Azure SDK.
        client.delete_blob()

    def __contains__(self, key) -> bool:
        """
        Return whether the specified key exists on the Azure Blob Storage container.
        """
        # Azure Blob Storage must be string and not bytes.
        return self._get_client(key.decode()).exists()

    def __iter__(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the Azure Blob Storage container.
        """
        for i in self.container_client.list_blob_names():
            # Azure blob names are strings and not bytes.
            # To respect the Shelf interface, we encode the string to bytes.
            yield i.encode()

    def __len__(self):
        """
        Return the number of objects stored in the database.
        """
        # The Azure SDK does not provide a method to get the number of blobs in a container.
        # We iterate over the blobs and count them.
        return sum(1 for _ in self.container_client.list_blob_names())

    def _get_client_cache(self, key):
        """
        Cache the blob clients to avoid creating a new client for each operation.
        Size of this object from getsizeof: 48 bytes
        """
        return self.blob_service_client.get_blob_client(self.container_name, key)

    def __container_exists(self) -> bool:
        """
        Check if the container exists on the Azure Blob Storage account.
        """
        return self.blob_service_client.get_container_client(
            self.container_name
        ).exists()

    @can_write
    def __create_container_if_not_exists(self):
        """
        Create the container.
        The container must not exist before calling this method.
        """
        try:
            self.blob_service_client.create_container(self.container_name)
        except Exception as e:
            raise CanNotCreateDBError(
                f"Can't create database: {self.container_name}"
            ) from e
