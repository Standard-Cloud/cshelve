---
title: In-Memory Provider
description: Configure *cshelve* to save in-memory data.
---

For testing and development purposes, it is useful to have an in-memory provider. This provider is not persistent, and data will be lost when the program ends, but it allows for testing without persistent storage.

## Configuration Options

| Option        | Description                                                               | Required | Default Value |
|---------------|---------------------------------------------------------------------------|----------|---------------|
| `persist-key` | If set, its value will be conserved and reused during program execution.  | No       | `False`      |
| `exists`      | If `True`, the database exists; otherwise, it will be created.             | No       | `False`      |

## Example Configuration

```ini
[default]
provider      = in-memory
persist-key   = True
exists        = True
```

> **Note:** The in-memory provider is included for convenience during development and testing. Data stored is not persistent and will be lost upon program termination.
