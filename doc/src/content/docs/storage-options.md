---
title: Storage Options
description: Configure data storage options for *cshelve*.
---

When using `cshelve`, you have full control over how data is stored and retrieved. By default, `cshelve` uses `pickle` for serializing and deserializing Python objects, but it also allows storage of raw bytes, making it compatible with formats like JSON, Parquet, CSV, and more.

This document explains these options and how to configure them.

---

## Storage Configuration Fields

Two primary configuration options control storage behavior:

### 1. `use_pickle` (Data Format Control)

- **Description:** Controls the use of `pickle` for serialization.
- **Default:** `True`.
- **Enabled:** Automatically serializes/deserializes Python objects.
- **Disabled:** Stores data as raw bytes; users handle byte conversions manually.

**Example Usage:**

Configuration file (`storage.ini`):
```ini
[default]
provider        = ...
auth_type       = ...
use_pickle      = false
```

Python usage:
```python
import json
import cshelve

data = {"key": "value", "number": 42}
with cshelve.open('storage.ini') as db:
    db['my_json'] = json.dumps(data).encode()

with cshelve.open('storage.ini') as db:
    retrieved_data = json.loads(db['my_json'].decode())

print(retrieved_data)
```

**Reasons to Disable `use_pickle`:**
- Data can be accessed in other programming languages.
- Avoid Python-specific serialization overhead.

**Important Note:**
- `cshelve` adds metadata to stored data. Use `use_versioning` to disable metadata.

### 2. `use_versioning` (Data Versioning and Metadata Management)

- **Description:** Adds versioning metadata to stored data.
- **Default:** `True`.
- **Purpose:**
  - Manages data evolution and integrity.
  - Facilitates smooth upgrades between data versions.

**Example Usage:**

Configuration file (`storage.ini`):
```ini
[default]
provider         = ...
auth_type        = ...
use_versionning  = false
```

Python usage:
```python
import cshelve

with cshelve.open('storage.ini') as db:
    db['my_data'] = b"Raw binary data"
```

**Why Enable `use_versioning`?**
- Easier management and upgrades of stored data.
- Ensures consistency and integrity.

**Why Disable `use_versioning`?**
- Reduced overhead in storage.
- Ideal for simple or temporary storage.

---

## Practical Use Cases

### Scenario 1: Storing JSON Data for External Use

- **Goal:** Store JSON data for non-Python access.
- **Configuration:** `use_pickle=False`, `use_versionning=False`.

Example:

Configuration (`storage.ini`):
```ini
[default]
provider         = ...
auth_type        = ...
use_pickle       = false
use_versionning  = false
```

Python:
```python
import json
import cshelve

data = {"name": "Alice", "score": 95}
with cshelve.open('storage.ini') as db:
    db['student_data'] = json.dumps(data).encode()

with cshelve.open('storage.ini') as db:
    retrieved = json.loads(db['student_data'].decode())
print(retrieved)  # {'name': 'Alice', 'score': 95}
```

### Scenario 2: Storing and Retrieving Parquet Files
- **Goal:** Store Parquet data usable by various loaders.
- **Configuration:** `use_pickle=False`, `use_versionning=False`.

Example:

Configuration (`storage.ini`):
```ini
[default]
provider         = ...
auth_type        = ...
use_pickle       = false
use_versionning  = false
```

Python:
```python
import pandas as pd
import cshelve

df = pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})
parquet_bytes = df.to_parquet()

with cshelve.open('storage.ini') as db:
    db['dataset'] = parquet_bytes

with cshelve.open('storage.ini') as db:
    retrieved_df = pd.read_parquet(db['dataset'])

print(retrieved_df)
```

---

## Conclusion

Configuring `use_pickle` and `use_versioning` provides flexibility to optimize performance, interoperability, and data management. These options enable `cshelve` to serve diverse storage needs—from simple key-value storage to advanced cloud-based data management solutions.
