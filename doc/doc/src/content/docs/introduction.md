---
title: Introduction
description: Introduction to the *cshelve* Modules.
---

Python's standard library includes various modules designed to simplify data storage and management. Among these, the **shelve** module stands out as an incredibly versatile tool for simple, file-based data persistence.

The **cshelve** module extends the functionality of the standard **shelve** module by adding cloud storage capabilities, allowing seamless switching between local and cloud storage without modifying existing code.

## What is the *shelve* Module?

The **shelve** module allows persistent storage of Python objects using a dictionary-like interface. It creates a disk-backed dictionary where keys are strings, and values can be any serializable Python object.

Unlike complex databases, **shelve** is lightweight, schema-less, and easy to use, making it ideal for quick storage and retrieval tasks.

### Key Features of *shelve*

- **Dictionary-like Interface**: Easy and intuitive.
- **Automatic Serialization**: Stores complex Python objects.
- **Persistent Storage**: Data persists between sessions.
- **Ease of Use**: Minimal setup.

## Basic Usage

Here's a simple usage example:

```python
import shelve

with shelve.open('my_shelve_db') as db:
    db['username'] = 'Alice'
    db['age'] = 30

    print(db['username'])  # Alice
```

## Storing Complex Objects

Complex objects can be stored seamlessly:

```python
import shelve

class User:
    def __init__(self, username, age):
        self.username = username
        self.age = age

with shelve.open('my_shelve_db') as db:
    db['user1'] = User('Bob', 35)
    retrieved_user = db['user1']
    print(retrieved_user.username)  # Output: Bob
```

## What is the *cshelve* Module?

The **cshelve** module enhances **shelve** by adding cloud storage capabilities. It allows seamless switching between local and cloud storage with no code changes required.

### Key Features of *cshelve*

- **Cloud Storage Support**: Azure Blob Storage, AWS S3, and more.
- **Configuration-based**: Uses an `.ini` file to configure providers.
- **Seamless API**: Same API as `shelve`.

## Basic `cshelve` Usage Example

Here's an example using the in-memory provider:

```ini
[default]
provider = in-memory
```

```python
import cshelve

with cshelve.open('in-memory.ini') as db:
    db['data'] = 'Test data'
    print(db['data'])  # Output: Test data
```

## Using Cloud Storage with `cshelve`

### Azure Blob Storage Example

Configuration file:

```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

Usage:

```python
import cshelve

with cshelve.open('azure-blob.ini') as db:
    db['username'] = 'Alice'
    print(db['username'])  # Output: Alice
```

## Using `Pathlib` with `cshelve`

Unlike the standard `shelve`, `cshelve` fully supports `Pathlib`:

```python
from pathlib import Path
import cshelve

with cshelve.open(Path('in-memory.ini')) as db:
    ...
```

## Environment Variables in Configuration

`cshelve` can use environment variables for sensitive configuration values:

```ini
[default]
provider        = azure-blob
account_url     = $ACCOUNT_URL
auth_type       = passwordless
container_name  = $CONTAINER_NAME
```

Environment variables (`ACCOUNT_URL`, `CONTAINER_NAME`) must be set.

## Customizing Provider Parameters

`provider_params` allows passing custom provider-specific parameters:

### Using Python

```python
import cshelve

provider_params = {
    'secondary_hostname': 'https://secondary.blob.core.windows.net',
    'max_block_size': 4 * 1024 * 1024,
    'use_byte_buffer': True
}

with cshelve.open('azure-blob.ini', provider_params=provider_params) as db:
    ...
```

### Using Configuration Files

You can also specify parameters in the `.ini` file:

```ini
[default]
provider        = azure-blob
container_name  = mycontainer

[provider_params]
secondary_hostname = https://secondary.blob.core.windows.net
```

Parameters set in the configuration file override those provided through code.
