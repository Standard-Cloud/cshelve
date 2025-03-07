# Cloud Shelve (`cshelve`)

`Cloud Shelve (cshelve)` is a Python package that provides a seamless way to store and manage data in the cloud using the familiar [Python Shelve interface](https://docs.python.org/3/library/shelve.html). The `shelve` interface is a simple dictionary-like storage system that persists data in a file-based format using `pickle` by default. However, `cshelve` extends this capability to store data in cloud storage, allowing users to store any data as bytes, including but not limited to JSON and Parquet formats.

## Why Use `cshelve`?

### **Cost-Effective & Scalable**
- `cshelve` allows you to leverage affordable cloud storage solutions (such as AWS S3 and Azure Blob) without managing your own database infrastructure.
- `cshelve` doesn't require a database server, making it easy to scale and manage data storage.

### **Simple & Intuitive Setup**
- No need for complex database configurations—just install, set up an INI configuration file, and start storing data.
- Works like a dictionary: store and retrieve data using familiar key-value operations.

### **Flexible & Interoperable**
- Supports multiple data formats (`pickle` by default), but can handle any other format provided as bytes.
- Compatible with Python's built-in `shelve` API, making migration easy.

## Installation

Install `cshelve` via pip:

```bash
pip install cshelve  # For local testing
pip install cshelve[azure-blob]  # For Azure Blob Storage support
pip install cshelve[aws-s3]  # For AWS S3 support
```

## Usage

The `cshelve` module provides a simple key-value interface for storing data in the cloud. By default, it serializes data using `pickle`, allowing users to store and retrieve Python objects in a dictionary-like manner. However, for interoperability, users can store and retrieve data in any format that can be represented as bytes, such as JSON, Parquet, CSV, or custom binary files.

### Quick Start Example

Here’s a basic example demonstrating how to store and retrieve data using `cshelve` locally:

```python
import cshelve

# Open a local database file
db = cshelve.open('local.db')

# Store data
db['my_key'] = 'my_data'

# Retrieve data
print(db['my_key'])  # Output: my_data

# Close the database
db.close()
```

### Using Cloud Storage (AWS S3, Azure Blob, etc.)

To use remote cloud storage, you need an INI configuration file specifying your cloud provider’s credentials and settings. Additional dependencies are required for each provider.

#### AWS S3 Configuration

[Provider documentation](https://cshelve.readthedocs.io/en/stable/aws-s3.html)

**Step 1: Install the AWS S3 provider**
```bash
pip install cshelve[aws-s3]
```

**Step 2: Create an INI file (e.g., `aws-s3.ini`)**
```ini
[default]
provider    = aws-s3
bucket_name = cshelve
auth_type   = access_key
key_id      = $AWS_KEY_ID
key_secret  = $AWS_KEY_SECRET
```

**Step 3: Set environment variables**
```bash
export AWS_KEY_ID=your_access_key_id
export AWS_KEY_SECRET=your_secret_access_key
```

**Step 4: Store and retrieve data in AWS S3**
```python
import cshelve

db = cshelve.open('aws-s3.ini')
db['my_key'] = 'my_data'
print(db['my_key'])  # Output: my_data
db.close()
```

#### Azure Blob Configuration

[Provider documentation](https://cshelve.readthedocs.io/en/stable/azure-blob.html)

**Step 1: Install the Azure Blob provider**
```bash
pip install cshelve[azure-blob]
```

**Step 2: Create an INI file (e.g., `azure-blob.ini`)**
```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

**Step 3: Store and retrieve data in Azure Blob Storage**
```python
import cshelve

db = cshelve.open('azure-blob.ini')
db['my_key'] = 'my_data'
print(db['my_key'])  # Output: my_data
db.close()
```

## Advanced Usage

### Storing DataFrames in the Cloud

In this advanced example, we will demonstrate how to store and retrieve a Pandas DataFrame using cshelve with Azure Blob Storage.

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

Then run the following code:
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

### Storing Any File Format in Cloud Storage

`cshelve` can store and retrieve any file format that can be represented as bytes, including JSON, Parquet, CSV, or binary files.

**Example: Storing JSON Files**

Update the INI file to use `use_pickle=false` and `use_versionning=false` to store data as bytes:
```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
use_pickle      = false
use_versionning = false
```

Then run the following code:
```python
import json
import cshelve

data = {"number": 42, "text": "Hello, World!"}

with cshelve.open('azure-blob.ini') as db:
    db['my_json_file'] = json.dumps(data).encode()

with cshelve.open('azure-blob.ini') as db:
    my_data = json.loads(db['my_json_file'].decode())

print(my_data)
```

### Providers configuration
#### AWS S3

Provider: `aws-s3`
Installation: `pip install cshelve[aws-s3]`

The AWS S3 provider uses an [AWS S3 Bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) as remote storage.

| Option              | Description                                                                 | Required           | Default Value |
|---------------------|-----------------------------------------------------------------------------|--------------------|---------------|
| `bucket_name`       | The name of the S3 bucket.                                                  | :white_check_mark: |               |
| `auth_type`         | The authentication method to use: `access_key`.                             | :white_check_mark: |               |
| `key_id`   | The environment variable for the AWS access key ID.                         | :white_check_mark: |               |
| `key_secret`| The environment variable for the AWS secret access key.                     | :white_check_mark: |               |

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

We welcome contributions from the community! Check out our [issues](https://github.com/Standard-Cloud/cshelve/issues) for ways to get involved.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions, issues, or feedback, feel free to [open an issue](https://github.com/Standard-Cloud/cshelve/issues).
