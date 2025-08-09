---
title: Cloud Shelve
description: Store and retrieve Python objects locally, in the cloud, or on-premise with a simple dictionary-like interface.
---

# Cloud Shelve (`cshelve`)

**CShelve** is a Python package that lets you store and retrieve Python objects—lists, DataFrames, JSON, binary files—across **local files**, **cloud storage** (AWS S3, Azure Blob), or **on-premise via SFTP**, all with the same easy dictionary-like interface.

If you know how to use:
```python
mydict['key'] = value
````

you already know how to use CShelve.
No database servers. No complex setup. Just install, configure, and start saving.

We welcome your feedback and contributions! ⭐ Star the project on [GitHub](https://github.com/Standard-Cloud/cshelve) to support development.

---

## 🚀 Installation

```bash
# Local storage only
pip install cshelve

# With Azure Blob support
pip install cshelve[azure-blob]

# With AWS S3 support
pip install cshelve[aws-s3]

# With SFTP support (on-premise or self-hosted)
pip install cshelve[sftp]
```

---

## 📝 Local Usage

Using CShelve locally is just like Python’s built-in [`shelve`](https://docs.python.org/3/library/shelve.html):

```python
import cshelve

db = cshelve.open('local.db')  # Create or open a local storage file

db['key'] = 'data'             # Store
print(db['key'])               # Retrieve
del db['key']                  # Delete

print('key' in db)             # Check if a key exists
print(list(db.keys()))         # List all keys (may be slow for huge datasets)

# Example with mutable objects (without writeback=True)
db['numbers'] = [0, 1, 2]
temp = db['numbers']
temp.append(3)
db['numbers'] = temp           # Re-store to persist changes

db.close()
```

> 📚 Tip: For more details on how `shelve` works under the hood, see the [official Python documentation](https://docs.python.org/3/library/shelve.html).

---

## ☁ Cloud Storage Example – Azure Blob

**1️⃣ Install provider**

```bash
pip install cshelve[azure-blob]
```

**2️⃣ Create `azure-blob.ini`**

```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

**3️⃣ Use in Python**

```python
import cshelve

db = cshelve.open('azure-blob.ini')
db['message'] = 'Hello from Azure!'
print(db['message'])
db.close()
```

---

## ☁ Cloud Storage Example – AWS S3

**1️⃣ Install provider**

```bash
pip install cshelve[aws-s3]
```

**2️⃣ Create `aws-s3.ini`**

```ini
[default]
provider    = aws-s3
bucket_name = mybucket
auth_type   = access_key
key_id      = $AWS_KEY_ID
key_secret  = $AWS_KEY_SECRET
```

**3️⃣ Set environment variables**

```bash
export AWS_KEY_ID=your_access_key_id
export AWS_KEY_SECRET=your_secret_access_key
```

**4️⃣ Use in Python**

```python
import cshelve

db = cshelve.open('aws-s3.ini')
db['cloud_key'] = 'Stored in S3!'
print(db['cloud_key'])
db.close()
```

---

## 🖥 On-Premise / Private Hosting Example – SFTP

**1️⃣ Install provider**

```bash
pip install cshelve[sftp]
```

**2️⃣ Create `sftp.ini`**

```ini
[default]
provider                    = sftp
hostname                    = $SFTP_PASSWORD_HOSTNAME
username                    = $SFTP_USERNAME
password                    = $SFTP_PASSWORD
auth_type                   = password

[provider_params]
remote_path                 = myuser
```

**3️⃣ Set environment variables**

```bash
export SFTP_PASSWORD_HOSTNAME=your-sftp-host
export SFTP_USERNAME=your-username
export SFTP_PASSWORD=your-password
```

**4️⃣ Use in Python**

```python
import cshelve

db = cshelve.open('sftp.ini')
db['local_backup'] = 'Stored via SFTP on-prem'
print(db['local_backup'])
db.close()
```

---

## 🌟 Why Use CShelve?

* **Familiar** – Works like a Python dictionary.
* **Cloud-Ready** – Switch between local and cloud storage without code changes.
* **On-Prem Capable** – Use SFTP for private or internal storage.
* **Lightweight** – No servers or SQL required.
* **Flexible** – Store any picklable object or raw bytes (JSON, CSV, images, etc.).
* **Scalable** – Leverage cloud or on-prem solutions for affordable, persistent storage.
