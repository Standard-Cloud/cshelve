# Cloud Shelve
`Cloud Shelve (cshelve)` is a Python package that provides a seamless way to store and manage data in the cloud using the familiar [Python Shelve interface](https://docs.python.org/3/library/shelve.html). It is designed for efficient and scalable storage solutions, allowing you to leverage cloud providers for persistent storage while keeping the simplicity of the `shelve` API.

## Installation

Install `cshelve` via pip:

```bash
pip install cshelve # For testing purposes
pip install cshelve[azure-blob]  # For Azure Blob Storage
```

## Usage

The `cshelve` module provides a simple key-value interface for storing data in the cloud.

### Quick Start Example

Here is a quick example demonstrating how to store and retrieve data using `cshelve`:

```python
import cshelve

# Open a local database file
d = cshelve.open('local.db')

# Store data
d['my_key'] = 'my_data'

# Retrieve data
print(d['my_key'])  # Output: my_data

# Close the database
d.close()
```

### Cloud Storage Example (e.g., AWS, Azure)

To configure remote cloud storage, you need to provide an INI file containing your cloud provider's configuration. The file should have a `.ini` extension. Remote storage also requires the installation of optional dependencies for the cloud provider you want to use.

#### Example AWS S3 Configuration

First, install the AWS S3 provider:
```bash
pip install cshelve[aws-s3]
```

Then, create an INI file with the following configuration:
```bash
$ cat aws-s3.ini
[default]
provider            = aws-s3
bucket_name         = cshelve
auth_type           = access_key
environment_key     = $AWS_KEY_ID
environment_secret  = $AWS_KEY_SECRET
```

Next, export the environment variables:
```bash
export AWS_KEY_ID=your_access_key_id
export AWS_KEY_SECRET=your_secret_access_key
```

Once the INI file is ready, you can interact with remote storage the same way as with local storage. Here's an example using AWS:

```python
import cshelve

# Open using the remote storage configuration
d = cshelve.open('aws-s3.ini')

# Store data
d['my_key'] = 'my_data'

# Retrieve data
print(d['my_key'])  # Output: my_data

# Close the connection to the remote storage
d.close()
```

#### Example Azure Blob Configuration

First, install the Azure Blob Storage provider:
```bash
pip install cshelve[azure-blob]
```

Then, create an INI file with the following configuration:
```bash
$ cat azure-blob.ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

Once the INI file is ready, you can interact with remote storage the same way as with local storage. Here's an example using Azure:

```python
import cshelve

# Open using the remote storage configuration
d = cshelve.open('azure-blob.ini')

# Store data
d['my_key'] = 'my_data'

# Retrieve data
print(d['my_key'])  # Output: my_data

# Close the connection to the remote storage
d.close()
```

### Advanced Scenario: Storing DataFrames in the Cloud

In this advanced example, we will demonstrate how to store and retrieve a Pandas DataFrame using `cshelve` with Azure Blob Storage.

First, install the required dependencies:
```bash
pip install cshelve[azure-blob] pandas
```

Create an INI file with the Azure Blob Storage configuration:
```bash
$ cat azure-blob.ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

Here's the code to store and retrieve a DataFrame:

```python
import cshelve
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
})

# Open the remote storage using the Azure Blob configuration
with cshelve.open('azure-blob.ini') as db:
    # Store the DataFrame
    db['my_dataframe'] = df

# Retrieve the DataFrame
with cshelve.open('azure-blob.ini') as db:
    retrieved_df = db['my_dataframe']

print(retrieved_df)
```

More configuration examples for other cloud providers can be found [here](./tests/configurations/).

### Providers configuration
#### AWS S3

Provider: `aws-s3`
Installation: `pip install cshelve[aws-s3]`

The AWS S3 provider uses an [AWS S3 Bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) as remote storage.

| Option              | Description                                                                 | Required           | Default Value |
|---------------------|-----------------------------------------------------------------------------|--------------------|---------------|
| `bucket_name`       | The name of the S3 bucket.                                                  | :white_check_mark: |               |
| `auth_type`         | The authentication method to use: `access_key`.                             | :white_check_mark: |               |
| `environment_key`   | The environment variable for the AWS access key ID.                         | :white_check_mark: |               |
| `environment_secret`| The environment variable for the AWS secret access key.                     | :white_check_mark: |               |

Depending on the `open` flag, the permissions required by `cshelve` for S3 storage vary.

| Flag | Description | Permissions Needed |
|------|-------------|--------------------|
| `r`  | Open an existing S3 bucket for reading only. | [AmazonS3ReadOnlyAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3ReadOnlyAccess.html) |
| `w`  | Open an existing S3 bucket for reading and writing. | [AmazonS3ReadAndWriteAccess](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html) |
| `c`  | Open an S3 bucket for reading and writing, creating it if it doesn't exist. | [AmazonS3FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html) |
| `n`  | Purge the S3 bucket before using it. | [AmazonS3FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html) |

#### Azure Blob

Provider: `azure-blob`
Installation: `pip install cshelve[azure-blob]`

The Azure provider uses [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) as remote storage.
The module considers the provided container as dedicated to the application. The impact might be significant. For example, if the flag `n` is provided to the `open` function, the entire container will be purged, aligning with the [official interface](https://docs.python.org/3/library/shelve.html#shelve.open).

| Option                           | Description                                                                                                                                                  | Required           | Default Value |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|---------------|
| `account_url`                    | The URL of your Azure storage account.                                                                                                                       | :x:                |               |
| `auth_type`                      | The authentication method to use: `access_key`, `passwordless`, `connection_string` or `anonymous`.                                                                               | :white_check_mark:                |               |
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
| Access Key       | Uses an Access Key or a Shared Access Signature for authentication. | Fast startup as no additional credential retrieval is needed. | Credentials need to be securely managed and provided. | [Example](./tests/configurations/azure-integration/access-key.ini) |
| Anonymous         | No authentication for anonymous access on public blob storage. | No configuration or credentials needed. | Read-only access. | [Example](./tests/configurations/azure-integration/anonymous.ini) |
| Connection String | Uses a connection string for authentication. Credentials are provided directly in the string. | Fast startup as no additional credential retrieval is needed. | Credentials need to be securely managed and provided. | [Example](./tests/configurations/azure-integration/connection-string.ini) |
| Passwordless      | Uses passwordless authentication methods such as Managed Identity. | Recommended for better security and easier credential management. | May impact startup time due to the need to retrieve authentication credentials. | [Example](./tests/configurations/azure-integration/standard.ini) |

#### In Memory

Provider: `in-memory`
Installation: No additional installation required.

The In-Memory provider uses an in-memory data structure to simulate storage. This is useful for testing and development purposes.

| Option         | Description                                                                  | Required | Default Value |
|----------------|------------------------------------------------------------------------------|----------|---------------|
| `persist-key`  | If set, its value will be conserved and reused during the program execution. | :x:      | None          |
| `exists`       | If True, the database exists; otherwise, it will be created.                 | :x:      | False         |

## Contributing

We welcome contributions from the community! Have a look at our [issues](https://github.com/Standard-Cloud/cshelve/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions, issues, or feedback, feel free to [open an issue](https://github.com/Standard-Cloud/cshelve/issues).
