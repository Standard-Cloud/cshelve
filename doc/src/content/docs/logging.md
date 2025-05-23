---
title: Logging Configuration
description: Configure logging for *cshelve*.
---

The `cshelve` module supports logging capabilities, enabling detailed logging for both the module itself and the underlying storage providers.

## Providing a Specific Logger to `cshelve`

A custom logger can be passed directly to the `cshelve.open` function using the `logger` parameter, allowing greater control over logging behavior.

### Example:

```python
import logging
import cshelve

custom_logger = logging.getLogger('custom_cshelve_logger')
custom_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
custom_logger.addHandler(handler)

with cshelve.open('config.ini', logger=custom_logger) as db:
    ...
```

## Provider-Specific Logging

Some storage providers offer their own detailed logging capabilities. Provider-specific logging settings can be enabled in the configuration file.

### Azure Blob Storage Example:

**Configuration file:**

```ini
[default]
provider        = azure-blob
account_url     = https://myaccount.blob.core.windows.net
auth_type       = passwordless
container_name  = mycontainer

[logging]
http            = true
credentials     = true
```

**Python usage:**

```python
import logging
import sys
import cshelve

# Configure Azure-specific logging
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

with cshelve.open('azure-blob.ini') as db:
    ...
```

For detailed logging capabilities, refer to the documentation of your specific cloud storage provider.
