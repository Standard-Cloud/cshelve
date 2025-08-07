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
- **Thread Safety**: Uses `ThreadPoolExecutor` for efficient database purging.
- **Flag Handling**: Manages database creation, write permissions, and clearing based on flags.

This layer is abstracting the complexities of different storage backends while providing a consistent interface for users.

### Configuration Parsing Module

The `_parser.py` file is responsible for parsing configuration files and determining the appropriate storage provider and its settings. Key features include:

- **Configuration Parsing**: Reads INI files to extract provider details and settings using the `configparser` module.
- **Provider Configuration**: Extracts provider-specific parameters and general settings like logging, compression, and encryption.
- **Environment Variable Support**: Allows configuration values to be overridden by environment variables using the `from_env` function.
- **Local Shelf Detection**: Determines if a local shelf (standard library `shelve`) should be used based on the file extension.
- **Named Tuple for Configuration**: Returns a structured `Config` named tuple containing all parsed settings.
- **Default Settings**: Provides sensible defaults for settings like `use_pickle` and `use_versionning`.

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
db['key'] = 'value'
print(db['key'])
db.close()
```

### Configuration Files
INI files specify the storage backend and authentication:
```ini
[default]
provider = aws-s3
bucket_name = my-bucket
auth_type = access_key
key_id = $AWS_KEY_ID
key_secret = $AWS_KEY_SECRET
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
