---
title: Configure CShelve from a Python dictionary
description: Use cshelve.open_from_dict() to configure providers without .ini files—perfect for serverless, CI/CD, or dynamic configs.
---

# Configure from a Python dictionary

`open_from_dict()` lets you pass configuration **directly as a Python dictionary** instead of a `.ini` file.
This is ideal when you generate settings at runtime, pull secrets from a vault, or run in environments where writing to disk is inconvenient.

---

## Why use a dict?

- **No temp files** – Great for serverless or read-only filesystems.
- **Dynamic config** – Build settings from environment variables or secret managers.
- **Same structure** – Mirrors the `.ini` format, so examples are easy to translate.

---

## Quick start

```python
import os
import cshelve

config = {
    "default": {
        "provider": "azure-blob",
        "auth_type": "passwordless",
        "account_url": "https://<account>.blob.core.windows.net"
        "container_name": "standard"
    },
}

with cshelve.open_from_dict(config) as db:
    db["hello"] = "world"
    print(db["hello"])
````

---

## API

```python
cshelve.open_from_dict(config: dict, *args, **kwargs)
```

* **`config`** – A dictionary mirroring the `.ini` structure (sections + key/value pairs).
* **`*args`, `**kwargs`** – Same flags and options supported by `cshelve.open()`.

---

## Provider examples

### Azure Blob (passwordless)

```python
config = {
    "default": {
        "provider": "azure-blob",
        "auth_type": "passwordless",
        "account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "mycontainer",
    }
}

with cshelve.open_from_dict(config) as db:
    db["key"] = "value"
```

### Azure Blob (connection string)

```python
import os

config = {
    "default": {
        "provider": "azure-blob",
        "auth_type": "connection_string",
        "environment_key": "AZURE_STORAGE_CONNECTION_STRING",
        "container_name": "standard",
    },
    "logging": {"http": True, "credentials": False, "level": "INFO"},
}

os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "<your-conn-string>"

with cshelve.open_from_dict(config) as db:
    db["config_type"] = "dict"
```

### AWS S3 (access key)

```python
import os

config = {
    "default": {
        "provider": "aws-s3",
        "auth_type": "access_key",
        "bucket_name": "mybucket",
        "key_id": "$AWS_KEY_ID",
        "key_secret": "$AWS_KEY_SECRET",
    }
}

os.environ["AWS_KEY_ID"] = "AKIA...snip..."
os.environ["AWS_KEY_SECRET"] = "secret...snip..."

with cshelve.open_from_dict(config) as db:
    db["cloud_key"] = "Stored in S3!"
```

### SFTP (on-prem / self-hosted)

```python
import os

config = {
    "default": {
        "provider": "sftp",
        "hostname": "$SFTP_PASSWORD_HOSTNAME",
        "username": "$SFTP_USERNAME",
        "password": "$SFTP_PASSWORD",
        "auth_type": "password",
    },
    "provider_params": {
        "remote_path": "myuser"
    }
}

os.environ.update({
    "SFTP_PASSWORD_HOSTNAME": "sftp.example.com",
    "SFTP_USERNAME": "myuser",
    "SFTP_PASSWORD": "mypassword",
})

with cshelve.open_from_dict(config) as db:
    db["local_backup"] = "Stored via SFTP"
```
