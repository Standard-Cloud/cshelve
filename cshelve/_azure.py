"""
Azure Mutable Mapping Module

This module provides an implementation of the CloudMutableMapping interface for Azure Blob Storage.
It allows for the configuration and interaction with Azure Blob Storage containers, enabling
CRUD operations on blobs within the specified container.

This module uses an Azure Container to store key/value data in blobs.
It creates a blob for each key/value pair, where the key is the blob name and the value is the blob content.
Operations as iteration and length are done using the container API.
"""
import functools
import io
import os
from typing import Dict, Optional

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
        self.flag = flag
        account_url = config.get("account_url")
        auth_type = config.get("auth_type")
        connection_string = config.get("connection_string_key")
        self.container_name = config.get("container_name")

        self.blob_service_client = self.__create_blob_service(
            account_url, auth_type, connection_string
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
        self, account_url: str, auth_type: str, connection_string: Optional[str]
    ) -> BlobServiceClient:
        if auth_type == "connection_string":
            if connection_string is None:
                raise AuthArgumentError(f"Missing connection_string")
            if connect_str := os.environ.get(connection_string):
                return BlobServiceClient.from_connection_string(connect_str)
            raise AuthArgumentError(
                f"Missing environment variable: {connection_string}"
            )
        elif auth_type == "passwordless":
            return BlobServiceClient(account_url, credential=DefaultAzureCredential())
        raise AuthTypeError(f"Invalid auth_type: {auth_type}")

    @key_access(ResourceNotFoundError)
    def __getitem__(self, key: bytes):
        key = key.decode()
        stream = io.BytesIO()

        client = self._get_client(key)

        client.download_blob().readinto(stream)
        return stream.getvalue()

    @can_write
    def __setitem__(self, key, value):
        key = key.decode()

        client = self._get_client(key)

        return client.upload_blob(
            value, blob_type=BlobType.BLOCKBLOB, overwrite=True, length=len(value)
        )

    @can_write
    @key_access(ResourceNotFoundError)
    def __delitem__(self, key):
        key = key.decode()

        client = self._get_client(key)

        client.delete_blob()

    def __contains__(self, key) -> bool:
        return self._get_client(key.decode()).exists()

    def __iter__(self):
        for i in self.container_client.list_blob_names():
            yield i.encode()

    def __len__(self):
        return sum(1 for _ in self.container_client.list_blob_names())

    def _get_client_cache(self, key):
        # Size of this object from getsizeof: 48 bytes
        return self.blob_service_client.get_blob_client(self.container_name, key)

    def __container_exists(self) -> bool:
        return self.blob_service_client.get_container_client(
            self.container_name
        ).exists()

    @can_write
    def __create_container_if_not_exists(self):
        try:
            self.blob_service_client.create_container(self.container_name)
        except Exception as e:
            raise CanNotCreateDBError(
                f"Can't create database: {self.container_name}"
            ) from e
