---
title: SFTP Provider
description: Configure *cshelve* to use SFTP for remote storage.
---

[SFTP (SSH File Transfer Protocol)](https://en.wikipedia.org/wiki/SSH_File_Transfer_Protocol) is a secure file transfer protocol that provides file access, file transfer, and file management over a reliable data stream. *cshelve* can be configured to use SFTP as a provider for storing and retrieving data on remote servers.

## Installation

To install the *cshelve* package with SFTP support, run the following command:

```console
pip install cshelve[sftp]
```

## Configuration Options

The following table lists the configuration options available for the SFTP provider:

| Scope     | Option                     | Description                                              | Default Value | Required |
|-----------|----------------------------|----------------------------------------------------------|--------------|----------|
| `default` | `hostname`                 | SFTP server hostname                                     | -            | Yes      |
| `default` | `port`                     | SFTP server port                                         | 22           | No       |
| `default` | `username`                 | SFTP username                                            | -            | Yes      |
| `default` | `auth_type`                | Authentication method: `password` or `key_filename`      | -            | Yes      |
| `default` | `password`                 | Password for password-based authentication               | -            | For password auth |
| `default` | `key_filename`             | Path to private key file for key-based authentication    | -            | For key auth    |
| `default` | `remote_path`              | Path on the remote server to store data                  | ""           | No       |
| `default` | `accept_unknown_host_keys` | Accept unknown host keys                                 | false        | No       |

## Permissions

The SFTP provider requires appropriate permissions on the remote server:

| Flag | Description                                                       | Permissions Needed                                            |
|------|-------------------------------------------------------------------|--------------------------------------------------------------|
| `r`  | Open existing remote path for read-only access                    | Read                            |
| `w`  | Open existing remote path for read/write access                   | Read and write                 |
| `c`  | Open remote path with read/write access, creating it if necessary | Read, write               |

Note that directory creation permissions are needed when using keys that contain path separators (e.g., `db['folder/file.txt'] = "data"`). In this case, the provider will automatically create the necessary subdirectories in the remote path if they don't exist.

## Authentication Methods

The SFTP provider supports two authentication methods:

### Password Authentication

```console
cat sftp-password.ini
[default]
provider                    = sftp
hostname                    = sftp.example.com
port                        = 22
username                    = user
auth_type                   = password
password                    = mypassword
remote_path                 = /data/cshelve
accept_unknown_host_keys    = false
```

### SSH Key Authentication

```console
cat sftp-key.ini
[default]
provider                    = sftp
hostname                    = sftp.example.com
port                        = 22
username                    = user
auth_type                   = key_filename
key_filename                = /path/to/private_key
remote_path                 = /data/cshelve
accept_unknown_host_keys    = false
```

## Configure the SFTP Client

Behind the scenes, this provider uses the [Paramiko](https://www.paramiko.org/) library for SFTP connectivity. Users can pass specific parameters using the `provider_params` parameter of the `cshelve.open` function.

The following table lists additional configuration parameters that can be passed via `provider_params`:

| Parameter         | Description                             | Default Value |
|-------------------|-----------------------------------------|---------------|
| `timeout`         | Connection timeout in seconds           | 10            |
| `banner_timeout`  | SSH banner timeout in seconds           | 10            |
| `auth_timeout`    | SSH authentication timeout in seconds   | 10            |
| `channel_timeout` | SSH channel timeout in seconds          | 10            |

```python
import cshelve

provider_params = {
    'timeout': 15,                # Connection timeout in seconds
    'banner_timeout': 20,         # SSH banner timeout in seconds
    'auth_timeout': 30,           # SSH authentication timeout in seconds
    'channel_timeout': 40,        # SSH channel timeout in seconds
    'accept_unknown_host_keys': True  # Accept unknown host keys
}

with cshelve.open('sftp.ini', provider_params=provider_params) as db:
    # Use the database
    db['key'] = 'value'
```

## Security Considerations

- For production environments, key-based authentication is generally recommended over password authentication
- The `accept_unknown_host_keys` parameter should be set to `false` in production environments to prevent man-in-the-middle attacks
- Store sensitive information such as passwords or private keys securely, preferably using environment variables or a secrets management system

## Notes

- The SFTP provider will automatically create parent directories as needed when storing data
- Directory deletion is not supported to maintain consistent behavior with other providers
- All operations on the SFTP provider are thread-safe through the use of locks
- The provider supports traversal of the database content, allowing you to iterate through all keys using standard dictionary operations like `keys()`, `items()`, or direct iteration
- Windows-style paths in keys are automatically converted to POSIX-style paths (e.g., `"folder\file.txt"` becomes `"folder/file.txt"`) to ensure compatibility with SFTP servers that expect forward slashes

## Example

```python
import cshelve

# Open the SFTP provider
with cshelve.open('sftp-config.ini') as db:
    # Store hierarchical data
    # If the folder customers/1001 does not exist, it will be created.
    # If permissions are missing, an error will be raised.
    db['customers/1001/name'] = 'John Doe'
    db['customers/1001/email'] = 'john@example.com'


    # Windows-style paths are automatically converted to POSIX-style paths.
    # The following data will be stored in the folder 'customers/1002/'.
    db['customers\\1002\\name'] = 'Jane Smith'
    db['customers\\1002\\email'] = 'jane@example.com'


    # Iterate through all keys
    # The iteration is recursive; the folders 'customers', 'customers/1001', and 'customers/1002' will be explored:
    for key in db:
        print(f"Key: {key}, Value: {db[key]}")
    # Example output:
    # Key: customers/1001/name, Value: John Doe
    # Key: customers/1001/email, Value: john@example.com
    # Key: customers/1002/name, Value: Jane Smith
    # Key: customers/1002/email, Value: jane@example.com
```
