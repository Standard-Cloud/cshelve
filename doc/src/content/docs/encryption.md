---
title: Encryption
description: Configure encryption for *cshelve*.
---

The `cshelve` module supports encryption to secure stored data. Encryption reduces data visibility, improving security for sensitive information.

**Note:** Encryption may impact performance.

## Installation

Encryption functionality is not included by default. Install the additional dependencies to enable encryption:

```console
pip install cshelve[encryption]
```

## Configuration File

Encryption settings are defined in an INI configuration file. Here's an example configuration:

```ini
[default]
provider        = in-memory

[encryption]
algorithm   = aes256
key         = Sixteen byte key
```

In this example, the encryption algorithm is set to `aes256`, and the encryption key is defined as `Sixteen byte key`.

## Using Environment Variables for Keys

For improved security, avoid storing encryption keys directly in configuration files. Instead, use environment variables:

```ini
[default]
provider        = in-memory

[encryption]
algorithm       = aes256
environment_key = ENCRYPTION_KEY
```

In this case, the encryption key is retrieved from the environment variable `ENCRYPTION_KEY`.

## Supported Algorithms

Currently, `cshelve` supports the following encryption algorithm:

- `aes256`: Advanced Encryption Standard with a 256-bit key.

## Example Usage

Encryption works transparently. Your application code doesn't need to change:

```python
import cshelve

with cshelve.open('config.ini') as db:
    db['data'] = 'This is some data that will be encrypted.'

with cshelve.open('config.ini') as db:
    data = db['data']
    print(data)  # Output: This is some data that will be encrypted.
```

## Error Handling

`cshelve` raises specific errors related to encryption:

- `UnknownEncryptionAlgorithmError`: If an unsupported algorithm is specified.
- `MissingEncryptionKeyError`: If no encryption key is provided.
- `EncryptedDataCorruptionError`: If the encrypted data is corrupted.

Ensure the encryption algorithm and key are correctly specified in the configuration.
