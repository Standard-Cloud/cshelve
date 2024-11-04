"""

"""
import functools
import io
import os
from typing import Dict, Iterator, Optional

from azure.core.exceptions import ResourceNotFoundError

from .provider_interface import ProviderInterface
from .exceptions import (
    AuthTypeError,
    AuthArgumentError,
    key_access,
)


class AzureTable(ProviderInterface):
    """ """

    def __init__(self) -> None:
        super().__init__()
        self.table_name = None
        self.table_client = None

    def configure(self, config: Dict[str, str]) -> None:
        """
        Configure the Azure Blob Storage client based on the configuration file.
        """
        # Retrieve the configuration parameters.
        # The Azure Storage Account URL
        # Ex: https://<account_name>.blob.core.windows.net
        account_url = config.get("account_url")
        # The authentication type to use.
        auth_type = config.get("auth_type")
        # The environment variable key that contains the connection string.
        environment_key = config.get("environment_key")
        # The name of the table to use.
        # It can be created if it does not exist depending on the flag parameter.
        self.table_name = config.get("container_name")

        # Create the TableServiceClient and TableClient objects.
        self.table_service_client = self.__create_table_service(
            auth_type, account_url, environment_key
        )
        self.table_client = self.table_service_client.get_table_client(self.table_name)

    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def get(self, key: bytes) -> bytes:
        """
        Retrieve the value of the specified key.
        """
        # Must be string and not bytes.
        key = key.decode()

        return self.table_client.get_entity(partition_key=key, row_key=key)["data"]

    def close(self) -> None:
        """
        Close the Azure Blob Storage client.
        """
        self.table_client.close()
        self.table_service_client.close()

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
        # Must be string and not bytes.
        key = key.decode()

        # Create the entity to store the data.
        # PartitionKey and RowKey are the same to simplify the query and optimized the sharding.
        entity = {"PartitionKey": key, "RowKey": key, "data": value}

        self.table_client.upsert_entity(entity)

    # If an `ResourceNotFoundError` is raised by the SDK, it is converted to a `KeyError` to follow the `dbm` behavior based on a custom module error.
    @key_access(ResourceNotFoundError)
    def delete(self, key: bytes):
        # Must be string and not bytes.
        key = key.decode()

        # Delete the entity.
        self.table_client.delete_entity(partition_key=key, row_key=key)

    def contains(self, key: bytes) -> bool:
        """
        Return whether the specified key exists in the Azure table.
        """
        try:
            self.get(key)
            return True
        except ResourceNotFoundError:
            return False

    def iter(self) -> Iterator[bytes]:
        """
        Return an iterator over the keys in the Azure Blob Storage container.
        """
        for e in self.table_client.list_entities():
            # Azure Table entities names are strings and not bytes.
            # To respect the Shelf interface, we encode the string to bytes.
            yield e["PartitionKey"].encode()

    def len(self):
        """
        Return the number of objects stored in the database.
        """
        # The Azure SDK does not provide a method to get the number of entities in a table.
        # We iterate over the entites and count them.
        return len(self.iter())

    def exists(self) -> bool:
        """
        Check if the container exists on the Azure Blob Storage account.
        """
        return (
            True
            if self.table_service_client.query_tables(
                f"TableName eq '{self.table_name}'"
            )
            else False
        )

    def create(self):
        """
        Create the container.
        The container must not exist before calling this method.
        """
        self.table_client = self.table_service_client.create_table(self.table_name)

    def __create_table_service(
        self, auth_type: str, account_url: Optional[str], environment_key: Optional[str]
    ):
        # TableServiceClient and DefaultAzureCredential are imported here to avoid importing them in the module scope.
        # This also simplify the mocking of the Azure SDK in the tests even if it remove the typing information.
        from azure.data.tables import TableServiceClient
        from azure.identity import DefaultAzureCredential

        # Create the BlobServiceClient based on the authentication type.
        # A lambda is used to avoid calling the method if the auth_type is not valid.
        supported_auth = {
            "access_key": lambda: TableServiceClient(
                account_url, credential=self.__get_credentials(environment_key)
            ),
            "anonymous": lambda: TableServiceClient(account_url),
            "connection_string": lambda: TableServiceClient.from_connection_string(
                self.__get_credentials(environment_key)
            ),
            "passwordless": lambda: TableServiceClient(
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
