# Cloud Shelve
`Cloud Shelve (cshelve)` is a Python package that provides a seamless way to store and manage data in the cloud using the familiar [Python Shelve interface](https://docs.python.org/3/library/shelve.html). It is designed for efficient and scalable storage solutions, allowing you to leverage cloud providers for persistent storage while keeping the simplicity of the `shelve` API.

## Features

- Supports large file storage in the cloud
- Secure data in-transit encryption when using cloud storage
- Fully compatible with Python's `shelve` API
- Cross-platform compatibility for local and remote storage

## Installation

Install `cshelve` via pip:

```bash
pip install cshelve
```

## Usage

The `cshelve` module strictly follows the official `shelve` API. Consequently, you can refer to the [Python official documentation](https://docs.python.org/3/library/shelve.html) for general usage examples. Simply replace the `shelve` import with `cshelve`, and you're good to go.

### Local Storage

Here is an example, adapted from the [official shelve documentation](https://docs.python.org/3/library/shelve.html#example), demonstrating local storage usage. Just replace `shelve` with `cshelve`:

```python
import cshelve

d = cshelve.open('local.db')  # Open the local database file

key = 'key'
data = 'data'

d[key] = data                 # Store data at the key (overwrites existing data)
data = d[key]                 # Retrieve a copy of data (raises KeyError if not found)
del d[key]                    # Delete data at the key (raises KeyError if not found)

flag = key in d               # Check if the key exists in the database
klist = list(d.keys())        # List all existing keys (could be slow for large datasets)

# Note: Since writeback=True is not used, handle data carefully:
d['xx'] = [0, 1, 2]           # Store a list
d['xx'].append(3)             # This won't persist since writeback=True is not used

# Correct approach:
temp = d['xx']                # Extract the stored list
temp.append(5)                # Modify the list
d['xx'] = temp                # Store it back to persist changes

d.close()                     # Close the database
```

### Remote Storage (e.g., Azure)

To configure remote cloud storage, you need to provide an INI file containing your cloud provider's configuration. The file should have a `.ini` extension.

#### Example Azure Configuration

```bash
$ cat azure.ini
[default]
provider        = azure
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

Once the INI file is ready, you can interact with remote storage the same way as with local storage. Here's an example using Azure:

```python
import cshelve

d = cshelve.open('azure.ini')  # Open using the remote storage configuration

key = 'key'
data = 'data'

d[key] = data                  # Store data at the key
data = d[key]                  # Retrieve the data
del d[key]                     # Delete the data

flag = key in d                # Check if the key exists in the cloud store
klist = list(d.keys())         # List all keys in the remote storage

d['xx'] = [0, 1, 2]            # Store a list remotely
d['xx'].append(3)              # Changes to the list won't persist

# Correct approach:
temp = d['xx']                 # Extract the stored list
temp.append(5)                 # Modify the list
d['xx'] = temp                 # Store it back to persist changes

d.close()                      # Close the connection to the remote store
```

More configuration examples for other cloud providers can be found [here](./tests/configurations/).

### Cloud Providers configuration

#### Azure

The Azure provider uses [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) as remote storage.
The module considers the provided container as dedicated to the application. The impact might be significant. For example, if the flag `n` is provided to the `open` function, the entire container will be purged, aligning with the [official interface](https://docs.python.org/3/library/shelve.html#shelve.open).

| Option                           | Description                                                                                                                                                  | Required           | Default Value |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|---------------|
| `account_url`                    | The URL of your Azure storage account.                                                                                                                       | :x:                |               |
| `auth_type`                      | The authentication method to use: `passwordless` or `connection_string`.                                                                               | :white_check_mark:                |               |
| `container_name`                 | The name of the container in your Azure storage account.                                                                                                     | :white_check_mark:                |               |

Depending on the `open` flag, the permissions required by `cshelve` for blob storage vary.

| Flag | Description | Permissions Needed |
|------|-------------|--------------------|
| `r`  | Open an existing blob storage container for reading only. | [Storage Blob Data Reader](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-reader) |
| `w`  | Open an existing blob storage container for reading and writing. | [Storage Blob Data Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor) |
| `c`  | Open a blob storage container for reading and writing, creating it if it doesn't exist. | [Storage Blob Data Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor) |
| `n`  | Purge the blob storage container before using it. | [Storage Blob Data Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor) |


Authentication type supported:

| Auth Type         | Description                                                                                     | Advantage                                                                 | Disadvantage                          | Example Configuration |
|-------------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|---------------------------------------|-----------------------|
| Connection String | Uses a connection string for authentication. Credentials are provided directly in the string.   | Fast startup as no additional credential retrieval is needed.             | Credentials need to be securely managed and provided. | [Example](tests/configurations/azure-integration/connection-string.ini) |
| Passwordless      | Uses passwordless authentication methods such as Managed Identity.                     | Recommended for better security and easier credential management.         | May impact startup time due to the need to retrieve authentication credentials. | [Example](./tests/configurations/azure-integration/standard.ini) |


## Roadmap

- **AWS S3 Support**: Integration for AWS S3 storage is planned in upcoming versions.
- **Google Cloud Storage Support**: Support for Google Cloud Storage is also on the roadmap.

Stay tuned for updates!

## Contributing

We welcome contributions from the community! If you'd like to contribute, please read our [contributing guidelines](CONTRIBUTING.md) for more details on how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions, issues, or feedback, feel free to [open an issue]https://github.com/Standard-Cloud/cshelve/issues).
