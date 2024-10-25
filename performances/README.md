# Performance Testing

## Overview

This project is designed to measure the performance of various database operations using the `cshelve` module. Tests are conducted on all backends, including the one provided by the Python interpreter, allowing comparisons between local and remote storage.

## Usage

```sh
python main.py <database_name> [<os_type> <python_major_version> <commit_hash>]
```

- `<database_name>`: The name of the database file where the results will be stored.
- `<os_type>` (optional): The operating system type.
- `<python_major_version>` (optional): The major version of Python.
- `<commit_hash>` (optional): The commit hash of the current codebase.

### Example

For testing:
```sh
python main.py staging.results.ini Linux 3.8 abc123
```

For production (running in the CI):
```sh
python main.py production.results.ini Linux 3.8 abc123
```

## Tests

Following tests are run on the database:
- `write_same_key`: Writes the same key multiple times.
- `delete_same_key`: Writes and then deletes the same key multiple times.
- `write_several_keys`: Writes several unique keys.
- `delete_several_keys`: Writes and then deletes several unique keys.
- `read_same_key`: Reads the same key multiple times.
- `read_several_keys`: Reads several unique keys.
- `iterate_several_keys`: Iterates over several keys.
- `len_several_keys`: Measures the length of the database with several keys.

## Running the Tests

1. Ensure you have the `cshelve` module installed.
2. Run the `main.py` script with the appropriate arguments.
3. The results will be stored in the specified database file.
