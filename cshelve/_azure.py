import functools
import io
from typing import Dict

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobType

from ._flag import can_create, can_write
from .cloud_mutable_mapping import CloudMutableMapping
from .exceptions import (
    CanNotCreateDBError,
    DBDoesNotExistsError,
    key_access,
)

LRU_CACHE_MAX_SIZE = 2048


class AzureMutableMapping(CloudMutableMapping):
    def __init__(self) -> None:
        super().__init__()
        self.container_name = None
        self.container_client = None

        cache_fct = functools.partial(self._get_client_cache)
        self._get_client = functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE, typed=False)(
            cache_fct
        )

    def configure(self, flag: str, config: Dict[str, str]) -> None:
        self.flag = flag
        account_url = config.get("account_url")
        # auth_type = config.get('auth_type')
        self.container_name = config.get("container_name")

        self.blob_service_client = BlobServiceClient(
            account_url, credential=DefaultAzureCredential()
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
