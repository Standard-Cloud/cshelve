# CShelve - Cloud Shelve Python Package

## Overview

CShelve (Cloud Shelve) is a Python package that extends the familiar Python `shelve` interface to support cloud storage backends. It provides a seamless, dictionary-like storage system that can persist data locally or in various cloud storage services including AWS S3, Azure Blob Storage, and SFTP.

## Key Concepts

### What CShelve Does
- **Cloud-Native Dictionary Storage**: Provides a `shelve`-like interface for storing Python objects in cloud storage
- **Multiple Backend Support**: Works with AWS S3, Azure Blob Storage, SFTP, and local storage
- **Pickle by Default**: Serializes Python objects using pickle, but supports any data format as bytes
- **Configuration-Driven**: Uses INI configuration files or the `provider_params` to specify storage backends, credentials and configuration options

### Architecture
- **Provider Interface**: Abstract base class (`provider_interface.py`) for storage backends
- **Factory Pattern**: Creates appropriate storage providers based on configuration (`_factory.py`)
- **Data Processing**: Handles data operations pre and post storage via the provider, including compression and encryption (`_data_processing.py`, `_compression.py`, `_encryption.py`)
- **Configuration**: INI file parser for backend configuration (`_parser.py`, `_config.py`)

### Database Abstraction Layer

The `_database.py` file provides the core abstraction for interacting with storage backends. It implements a `MutableMapping` interface, making it behave like a Python dictionary. Key features include:

- **Versioning**: Ensures backward compatibility with `_VersionedDatabase`, handling data migrations when record structures change.
- **Provider Integration**: Delegates storage operations to the `ProviderInterface`.
- **Data Processing**: Applies pre- and post-processing (e.g., compression, encryption) using the `DataProcessing` module.
- **Thread Safety**: Uses `ThreadPoolExecutor` for efficient database purging.# CShelve - Cloud Shelve Python Package

## Overview

CShelve is a Python package that extends the `shelve` interface to support cloud storage backends. It provides a dictionary-like API for storing Python objects locally or in the cloud (AWS S3, Azure Blob Storage, SFTP).

## Key Concepts

- **Cloud-Native Dictionary Storage**: Like `shelve`, but supports cloud backends.
- **Multiple Backend Support**: AWS S3, Azure Blob, SFTP, local, and in-memory.
- **Pickle Serialization**: Uses pickle by default; stores any bytes.
- **Configuration-Driven**: Uses INI files or `provider_params` for backend setup.

## Architecture

- **Provider Interface**: Abstract base class for storage backends (`provider_interface.py`).
- **Factory Pattern**: Instantiates providers based on config (`_factory.py`).
- **Data Processing**: Handles compression/encryption (`_data_processing.py`, `_compression.py`, `_encryption.py`).
- **Configuration Parsing**: Reads INI files and environment variables (`_parser.py`, `_config.py`).

## Database Abstraction Layer (`_database.py`)

- Implements `MutableMapping` (dict-like).
- Supports versioning and migrations.
- Delegates storage to providers.
- Handles data processing (compression/encryption).
- Thread-safe purging.
- Manages flags for creation, write permissions, clearing.

## Configuration Parsing (`_parser.py`)

- Parses INI files for provider and settings.
- Supports environment variable overrides.
- Detects local shelf usage by file extension.
- Returns a `Config` named tuple with provider, params, and settings.

## Data Processing (`_data_processing.py`)

- `DataProcessing` class for pre/post-processing (compression, encryption).
- Uses signatures for transformation order.
- Encapsulates data with metadata.
- Raises `DataProcessingSignatureError` for signature issues.
- Extensible via subclasses.

## Exceptions (`_exceptions.py`)

- Custom exceptions for uniform error handling.
- Wraps low-level provider errors.

## Supported Storage Backends

- **AWS S3** (`_aws_s3.py`): Access key/IAM role, bucket storage.
- **Azure Blob** (`_azure_blob_storage.py`): Connection string/Azure Identity, container storage.
- **SFTP** (`_sftp.py`): SSH key/password, remote file system.
- **In-Memory** (`_in_memory.py`): For testing.

All providers implement `ProviderInterface`.

## Usage Example

```python
import cshelve

db = cshelve.open('local.db')  # Local storage
db = cshelve.open('aws-s3.ini')  # Cloud storage via INI

db['key'] = 'value'
print(db['key'])

for key, value in db.items():
    print(key, value)

del db['key']
db.close()
```

## Features

- Optional compression and encryption.
- Writeback for mutable objects.
- Context manager support.

## Development Guidelines

- Core code in `cshelve/`
- Providers in `_<provider>.py`
- Examples in `examples/`
- Tests in `tests/` (use `pytest`)
- Documentation in `doc/` (Astro framework)

## Testing

- Unit, end-to-end, and performance tests.
- Example apps in `examples/`.

## Dependencies

- Managed via `pyproject.toml`.
- Minimal core dependencies.
- Provider-specific extras (`[aws-s3]`, `[azure-blob]`).

## DevOps

- GitHub Actions for CI.
- `pre-commit` hooks.
- Semantic versioning.

## Coding Standards

- PEP 8 style.
- Type hints for public APIs.
- Use `mypy` and `black`.
- Docstrings for public classes/methods.
- Use
- **Flag Handling**: Manages database creation, write permissions, and clearing based on flags.

This layer is abstracting the complexities of different storage backends while providing a consistent interface for users.

### Configuration Parsing Module

The `_parser.py` file is responsible for parsing configuration files and determining the appropriate storage provider and its settings. Key features include:

- **Configuration Parsing**: Reads INI files to extract provider details and settings using the `configparser` module.
- **Provider Configuration**: Extracts provider-specific parameters and general settings like logging, compression, and encryption.
- **Environment Variable Support**: Allows configuration values to be overridden by environment variables using the `from_env` function.
- **Local Shelf Detection**: Determines if a local shelf (standard library `shelve`) should be used based on the file extension.
- **Named Tuple for Configuration**: Returns a structured `Config` named tuple containing all parsed settings. It contains provider name, parameters, and default settings.
- **Default Settings**: Provides general settings like `use_pickle` and `use_versionning`.

This module ensures that the correct provider and settings are loaded, enabling seamless integration with various storage backends.

### Data Processing Module

The `_data_processing.py` file provides the `DataProcessing` class, which handles pre-processing and post-processing of data. Key features include:

- **Custom Transformations**: Allows adding pre- and post-processing functions for data transformations.
- **Signatures**: Ensures transformations are applied in the correct order using metadata signatures.
- **Encapsulation**: Wraps data with metadata, including signature and length information, for secure processing.
- **Error Handling**: Raises `DataProcessingSignatureError` for incompatible signatures.
- **Extensibility**: Supports both signed and unsigned data processing through `_SignedDataProcessing` and `_UnSignedDataProcessing` subclasses.

This module ensures data integrity and applies transformations like compression and encryption before storage.

### Exceptions

Custom exceptions are defined in the `_exceptions.py` file. These exceptions should be reused consistently across the package to ensure uniform error handling. They also encapsulate low-level exceptions thrown by the underlying storage providers, providing a clear and standardized interface for error reporting.

## Supported Storage Backends

1. **AWS S3** (`_aws_s3.py`)
   - Access key authentication
   - IAM role authentication
   - Bucket-based storage

2. **Azure Blob Storage** (`_azure_blob_storage.py`)
   - Connection string authentication
   - Passwordless authentication (Azure Identity)
   - Container-based storage

3. **SFTP** (`_sftp.py`)
   - SSH key authentication
   - Password authentication
   - Remote file system storage

4. **In-Memory** (`_in_memory.py`)
   - For testing and temporary storage

All providers implement the `ProviderInterface` from `provider_interface.py`, ensuring a consistent API for data operations.

## Common Patterns

### Basic Usage
```python
import cshelve

# Local storage (fallback to standard shelve)
db = cshelve.open('local.db')

# Cloud storage using INI configuration
db = cshelve.open('aws-s3.ini')
db['key'] = 'value' # Store data
print(db['key']) # Retrieve data

for key, value in db.items(): # Iterate over keys
    print(key, value)

del db['key'] # Delete data
db.close()
```

### Features
- **Compression**: Optional data compression using various algorithms
- **Encryption**: Optional data encryption for security
- **Writeback**: Support for mutable objects with automatic syncing
- **Context Manager**: Automatic resource cleanup with `with` statements

## Development Guidelines

### File Organization
- Core functionality in `cshelve/` directory
- Provider implementations in `_<provider>.py` files
- Examples in `examples/` directory with real-world use cases
- Tests in `tests/` with unit and end-to-end testing using `pytest`
- Documentation in `doc/` using Astro framework must be updated, improved, and maintained

### Testing
- Unit tests for individual components
- End-to-end tests for full workflows
- Performance tests in `performances/` directory
- Example applications in `examples/` serve as integration tests

### Dependencies
- Dependencies are managed via `pyproject.toml`
- Core package has minimal dependencies
- Provider-specific dependencies are optional extras (`[aws-s3]`, `[azure-blob]`, etc.)
- Dependencies must be minimal

### DevOps
- Use GitHub Actions for continuous integration
- `pre-commit` hooks for code quality checks
- Package versioning follows semantic versioning

### Coding Standards
- Follow PEP 8 style guide
- Type hints for all public APIs
- Use `black` for code formatting
- Put docstrings in all public methods and classes
- Use `pytest` for testing with fixtures and parameterized tests
- `assert` statements can only be used in tests
