---
title: Azure Storage Account
description: Configure *cshelve* to use Azure Storage Account.
---

Azure Blob Storage is a cloud storage solution for data storage and retrieval that is highly available, secure, durable, and scalable. *cshelve* can be configured to use Azure Blob Storage as a provider for storing and retrieving data.

## Installation

To install the *cshelve* package with Azure Blob support, run the following command:

```console
pip install cshelve[azure-blob]
```

## Configuration Options

The following table lists the configuration options available for the Azure Blob Storage provider:

| Scope     | Option           | Description                                                                                          | Required |
|-----------|------------------|------------------------------------------------------------------------------------------------------|----------|
| `default` | `account_url`    | URL of the Azure Blob Storage account                                                               | No       |
| `default` | `auth_type`      | Authentication method: `access_key`, `connection_string`, `passwordless`, or `anonymous`.            | Yes      |
| `default` | `container_name` | Container name in the Azure storage account                                                         | Yes      |
| `logging` | `http`           | Enable HTTP logging                                                                                  | No       |
| `logging` | `credentials`    | Enable logging for credential operations                                                            | No       |

## Permissions

| Flag | Description                                                       | Permissions Needed                                                                                                                               |
|------|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| `r`  | Open existing container for read-only access.                     | [Storage Blob Data Reader](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-reader)            |
| `w`  | Open existing container for read/write access.                    | [Storage Blob Data Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor) |
| `c`  | Open container with read/write access, creating it if necessary.  | [Storage Blob Data Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor) |

## Logging Configuration

The logging configuration allows enabling HTTP logging for blob storage operations and credential operations. To view logging output, you must configure the logging handler as explained in the [Azure SDK logging documentation](https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging).

### Example: Passwordless Authentication

```console
cat passwordless.ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer

[logging]
http            = true
```

```python
import cshelve
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

with cshelve.open('passwordless.ini') as db:
    ...
```

### Example: Access Key Authentication

```console
cat access-key.ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = access_key
# Environment variables: AZURE_STORAGE_ACCESS_KEY
container_name  = container
key_id          = AZURE_STORAGE_KEY_ID
key_secret      = AZURE_STORAGE_KEY_SECRET
```

### Example: Connection String Authentication

```console
cat connection-string.ini
[default]
provider        = azure-blob
auth_type       = connection_string
environment_key = AZURE_STORAGE_CONNECTION_STRING
container_name  = test-connection-string
```

### Example: Anonymous Authentication

```console
cat anonymous.ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = anonymous
container_name  = public-container
```

## Configure the BlobServiceClient

Behind the scenes, this provider uses the [BlobServiceClient](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient).

```python
import cshelve

provider_params = {
    'secondary_hostname': 'https://secondary.blob.core.windows.net',
    'max_block_size': 4 * 1024 * 1024,  # 4 MB
    'use_byte_buffer': True
}

with cshelve.open('azure-blob.ini', provider_params=provider_params) as db:
    ...
```
