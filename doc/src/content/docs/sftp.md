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
| `default` | `accept_unknown_host_keys` | Accept unknown host keys (`true` or `false`)             | false        | No       |

### Configuration Precedence

When the same parameter is specified in both the configuration file and `provider_params`, the configuration file takes precedence. The only exception is when a parameter is not set in the configuration file (or set to `None`), in which case the value from `provider_params` will be used.

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
    'timeout': 15,                      # Connection timeout in seconds
    'banner_timeout': 20,               # SSH banner timeout in seconds
    'auth_timeout': 30,                 # SSH authentication timeout in seconds
    'channel_timeout': 40,              # SSH channel timeout in seconds
    'accept_unknown_host_keys': True,   # Accept unknown host keys
    'remote_path': '/custom/path'       # Can also be set via provider_params
}

with cshelve.open('sftp.ini', provider_params=provider_params) as db:
    # Use the database
    db['key'] = 'value'
```

## Security Considerations

- For production environments, key-based authentication is generally recommended over password authentication.
- The `accept_unknown_host_keys` parameter should be set to `false` in production environments to prevent man-in-the-middle attacks.
- Store sensitive information such as passwords or private keys securely, preferably using environment variables or a secrets management system.
- Ensure SSH private key files have restrictive permissions (600 or 400).
- Use strong passwords and consider implementing key rotation policies.

## Notes

- **Thread Safety**: The SFTP provider is thread-safe. All operations are protected by locks to prevent concurrent access issues. However, for optimal performance in multi-threaded applications, consider using separate database instances per thread.
- **Directory Creation**: The SFTP provider will automatically create parent directories as needed when storing data. This requires write permissions on the remote server.
- **Directory Deletion**: Directory deletion is not supported to maintain consistent behavior with other providers. Only individual files (keys) can be deleted.
- **Path Handling**:
  - The provider uses POSIX-style paths internally (forward slashes)
  - Windows-style paths in keys are automatically converted to POSIX-style paths (e.g., `"folder\file.txt"` becomes `"folder/file.txt"`)
  - All paths are relative to the configured `remote_path`
- **Iteration Support**: The provider supports traversal of the database content, allowing you to iterate through all keys using standard dictionary operations like `keys()`, `items()`, or direct iteration. Iteration is recursive through all subdirectories.
- **Connection Management**: Connections are established lazily (on first use) and automatically reused for subsequent operations within the same session.

## Troubleshooting

### Common Issues and Solutions

#### Connection Timeout
**Problem**: Connection hangs or times out
**Solution**: Adjust timeout parameters in `provider_params`:
```python
provider_params = {
    'timeout': 30,           # Increase connection timeout
    'banner_timeout': 30,    # Increase banner timeout
    'auth_timeout': 30       # Increase auth timeout
}
```

#### Authentication Failed
**Problem**: `cshelve.AuthError: Authentication failed for SFTP connection`
**Solutions**:
- Verify username and password/key file are correct.
- Ensure the SSH key has proper permissions (600 for private keys).
- Check if the server allows the authentication method you're using.
- Verify the hostname and port are correct.

#### Host Key Verification Failed
**Problem**: Connection refused due to unknown host key.
**Solutions**:
- For development/testing: Set `accept_unknown_host_keys = true`
- For production: Add the server's host key to your known_hosts file.
- Use SSH to connect manually first to accept the host key.

#### Permission Denied
**Problem**: Cannot create directories or write files.
**Solutions**:
- Verify the user has write permissions to the `remote_path`.
- Check if the `remote_path` directory exists and is writable.
- Ensure the user can create subdirectories if using nested keys.

#### Missing Dependencies
**Problem**: `ImportError: The paramiko package is required`
**Solution**: Install the SFTP extra dependency:
```bash
pip install cshelve[sftp]
```

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
