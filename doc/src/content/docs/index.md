---
title: Cloud Shelve
description: What is *cshelve*?
---

**Cloud Shelve (cshelve)** is a Python package that provides a seamless way to store and manage data in the cloud using the familiar [Python Shelve interface](https://docs.python.org/3/library/shelve.html). It is designed for efficient and scalable storage solutions, allowing you to leverage cloud providers for persistent storage while keeping the simplicity of the *shelve* API.

We welcome your feedback, contributions, and support! Feel free to star the project on [GitHub](https://github.com/Standard-Cloud/cshelve).

## Installation

```console
pip install cshelve
```

## Usage

Locally, *cshelve* works just like the built-in *shelve* module:

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

Refer to the [Python official documentation of the Shelve module](https://docs.python.org/3/library/shelve.html) for more information.

### Cloud Storage Example

*cshelve* also supports cloud storage. You can use the same API to store data in the cloud. You just need to install the targeted provider and create an `.ini` file with your configuration.

Here is an example using Azure Blob Storage:

First, install the provider (first time only):

```console
pip install cshelve[azure-blob]
```

Then create a configuration file `my_configuration.ini`:

```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer
```

Finally, specify the configuration file when opening the database:

```python
import cshelve

d = cshelve.open('my_configuration.ini')
```
