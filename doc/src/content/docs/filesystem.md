---
title: Filesystem Provider
description: Configure *cshelve* to store keys as regular files on the local filesystem.
---

The **filesystem provider** stores each key as a file inside a chosen folder.

## Installation

No extra dependencies are required beyond `cshelve` itself:

```console
pip install cshelve
```

## Configuration Options

| Scope     | Option        | Description                                                                                 | Default Value | Required |
|-----------|---------------|---------------------------------------------------------------------------------------------|---------------|----------|
| `default` | `folder_path` | Root folder where keys are stored. Absolute paths are used as-is. | `.`           | No      |
| `default` | `encoding`    | Text encoding used to decode key bytes into path segments.                                  | `utf-8`       | No       |

## Behavior and Notes

- **Creation (`create`)**: Creates `folder_path` (and parents) if it does not exist. If the folder already exists, `create()` is a no-op. If a non-directory exists at that path, a `ConfigurationError` is raised.
- **Delete semantics**: `delete()` removes only the file for the key and intentionally leaves any empty parent directories. This avoids extra parsing and plays better with concurrent access.
- **Iteration/len**: Recursively walks the root folder and yields keys with POSIX separators (`/`).
- **Encoding**: Keep `encoding` consistent between writers and readers. Use a compatible encoding (e.g., `utf-8`, `utf-16`) if your keys include non-ASCII characters.
- **Thread safety**: No locking is applied; callers should coordinate concurrent writes if needed.

## Example INI Configuration

```ini
[default]
provider     = filesystem
folder_path  = ./data/cache        # relative to the current working directory
encoding     = utf-8               # optional

[provider_params]
# You can override folder_path/encoding here; values in [default] win when present.
```

### Absolute Path Example

```ini
[default]
provider     = filesystem
folder_path  = /tmp/tmp_file
```

## Python Usage

```python
import cshelve

# Using the INI configuration
with cshelve.open('filesystem.ini') as db:
    db['bonjour'] = 'hello'
    assert db['bonjour'] == 'hello'
```

## Troubleshooting

- **Permission denied**: Ensure the process can create and write to `folder_path` (and its parents). On Unix, check directory ownership and mode bits; on Windows, ensure the process has write permissions.
- **Non-directory at folder_path**: If a file already exists where `folder_path` should be, `create()` will raise a `ConfigurationError`. Remove or rename the conflicting file, or choose another folder.
- **Encoding errors**: If decoding issues occur with keys, align the `encoding` setting between writers and readers. Prefer UTF-8 unless there is a specific need for another encoding.
