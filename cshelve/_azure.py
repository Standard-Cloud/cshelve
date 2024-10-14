import functools
import io
from typing import Dict

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobType

from .cloud_mutable_mapping import CloudMutableMapping

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

    def configure(self, config: Dict[str, str]) -> None:
        account_url = config.get("account_url")
        # auth_type = config.get('auth_type')
        self.container_name = config.get("container_name")

        self.blob_service_client = BlobServiceClient(
            account_url, credential=DefaultAzureCredential()
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        if config.get("create_container_if_not_exists", "False").lower() == "true":
            self.__create_container_if_not_exists()

    def __getitem__(self, key: bytes):
        key = key.decode()
        stream = io.BytesIO()

        client = self._get_client(key)

        try:
            client.download_blob().readinto(stream)
            return stream.getvalue()
        except ResourceNotFoundError:
            raise KeyError(f"Key not found: {key}")

    def __setitem__(self, key, value):
        key = key.decode()

        client = self._get_client(key)

        return client.upload_blob(
            value, blob_type=BlobType.BLOCKBLOB, overwrite=True, length=len(value)
        )

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
        return len(list(self.container_client.list_blob_names()))

    def _get_client_cache(self, key):
        # 48 bytes from getsizeof
        return self.blob_service_client.get_blob_client(self.container_name, key)

    def __create_container_if_not_exists(self):
        try:
            self.blob_service_client.create_container(self.container_name)
        except Exception as e:
            # Already exists or no permission.
            ...
