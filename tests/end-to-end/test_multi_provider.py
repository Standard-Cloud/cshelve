"""
End-to-end tests for multi-provider configuration.
Tests that data is written to and read from all providers correctly.
"""
from pathlib import Path
from unittest.mock import Mock
from logging import Logger
import os
from unittest.mock import patch
import pickle

import pytest

import cshelve


def _verify_data_in_all_databases(shelf, test_key, test_value):
    """
    Helper function to verify that data exists in all underlying databases.

    Note: The data is pickled when stored in the underlying _Database, so we need to unpickle it.

    Args:
        shelf: The CloudShelf instance
        test_key: The key to verify
        test_value: The expected value (as bytes)
    """
    # Access the DatabaseManager which contains all _Database instances
    database_manager = shelf.dict

    # Verify data exists in all databases by checking each one directly
    for idx, database in enumerate(database_manager.databases):
        # Try to retrieve the data from each database
        try:
            # Data is stored in pickled form in the underlying database
            stored_pickled = database[test_key.encode("utf-8")]
            # Unpickle to get the actual value
            stored_value = pickle.loads(stored_pickled)
            assert (
                stored_value == test_value
            ), f"Database {idx}: Value mismatch. Expected {test_value}, got {stored_value}"
        except KeyError:
            raise AssertionError(f"Database {idx}: Key '{test_key}' not found")


def _verify_data_deleted_from_all_databases(shelf, test_key):
    """
    Helper function to verify that data has been deleted from all underlying databases.

    Args:
        shelf: The CloudShelf instance
        test_key: The key to verify is deleted
    """
    # Access the DatabaseManager which contains all _Database instances
    database_manager = shelf.dict

    # Verify data is deleted from all databases
    for idx, database in enumerate(database_manager.databases):
        with pytest.raises(Exception):
            database[test_key.encode("utf-8")]


def test_multi_provider_write_read_delete():
    """
    End-to-end test for multi-provider configuration.

    Scenario:
    1. Open multi-provider shelf (filesystem + in-memory)
    2. Write data using cshelve
    3. Read data using cshelve
    4. Verify data exists in all underlying _Database objects
    5. Delete data using cshelve
    6. Verify cshelve cannot read the deleted data
    7. Verify data is deleted from all underlying _Database objects
    """
    config_file = Path("tests/configurations/config/local-mutli-providers.ini")
    logger = Mock(spec=Logger)

    # Test data
    test_data = {
        "user:1": b"Alice",
        "user:2": b"Bob",
        "settings:color": b"blue",
    }

    # Set required environment variable for encryption
    with patch.dict(os.environ, {"ENCRYPTION_KEY": "Sixteen byte key"}):
        # Part 1: Write and read data using cshelve normally
        print("\n=== Part 1: Write and read data ===")
        with cshelve.open(config_file, logger=logger) as shelf:
            # Write all test data
            for key, value in test_data.items():
                shelf[key] = value
                print(f"Written: {key} = {value}")

            # Read all test data back
            for key, expected_value in test_data.items():
                read_value = shelf[key]
                assert read_value == expected_value, f"Read mismatch for {key}"
                print(f"Read: {key} = {read_value}")

        # Part 2: Reopen shelf and verify data persists
        print("\n=== Part 2: Verify data persists across opens ===")
        with cshelve.open(config_file, logger=logger) as shelf:
            for key, expected_value in test_data.items():
                read_value = shelf[key]
                assert (
                    read_value == expected_value
                ), f"Data persistence failed for {key}"
                print(f"Verified persistent: {key} = {read_value}")

        # Part 3: Verify data exists in all underlying databases
        print("\n=== Part 3: Verify data in all databases ===")
        with cshelve.open(str(config_file), logger=logger) as shelf:
            for key, expected_value in test_data.items():
                _verify_data_in_all_databases(shelf, key, expected_value)
                print(f"Verified in all databases: {key}")

        # Part 4: Delete data and verify cshelve cannot read it
        print("\n=== Part 4: Delete data ===")
        with cshelve.open(str(config_file), logger=logger) as shelf:
            # Delete one key at a time and verify
            for key_to_delete in list(test_data.keys())[:2]:
                del shelf[key_to_delete]
                print(f"Deleted from shelf: {key_to_delete}")

                # Verify cshelve cannot read deleted key
                with pytest.raises(Exception):
                    _ = shelf[key_to_delete]
                print(f"Verified deleted from shelf: {key_to_delete}")

                # Verify data is deleted from all databases
                _verify_data_deleted_from_all_databases(shelf, key_to_delete)
                print(f"Verified deleted from all databases: {key_to_delete}")

        # Part 5: Verify data is still deleted after reopening
        print("\n=== Part 5: Verify deletions persist ===")
        with cshelve.open(str(config_file), logger=logger) as shelf:
            # Check deleted keys are still gone
            for key_to_check in list(test_data.keys())[:2]:
                with pytest.raises(Exception):
                    _ = shelf[key_to_check]
                print(f"Verified still deleted: {key_to_check}")

            # Check remaining key still exists
            remaining_key = list(test_data.keys())[2]
            remaining_value = shelf[remaining_key]
            assert remaining_value == test_data[remaining_key]
            del shelf[remaining_key]
            print(f"Verified remaining data still exists: {remaining_key}")

        print("\n=== Test completed successfully ===")
