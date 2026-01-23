---
title: Multi-Provider Support
description: Use multiple storage backends simultaneously with cshelve.
---

`cshelve` supports writing data to multiple storage providers at the same time. This enables powerful patterns like data replication for backup, performance optimization with caching, and multi-cloud deployments.

---

## Why Use Multiple Providers?

1. **Backup & Redundancy** – Primary storage + automatic backup to another provider
2. **Multi-Cloud Resilience** – Replicate data across AWS, Azure, and other providers
3. **Compliance** – Store data in multiple regions or providers for regulatory requirements
4. **Performance Optimization** – Fast in-memory cache + durable cloud storage

---

## How It Works

- **Writes** are sent to **all providers**
- **Reads** come from the **first provider** (for performance)
- **Deletes** are applied to **all providers**

This ensures all backends stay synchronized.

```
Write Operation:  db['key'] = value
                  ├─ → Provider 1 (Write)
                  ├─ → Provider 2 (Write)
                  └─ → Provider 3 (Write)

Read Operation:   value = db['key']
                  └─ → Provider 1 (Read only)
```

---

## Configuration

### Using INI Format

Create a configuration file with multiple provider sections:

**multi-cloud.ini**

```ini
[default]
providers = azure-primary, aws-backup
strategy  = all

[azure-primary]
provider            = azure-blob
auth_type           = connection_string
environment_key     = AZURE_STORAGE_CONNECTION_STRING
container_name      = standard

[aws-backup]
provider    = aws-s3
bucket_name = my-backup-bucket
auth_type   = access_key
key_id      = $AWS_ACCESS_KEY_ID
key_secret  = $AWS_SECRET_ACCESS_KEY
```

**Usage:**

```python
import cshelve

with cshelve.open('multi-cloud.ini') as db:
    db['user:1'] = {'name': 'Alice', 'email': 'alice@example.com'}
    print(db['user:1'])  # Read from Azure (first provider)

# Data automatically backed up to AWS S3
```

---

## Example: Provider-Specific Compression

Different compression settings per provider:

**config.ini**

```ini
[default]
providers = filesystem, s3
strategy  = all

[filesystem]
provider = filesystem
folder_path = /data/local

[filesystem.compression]
algorithm = zlib
level = 6

[s3]
provider    = aws-s3
bucket_name = my-backup-bucket
auth_type   = access_key
key_id      = $AWS_ACCESS_KEY_ID
key_secret  = $AWS_SECRET_ACCESS_KEY

[s3.compression]
algorithm = zlib
level = 9
```

This way, local storage uses moderate compression (faster), while cloud storage uses maximum compression (cheaper bandwidth).

---

## Configuration Reference

### Provider Names

In the `providers` field, use comma-separated provider names:

```ini
[default]
providers = provider1, provider2, provider3
```

### Provider Configuration

Each provider section follows the standard configuration. Check their documentation for more information:
- [AWS S3 Provider](./aws-s3)
- [Azure Blob Provider](./azure-blob)
- [Filesystem Provider](./filesystem)
- [In-Memory Provider](./in-memory)

---

## Important Considerations

### Exception Handling

There is no rollback on write failures. If a write operation fails on one provider, the operation stops and is not retried on remaining providers. For example, with 3 providers, if a write fails on the second provider, only the first provider will be updated. This inconsistency won't be visible when reading because reads only use the first provider.

### Read Performance

Reads only use the first provider, so they're fast. Place your fastest provider first:

```ini
[default]
providers = cache, persistent
```

### Write Performance

Writing to multiple providers takes longer than writing to a single provider.

---

## Next Steps

- Learn about [Compression](./compression) to optimize storage per provider
- Learn about [Encryption](./encryption) to secure your data
- See [Configuration as Dictionary](./configuration-as-dictionary) for programmatic setup
