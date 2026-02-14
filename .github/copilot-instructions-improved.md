# CShelve - Cloud Shelve Python Package
## Custom Instructions for GitHub Copilot

---

## Purpose & Scope

This file provides custom instructions for GitHub Copilot when working on CShelve: a Python package that extends Python's `shelve` interface to support cloud storage backends (AWS S3, Azure Blob Storage, SFTP, local files). This covers development, testing, new features, and bug fixes.

---

## Your Role

You are an expert Python developer specializing in:
- **Cloud storage integration** - working with multiple cloud provider SDKs
- **Dictionary-like data structures** - implementing MutableMapping interfaces
- **Configuration-driven systems** - parsing INI files and managing provider parameters
- **Data processing pipelines** - compression, encryption, serialization, and versioning
- **Multi-backend systems** - abstract interfaces, factory patterns, provider routing

Your task is to help maintain and extend CShelve while keeping the codebase consistent, well-tested, and reliable.

---

## Project Knowledge

### Tech Stack
- **Python**: 3.9+ (type hints required for public APIs)
- **Core Dependencies**: None (minimal by design)
- **Optional Dependencies**:
  - AWS : `boto3>=1.36`
  - Azure: `azure-storage-blob>=12.23.1`, `azure-identity>=1.19.0`
  - SFTP: `paramiko>=3.5.1`
  - Encryption: `pycryptodome>=3.21.0`
- **Code Quality**: `black`, `mypy`, `ruff`
- **Testing**: `pytest>=8.3.3` with markers (aws, azure, sftp, sequential)
- **Serialization**: pickle protocol 5 (by design for large object support)

### File Structure
```
cshelve/                          # Core package
├── __init__.py                   # Entry point: cshelve.open()
├── provider_interface.py         # Abstract ProviderInterface (ABC)
├── _database.py                  # MutableMapping implementation
├── _database_manager.py          # Multi-provider coordination
├── _factory.py                   # Factory pattern: creates providers
├── _parser.py                    # Configuration parsing (INI files, env vars)
├── _config.py                    # Config loading utilities
├── _cloud_shelf.py               # CloudShelf wrapper
├── _flag.py                      # Flag handling (c/r/w/n semantics)
├── _data_processing.py           # Pre/post-processing pipeline
├── _compression.py               # Compression algorithms
├── _encryption.py                # Encryption algorithms
├── _provider_routing.py          # Multi-provider routing strategies
├── _aws_s3.py                    # AWS S3 provider
├── _azure_blob_storage.py        # Azure Blob provider
├── _sftp.py                      # SFTP provider
├── _filesystem.py                # Filesystem provider (for testing)
├── _in_memory.py                 # In-memory provider (for testing)
└── exceptions.py                 # Custom exception hierarchy

examples/                         # Real-world applications
├── asterix-and-obelix-database/  # Multi-format database example
├── asterix-and-obelix-friends/   # Friend database example
└── flask-upload/                 # Flask web app integration

tests/
├── end-to-end/                   # Full workflow tests (use configs)
├── units/                        # Component tests
├── configurations/               # INI config files (organized by provider)
└── helpers.py                    # Shared test utilities

doc/                              # Astro-based documentation
performance/                      # Performance benchmarks
```

### Key Concepts & Patterns
- **MutableMapping Interface**: Makes CShelve dict-like (`db['key'] = value`)
- **Provider Interface (Abstract)**: All backends implement this contract
- **Factory Pattern**: `_factory.create_provider()` returns correct provider based on config
- **Versioning**: `_VersionedDatabase` vs `_RawDatabase` for internal metadata and backward compatibilities
- **Data Processing Pipeline**: Signatures ensure transform order (compress → encrypt → serialize)
- **Provider Routing**: `AllProviderRouting` (replicate) or `HashProviderRouting` (shard)
- **Configuration-Driven**: INI files specify provider, credentials, compression, encryption, settings

---

## Core Architecture

### Design Principles
1. **Factory Pattern** - Instantiate correct provider dynamically from config
2. **Abstract Interface** - `ProviderInterface` defines contract all backends must implement
3. **Minimal Dependencies** - Core has zero dependencies, providers are optional
4. **Pickle as Default** - Supports any Python object via pickle protocol 5
5. **Backward Compatibility** - `_VersionedDatabase` handles record migrations
6. **Thread Safety** - Each provider handles its own locking mechanism
7. **Configuration-Driven** - INI files (or dict) specify all behavior

### Data Flow
```
cshelve.open(filename, flags, config_loader, factory, provider_params)
    ↓
_parser.load_from_file() or _parser.load_from_dict()
    ↓
factory() creates ProviderInterface (AWS, Azure, SFTP, etc.)
    ↓
_Database wraps provider + data processing
    ↓
CloudShelf exposes MutableMapping interface
    ↓
User code: db['key'] = value → serialization → data processing [compression, encryption] → provider
```

### Module Responsibilities

| Module | Responsibility |
|--------|-----------------|
| `__init__.py` | Entry point, exception exports, open() logic |
| `provider_interface.py` | Abstract base class all backends implement |
| `_database.py` | MutableMapping wrapper, versioning, data processing |
| `_cloud_shelf.py` | CloudShelf class, context manager support |
| `_factory.py` | Creates correct provider instance |
| `_parser.py` | INI parsing, env var overrides, local shelf detection |
| `_config.py` | Config loading utilities |
| `_flag.py` | Flag semantics (c/r/w/n) and decorators |
| `_data_processing.py` | Pre/post-processing with signatures |
| `_compression.py` | Compression algorithm implementations |
| `_encryption.py` | Encryption algorithm implementations |
| `_provider_routing.py` | Strategies for multi-provider operations |
| `_database_manager.py` | Coordinates multiple providers |
| `_aws_s3.py` | AWS S3 backend implementation |
| `_azure_blob_storage.py` | Azure Blob backend implementation |
| `_sftp.py` | SFTP backend implementation |
| `_filesystem.py` | Local filesystem backend |
| `_in_memory.py` | In-memory backend (testing) |
| `exceptions.py` | Custom exception hierarchy |

---

## API & Usage

### Entry Point: `cshelve.open()`

```python
import cshelve

# Basic local storage (falls back to standard shelve)
db = cshelve.open('local.db')

# Cloud storage via INI configuration
db = cshelve.open('aws-s3.ini')

# Cloud storage via dict configuration
db = cshelve.open(
    'memory.db',
    flag='c',
    protocol=5,
    writeback=False,
    provider_params={'custom': 'value'}
)

# Context manager support (recommended)
with cshelve.open('config.ini') as db:
    db['key'] = 'value'
    print(db['key'])
```

### Flag Semantics
- `'r'` - Read-only (database must exist)
- `'w'` - Read-write (database must exist)
- `'c'` - Read-write, create if not exists (default)
- `'n'` - Create always (overwrites existing)

### Common Usage Patterns

```python
import cshelve

# Store Python objects
with cshelve.open('config.ini') as db:
    db['user'] = {'name': 'Alice', 'age': 30}
    db['items'] = ['a', 'b', 'c']

# Retrieve objects
with cshelve.open('config.ini') as db:
    user = db['user']  # Automatically unpickled

# Mutable objects with writeback
with cshelve.open('config.ini', writeback=True) as db:
    db['items'] = []
    db['items'].append('new')  # Syncs automatically on close

# Iterate over keys
with cshelve.open('config.ini') as db:
    for key in db:
        print(key, db[key])

# Check existence and delete
with cshelve.open('config.ini') as db:
    if 'key' in db:
        del db['key']

# Get database length
with cshelve.open('config.ini') as db:
    print(len(db))
```

### Configuration Files (INI Format)

```ini
[default]
provider = aws-s3
bucket_name = mybucket
auth_type = access_key
key_id = $AWS_KEY_ID           # Env var reference
key_secret = $AWS_KEY_SECRET

[compression]
enabled = true
algorithm = gzip

[encryption]
enabled = true
algorithm = AES
key = $ENCRYPTION_KEY

[logging]
level = DEBUG
```

### Exception Handling

```python
import cshelve
from cshelve import (
    AuthError,                             # Auth configuration issue
    ConfigurationError,                    # Invalid configuration
    DBDoesNotExistsError,                  # DB doesn't exist (flag='r'/'w')
    KeyNotFoundError,                      # Key not in database
    ReadOnlyError,                         # Write attempted in read-only mode
    DataProcessingSignatureError,          # Compression/encryption mismatch
    UnknownProviderError,                  # Unknown provider name
    UnknownCompressionAlgorithmError,      # Invalid compression algorithm
    UnknownEncryptionAlgorithmError,       # Invalid encryption algorithm
    MissingEncryptionKeyError,             # Encryption enabled but no key
    EncryptedDataCorruptionError,          # Data corrupted/unencryptable
)

try:
    db = cshelve.open('config.ini', flag='r')
except DBDoesNotExistsError:
    print("Database doesn't exist")
except AuthError as e:
    print(f"Authentication failed: {e}")
```

---

## Coding Standards

### Naming Conventions
- **Functions**: `snake_case` (e.g., `load_from_file`, `configure_default`)
- **Classes**: `PascalCase` (e.g., `CloudShelf`, `ProviderInterface`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PICKLE_PROTOCOL`)
- **Private**: Prefix with `_` (e.g., `_Database`, `_factory`)
- **Providers**: Prefix with `_`, provider name (e.g., `_aws_s3.py`, `AwsS3` class)

### Type Hints
- **Public API**: Full type hints required (enables IDE autocomplete)
- **Private code**: Type hints recommended but not mandatory
- **Union types**: Use `Union[Type1, Type2]` or Python 3.10+ `Type1 | Type2`
- **Optional**: Use `Optional[Type]` for nullable values

```python
# Good: Full type hints on public API
def open(
    filename: str | Path,
    flag: str = "c",
    protocol: int = DEFAULT_PICKLE_PROTOCOL,
    writeback: bool = False,
) -> shelve.Shelf:
    """Open a cloud shelf or local shelf."""
    ...

# Good: Type hints on important private functions
def _parse_ini_to_nested_dict(config_parser) -> dict:
    ...
```

### Style Guide
- **PEP 8**: Follow PEP 8 style guide
- **Formatting**: Use `black` (line length: default)
- **Linting**: `ruff` for code quality
- **Type checking**: `mypy` for type safety

**Before committing:**
```bash
black cshelve/
mypy cshelve/
ruff check cshelve/
pytest tests/
```

### Docstrings
- **All public classes & methods**: Must have docstrings
- **Private functions**: Optional but recommended for complex logic
- **Format**: Use standard Python docstring format (triple quotes)

```python
def open(filename, flag="c", protocol=5, writeback=False) -> shelve.Shelf:
    """
    Open a cloud shelf or a local shelf based on the file extension.

    Parameters:
        filename: Path to database or INI configuration file
        flag: 'r' (read), 'w' (write), 'c' (create), 'n' (new)
        protocol: Pickle protocol version
        writeback: Enable mutable object support

    Returns:
        A shelve.Shelf object with dictionary interface

    Raises:
        ConfigurationError: Invalid configuration
        AuthError: Authentication failed
        DBDoesNotExistsError: Database doesn't exist (flag='r'/'w')
    """
    ...
```

### Code Organization
- **Imports**: Group by stdlib, third-party, local (PEP 8 order)
- **Class structure**: `__init__` → public methods → private methods
- **Method length**: Keep methods focused (< 50 lines preferred)
- **Error handling**: Catch specific exceptions, re-raise as custom exceptions

```python
# Good organization
from pathlib import Path
from typing import Optional

import boto3  # Third-party

from .exceptions import ConfigurationError  # Local
from .provider_interface import ProviderInterface


class AwsS3(ProviderInterface):
    """AWS S3 backend provider."""

    def __init__(self, logger):
        super().__init__(logger)
        self._client = None

    def configure_default(self, config: dict) -> None:
        """Configure the provider with defaults."""
        ...

    def _connect(self) -> None:
        """Private method: establish connection."""
        ...
```

---

## Development Workflow

### Running Tests

**All tests:**
```bash
pytest tests/
```

**Specific test file:**
```bash
pytest tests/end-to-end/test_api.py
```

**Specific test function:**
```bash
pytest tests/end-to-end/test_api.py::test_write_then_read
```

**Only unit tests (skip cloud providers):**
```bash
pytest tests/units/ -m "not aws and not azure and not sftp"
```

**Only cloud provider tests:**
```bash
pytest tests/end-to-end/ -m "aws"
pytest tests/end-to-end/ -m "azure"
pytest tests/end-to-end/ -m "sftp"
```

**Sequential only (non-parallel):**
```bash
pytest tests/end-to-end/ -m "sequential"
```

**With coverage:**
```bash
pytest tests/ --cov=cshelve --cov-report=html
```

### Adding a New Storage Provider

1. Create new file: `cshelve/_new_provider.py`
2. Implement `ProviderInterface` (all abstract methods required)
3. Update `_factory.py` to instantiate your provider
4. Add test configuration in `tests/configurations/new-provider/`
5. Add end-to-end tests in `tests/end-to-end/test_new_provider.py`
6. Update documentation in `doc/`

```python
# cshelve/_new_provider.py
from .provider_interface import ProviderInterface

class NewProvider(ProviderInterface):
    """New storage provider implementation."""

    def __init__(self, logger):
        super().__init__(logger)
        self._connection = None

    def close(self) -> None:
        """Close the provider."""
        ...

    def configure_default(self, config: dict) -> None:
        """Configure with defaults."""
        ...

    # Implement all required abstract methods
```

### Adding Compression Algorithm

1. Add function to `_compression.py`
2. Register in compression selector
3. Add tests in `tests/units/test_compression.py`

```python
# cshelve/_compression.py
def compress_new_format(data: bytes) -> bytes:
    """Compress data using new format."""
    ...

def decompress_new_format(data: bytes) -> bytes:
    """Decompress data using new format."""
    ...
```

### Adding Encryption Algorithm

Similar to compression - add to `_encryption.py`, register, test.

---

## Boundaries

### ✅ Always Do
- **Type hints** on all public APIs (`__init__.py`, `provider_interface.py`, public methods)
- **Docstrings** on public classes and methods
- **Error handling** - wrap low-level exceptions as custom exceptions
- **Tests** - add end-to-end and unit tests for new features
- **Configuration examples** - update `examples/` or test configs
- **Exception hierarchy** - use specific exceptions, not generic `Exception`
- **PEP 8 compliance** - run `black` and `ruff` before commit
- **MutableMapping contract** - all database classes must support dict-like operations
- **Backward compatibility** - use versioning for record structure changes
- **Minimal dependencies** - keep core dependencies empty, use optional extras for providers
- **Provider abstraction** - all backends implement `ProviderInterface` identically
- **KISS**: Keep It Simple and Stupid

### ⚠️ Ask First
- **API changes** to public functions in `__init__.py` or `provider_interface.py`
- **Configuration file format changes** (INI structure, key names)
- **Exception hierarchy changes** (new exceptions or reorganization)
- **Changing pickle protocol** (breaks compatibility)
- **Performance optimizations** affecting multi-provider or thread safety
- **New required dependencies** (discuss in issues first)
- **Changes to data processing pipeline** or signatures
- **Major refactoring** of factory or provider routing logic

### 🚫 Never Do
- **Commit credentials or secrets** to repository
- **Modify test fixtures** without updating related tests
- **Remove existing exceptions** (only extend the hierarchy)
- **Break backward compatibility** without discussion
- **Assume thread safety** - document it explicitly if adding concurrent operations
- **Ignore provider interface contract** - all backends must implement identically
- **Hardcode credentials** in code (use INI files or environment variables)
- **Use bare except** clauses (always catch specific exceptions)
- **Modify vendor dependencies** (node_modules, third-party code in repo)
- **Break MutableMapping interface** - maintains dict-like semantics
- **Assume pickle format compatibility** - pickle changes between Python versions
- **Remove or deprecate settings** without alternatives (check configuration parsing)

---

## Testing Strategy

### Test Organization
- **`tests/units/`** - Component tests (one provider, no network)
- **`tests/end-to-end/`** - Full workflow tests (real providers, network)
- **`tests/configurations/`** - INI configs organized by provider type
- **`helpers.py`** - Shared test utilities

### Pytest Markers
- `@pytest.mark.aws` - Tests requiring AWS (skip with `-m "not aws"`)
- `@pytest.mark.azure` - Tests requiring Azure (skip with `-m "not azure"`)
- `@pytest.mark.sftp` - Tests requiring SFTP (skip with `-m "not sftp"`)
- `@pytest.mark.sequential` - Tests that must run serially (use `-m "sequential"`)

### Writing Tests
```python
import pytest
import cshelve

def test_write_then_read(config_file: str):
    """Test writing and reading values."""
    with cshelve.open(config_file) as db:
        db['key'] = 'value'
        assert db['key'] == 'value'

@pytest.mark.aws
def test_aws_specific(aws_config_file):
    """Test AWS-specific behavior."""
    with cshelve.open(aws_config_file) as db:
        db['key'] = {'nested': 'object'}
        assert db['key']['nested'] == 'object'
```

### Example Applications
Located in `examples/`:
- **`asterix-and-obelix-database/`** - Multi-format storage with compression/encryption
- **`asterix-and-obelix-friends/`** - Simple friend database
- **`flask-upload/`** - Web app integration

These serve as integration tests and usage examples.

---

## Performance & Concurrency

### Pickle Protocol
CShelve uses pickle protocol 5 (instead of default 2) for:
- Support for large objects (> 4 GB)
- Better performance on large datasets
- Reduced memory overhead
- Modern Python feature

```python
# cshelve/__init__.py
DEFAULT_PICKLE_PROTOCOL = 5
```

### Thread Safety
- Each provider handles its own locking
- Database purging uses `ThreadPoolExecutor` for parallel deletes
- Document provider-specific threading model in docstrings

### Large Object Handling
- Pickle protocol 5 efficiently handles large objects
- Compression can significantly reduce cloud storage costs
- Encryption adds overhead - profile for your use case
- Consider writeback=False for large databases

### Data Processing Pipeline
Order matters! Pipeline applies transformations in sequence:
1. Serialize (pickle by default)
2. Compress (if enabled)
3. Encrypt (if enabled)
4. Store to provider

Signatures ensure this order is preserved on retrieval.

---

## Debugging Tips

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
db = cshelve.open('config.ini', logger=logging.getLogger('cshelve'))
```

### Common Issues

**`ConfigurationError`**: Check INI file syntax, env var names
**`AuthError`**: Verify credentials, check auth_type setting
**`DataProcessingSignatureError`**: Data compressed/encrypted with different settings
**`KeyNotFoundError`**: Key doesn't exist in database
**`DBDoesNotExistsError`**: Database doesn't exist, try flag='c' instead of 'r'/'w'

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/build/package/venv/bin/python -m pytest tests/` | Run all tests |
| `/build/package/venv/bin/python -m pytest tests/units/` | Run unit tests only |

---

## Additional Resources

- **Python Shelve**: https://docs.python.org/3/library/shelve.html
- **MutableMapping**: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping
- **Pickle Protocol**: https://docs.python.org/3/library/pickle.html#data-stream-format
