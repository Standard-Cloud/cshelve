# CShelve – The Python Dictionary That Lives in the Cloud 🚀

**Store Python objects locally *or* in the cloud with the same, simple dictionary interface.**
CShelve lets you store and retrieve any Python object—lists, DataFrames, JSON, binary files—whether on local files, AWS S3, Azure Blob Storage, or in-memory, all with the same simple dictionary-like interface.

---

## 📌 Why CShelve?

* **Familiar & Fast** – If you know Python dictionaries, you already know CShelve.
* **Cloud-Ready** – Switch between local files and cloud storage (AWS S3, Azure Blob, SFTP) with **zero code changes**.
* **Lightweight** – No database servers, no migrations, no schema headaches and minimals dependencies.
* **Flexible Formats** – Store pickled Python objects by default, or any format as bytes (JSON, CSV, Parquet, images, etc.).
* **Cost-Effective Scaling** – Tap into cheap and durable cloud storage without maintaining infrastructure.

---

## 🔍 What’s “Shelve” Anyway?

Python’s built-in [`shelve`](https://docs.python.org/3/library/shelve.html) module stores Python objects in a file with a dictionary-like API.
**CShelve supercharges it** with:

* Cloud backends
* Multiple authentication methods
* Format flexibility
* Provider-agnostic switching

If you can do:

```python
mydict['key'] = value
```

You can use CShelve—locally, in the cloud, or on-premises.

---

## 📦 Installation

```bash
# Local storage only
pip install cshelve

# With AWS S3 support
pip install cshelve[aws-s3]

# With Azure Blob support
pip install cshelve[azure-blob]
```

---

## ⚡ Quick Start

### Local Storage

```python
import cshelve

db = cshelve.open('local.db')
db['user'] = {'name': 'Alice', 'age': 30}
print(db['user'])  # {'name': 'Alice', 'age': 30}
db.close()
```

### AWS S3

```bash
# Install provider
pip install cshelve[aws-s3]
```

**aws-s3.ini**

```ini
[default]
provider    = aws-s3
bucket_name = mybucket
auth_type   = access_key
key_id      = $AWS_KEY_ID
key_secret  = $AWS_KEY_SECRET
```

**Python**

```python
import cshelve

db = cshelve.open('aws-s3.ini')
db['session'] = 'cloud storage is easy'
print(db['session'])
db.close()
```

### Azure Blob

```bash
# Install provider
pip install cshelve[azure-blob]
```

**azure-blob.ini**

```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

**Python**

```python
import cshelve

db = cshelve.open('azure-blob.ini')
db['analytics'] = [1, 2, 3, 4]
print(db['analytics'])
db.close()
```

---

## 📊 Advanced Examples

### Storing Pandas DataFrames in the Cloud

```python
import cshelve, pandas as pd

df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})

with cshelve.open('azure-blob.ini') as db:
    db['users'] = df

with cshelve.open('azure-blob.ini') as db:
    print(db['users'])
```

### Storing JSON (no pickle)

```python
import json, cshelve

data = {"msg": "Hello, Cloud!"}

with cshelve.open('azure-blob.ini') as db:
    db['config.json'] = json.dumps(data).encode()

with cshelve.open('azure-blob.ini') as db:
    print(json.loads(db['config.json'].decode()))
```

---

## � Multi-Provider Support

**Store data across multiple backends simultaneously for redundancy and performance.**

CShelve supports writing to multiple storage providers at once. Perfect for:
- **Backup strategies** – Primary storage + cloud backup
- **Multi-region deployment** – Replicate across multiple cloud providers

### Using Multiple Providers

Real-world example: Replicate data from Azure Blob Storage to AWS S3 for disaster recovery.

**multi-cloud.ini**

```ini
[default]
providers = azure-primary, aws-backup, local-backup

[azure-primary]
provider        = azure-blob
auth_type       = connection_string
environment_key = AZURE_STORAGE_CONNECTION_STRING
container_name  = standard

[aws-backup]
provider    = aws-s3
bucket_name = cshelve
auth_type   = access_key
key_id      = $AWS_KEY_ID
key_secret  = $AWS_KEY_SECRET

[local-backup]
provider = filesystem
folder_path = /data/cache
```

**Python**

```python
import cshelve

# Write to both Azure AND AWS
with cshelve.open('multi-cloud.ini') as db:
    db['user'] = {'name': 'Alice'}      # Written to both Azure and AWS
    print(db['user'])                   # Read from first provider (Azure)

# Data persists in both clouds
with cshelve.open('multi-cloud.ini') as db:
    print(db['user'])  # Available in both Azure and AWS
```

**Dictionary Format - Multi-Cloud Example**

```python
import cshelve

config = {
    "default": {
        "providers": "aws, azure",
        "strategy": "all",
    },
    "aws": {
        "provider": "aws-s3",
        "bucket_name": "my-bucket",
        "auth_type": "access_key",
        "key_id": "$AWS_ACCESS_KEY_ID",
        "key_secret": "$AWS_SECRET_ACCESS_KEY",
    },
    "azure": {
        "provider": "azure-blob",
        "auth_type": "connection_string",
        "environment_key": "AZURE_STORAGE_CONNECTION_STRING",
        "container_name": "my-container",
    },
}

db = cshelve.open_from_dict(config)
db['key'] = 'value'  # Written to both AWS and Azure
db.close()
```

---

## �🛠 Supported Providers

| Provider   | Install Extra         | Notes                                                                        |
| ---------- | --------------------- | ---------------------------------------------------------------------------- |
| Local      | none                  | Stores data in a local `.db` file                                            |
| AWS S3     | `cshelve[aws-s3]`     | Supports `access_key` auth                                                   |
| Azure Blob | `cshelve[azure-blob]` | Supports `access_key`, `passwordless`, `connection_string`, `anonymous` auth |
| In-Memory  | none                  | Perfect for tests and temporary storage                                      |

[Detailed configuration in the documentation.](https://standard-cloud.github.io/cshelve/)

---

## 🤝 Contributing

We welcome pull requests, feature suggestions, and bug reports.
Check the [issues](https://github.com/Standard-Cloud/cshelve/issues) to get started.

---

## 📄 License

MIT – see [LICENSE](LICENSE)

---

## ⭐ Pro Tip

Switching from **local** to **cloud** to **on-premises** is as easy as:

```python
db = cshelve.open('local.db')
# to
db = cshelve.open('aws-s3.ini')
# to
db = cshelve.open('sftp.ini')
```

**No code rewrite. Just change the config.**
