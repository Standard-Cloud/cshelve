---
title: Getting Started
description: Getting Started with *cshelve*.
---

Because *cshelve* follows the *shelve* interface, the best way to start with *cshelve* is by understanding the [*shelve* module](https://docs.python.org/3/library/shelve.html).

## Installation

First, install the core *cshelve* package:

```console
$ pip install cshelve
```

By default, only an in-memory provider is included, which is useful for testing but not suitable for production. To install a specific provider, such as Azure Blob Storage, use:

```console
$ pip install cshelve[azure-blob]
```

## Basic Usage

*cshelve* works similarly to a dictionary and can store data in various storage providers:

```python
import cshelve

# Using a context manager
with cshelve.open('config.ini') as db:
    db['user_info'] = {'name': 'Alice', 'age': 28}

# Without a context manager (ensure you close the database!)
db = cshelve.open('config.ini')
db['key'] = 'value'
db.close()
```

### Retrieving Data

```python
with cshelve.open('config.ini') as db:
    username = db['username']
    print(username)  # Output: Alice
```

Attempting to retrieve a non-existent key will raise a `KeyError`.

### Updating Data

Be cautious with complex objects—modifying them directly won't persist unless `writeback=True` is used.

**Without `writeback=True`:**

```python
with cshelve.open('config.ini') as db:
    db['ages'] = [21, 42, 84]
    temp = db['ages']
    temp.append(168)
    db['ages'] = temp  # explicitly save changes
```

**With `writeback=True`:**

```python
with cshelve.open('config.ini', writeback=True) as db:
    db['ages'] = [21, 42, 84]
    db['ages'].append(168)  # Automatically persists

with cshelve.open('config.ini') as db:
    print(db['ages'])  # Output: [21, 42, 84, 168]
```

### Deleting Data

```python
with cshelve.open('config.ini') as db:
    db['name'] = 'Alice'
    del db['name']  # Delete key-value pair
    assert 'name' not in db
```

Attempting to access deleted keys raises a `KeyError`.

### Storing Custom Objects

You can store and retrieve complex objects easily:

```python
class User:
    def __init__(self, username, age):
        self.username = username
        self.age = age

with cshelve.open('conf.ini') as db:
    db['user1'] = User('Bob', 35)

with cshelve.open('conf.ini') as db:
    user1 = db['user1']
    print(user1.username)  # Output: Bob
```

Note that updating attributes of custom objects directly won't persist unless using `writeback=True` or explicitly saving changes.

```python
with cshelve.open('conf.ini') as db:
    user1 = db['user1']
    user1.age = 40
    db['user1'] = user1  # Explicitly persist changes
```

## Closing the Database

Always ensure the database is closed to persist changes. Using a context manager (`with` statement) is recommended:

```python
with cshelve.open('conf.ini') as db:
    db['key'] = 'value'  # Automatically closed and saved

# Without context manager
db = cshelve.open('conf.ini')
db['key'] = 'value'
db.close()
```
