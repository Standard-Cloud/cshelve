---
title: Compression Configuration
description: Configure *cshelve* to use compression.
---

*cshelve* supports compression to reduce the size of stored data. This is particularly useful when working with large datasets or to reduce network time. The compression algorithm can be configured using the options provided in the configuration.

## Example Configuration

```ini
[default]
provider        = in-memory
algorithm       = zlib

[compression]
algorithm   = zlib
level       = 1
```

In this example, the `algorithm` is set to `zlib`, and the [compression level](https://docs.python.org/3/library/zlib.html) is set to `1`.

## Supported Algorithms

Supported compression algorithms include:

- `zlib`: Uses the `zlib` library for compression.

## Usage Example

*cshelve* supports compression transparently; the compression settings don't require changes to the application code:

```python
import cshelve

with cshelve.open('config.ini') as db:
    db['data'] = 'This is some data that will be compressed.'

with cshelve.open('config.ini') as db:
    data = db['data']
```

## Error Handling

If the specified compression algorithm isn't supported, *cshelve* raises an `UnknownCompressionAlgorithmError`. Ensure the chosen algorithm is correctly specified in the configuration.
