from unittest.mock import patch, Mock
import pytest
from azure.storage.blob import BlobType

from cshelve._factory import factory
from azure.core.exceptions import ResourceNotFoundError
from cshelve import AuthArgumentError, AuthTypeError, KeyNotFoundError


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_passwordless(BlobServiceClient, DefaultAzureCredential):
    """
    Test the Azure Blob Storage client with the passwordless authentication.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": "container",
    }
    identity = Mock()
    DefaultAzureCredential.return_value = identity

    provider = factory("azure-blob")
    provider.configure(config)

    DefaultAzureCredential.assert_called_once()
    BlobServiceClient.assert_called_once_with(
        config["account_url"],
        credential=identity,
    )


@patch("azure.storage.blob.BlobServiceClient")
def test_anonymous_public_read_access(BlobServiceClient):
    """
    Ensure the capability of accessing an Azure Blob Storage client with the anonymous public read access authentication.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "anonymous",
        "container_name": "container",
    }

    provider = factory("azure-blob")
    provider.configure(config)

    BlobServiceClient.assert_called_once_with(config["account_url"])


@patch("azure.storage.blob.BlobServiceClient")
def test_connection_string(BlobServiceClient):
    """
    Test the Azure Blob Storage client with the connection string authentication.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "connection_string",
        "environment_key": "ENV_VAR",
        "container_name": "container",
    }
    connection_string = "my_connection_string"

    with patch.dict("os.environ", {"ENV_VAR": connection_string}):
        provider = factory("azure-blob")
        provider.configure(config)

    BlobServiceClient.from_connection_string.assert_called_once_with(connection_string)


def test_missing_connection_string_value():
    """
    Test the Azure Blob Storage client with the connection string authentication without providing the
    connection string in the environment variable.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "connection_string",
        "environment_key": "ENV_VAR",
        "container_name": "container",
    }

    with pytest.raises(AuthArgumentError):
        provider = factory("azure-blob")
        provider.configure(config)


def test_wrong_auth_type():
    """
    Ensure an AuthTypeError is raised when the authentication type is not supported.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "unknonwn",
    }

    with pytest.raises(AuthTypeError):
        provider = factory("azure-blob")
        provider.configure(config)


def test_missing_connection_string_env_var():
    """
    Test the Azure Blob Storage client with the connection string authentication without the env variable
    key in the configuration.
    """
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "connection_string",
        "container_name": "container",
    }

    with pytest.raises(AuthArgumentError):
        provider = factory("azure-blob")
        provider.configure(config)


@patch("io.BytesIO")
@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_get(BlobServiceClient, DefaultAzureCredential, BytesIO):
    """
    Ensure we can retrieve a value from an Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    key, value = b"key", b"value"

    blob_client = Mock()
    blob_service_client = Mock()
    download_blob = Mock()
    stream = Mock()

    BytesIO.return_value = stream
    DefaultAzureCredential.return_value = Mock()
    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_blob_client.return_value = blob_client
    blob_client.download_blob.return_value = download_blob

    provider = factory("azure-blob")
    provider.configure(config)

    provider.get(key)

    # Blob is retrieved from the container.
    blob_service_client.get_blob_client.assert_called_once_with(
        container_name, key.decode()
    )
    # Create the blob content stream.
    blob_client.download_blob.assert_called_once()
    # Blob content is read into the stream.
    download_blob.readinto.assert_called_once()
    # Stream content is returned.
    stream.getvalue.assert_called_once()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_get_key_error(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure a key error is raised when the blob is not found in the Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    key = b"doesnt-exists"

    blob_client = Mock()
    blob_service_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_blob_client.return_value = blob_client
    blob_client.download_blob.side_effect = ResourceNotFoundError

    provider = factory("azure-blob")
    provider.configure(config)

    with pytest.raises(KeyNotFoundError):
        provider.get(key)


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_set(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure we can set a value to a Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    key, value = b"key", b"value"

    blob_client = Mock()
    blob_service_client = Mock()
    upload_blob = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_blob_client.return_value = blob_client
    blob_client.upload_blob.return_value = upload_blob

    provider = factory("azure-blob")
    provider.configure(config)

    provider.set(key, value)

    # Blob is retrieved from the container.
    blob_service_client.get_blob_client.assert_called_once_with(
        container_name, key.decode()
    )
    # Upload the blob content.
    blob_client.upload_blob.assert_called_once_with(
        value,
        blob_type=BlobType.BLOCKBLOB,
        overwrite=True,
        length=len(value),
    )


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_close(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the close method is called on the Azure Blob Storage client.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }

    blob_service_client = Mock()
    container_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_container_client.return_value = container_client

    provider = factory("azure-blob")
    provider.configure(config)
    provider.close()

    container_client.close.assert_called_once()
    blob_service_client.close.assert_called_once()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_delete(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the delete method is called on the Azure Blob Storage client.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    key = b"key"

    blob_client = Mock()
    blob_service_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_blob_client.return_value = blob_client

    provider = factory("azure-blob")
    provider.configure(config)

    provider.delete(key)

    # Blob is retrieved from the container.
    blob_service_client.get_blob_client.assert_called_once_with(
        container_name, key.decode()
    )
    # Blob is deleted.
    blob_client.delete_blob.assert_called_once()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_iter(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the list of key is correctly returned from the Azure Blob Storage during iteration.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    list_blob_names = ["key1", "key2"]
    list_blob_names_attended = [b"key1", b"key2"]

    blob_service_client = Mock()
    container_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_container_client.return_value = container_client
    container_client.list_blob_names.return_value = list_blob_names

    provider = factory("azure-blob")
    provider.configure(config)

    assert list(provider.iter()) == list_blob_names_attended


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_contains(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the contains correctly check if the blob exists on the Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    key = b"key"

    blob_client = Mock()
    blob_service_client = Mock()
    upload_blob = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_blob_client.return_value = blob_client

    provider = factory("azure-blob")
    provider.configure(config)

    provider.contains(key)

    # Blob is retrieved from the container.
    blob_service_client.get_blob_client.assert_called_once_with(
        container_name, key.decode()
    )
    # Ensure the exists method is called.
    blob_client.exists.assert_called_once()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_len(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the cacul of the number of keys is correctly returned from the Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }
    list_blob_names = ["key1", "key2"]

    blob_service_client = Mock()
    container_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_container_client.return_value = container_client
    container_client.list_blob_names.return_value = list_blob_names

    provider = factory("azure-blob")
    provider.configure(config)

    assert 2 == provider.len()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_exists(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the exists method is correctly called from the Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }

    blob_service_client = Mock()
    container_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client
    blob_service_client.get_container_client.return_value = container_client

    provider = factory("azure-blob")
    provider.configure(config)
    provider.exists()

    container_client.exists.assert_called_once()


@patch("azure.identity.DefaultAzureCredential")
@patch("azure.storage.blob.BlobServiceClient")
def test_create(BlobServiceClient, DefaultAzureCredential):
    """
    Ensure the create method on a container is correctly called from the Azure Blob Storage.
    """
    container_name = "container"
    config = {
        "account_url": "https://account.blob.core.windows.net",
        "auth_type": "passwordless",
        "container_name": container_name,
    }

    blob_service_client = Mock()
    DefaultAzureCredential.return_value = Mock()

    BlobServiceClient.return_value = blob_service_client

    provider = factory("azure-blob")
    provider.configure(config)
    provider.create()

    blob_service_client.create_container.assert_called_once_with(container_name)
