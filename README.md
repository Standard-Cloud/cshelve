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

## Contributing

We welcome contributions from the community! Check out our [issues](https://github.com/Standard-Cloud/cshelve/issues) for ways to get involved.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions, issues, or feedback, feel free to [open an issue](https://github.com/Standard-Cloud/cshelve/issues).
