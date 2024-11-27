"""
Verify error handling in the library.
"""
import os
import pytest

import cshelve


CONFIG_FILES = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
]


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_key_not_found(config_file):
    """
    Ensure KeyError is raised when key is not found.
    """
    db = cshelve.open(config_file)

    with pytest.raises(cshelve.KeyNotFoundError):
        db["test_key_not_found"]

    db.close()


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES,
)
def test_raise_delete_missing_object(config_file):
    """
    Ensure delete an non-existing object raises KeyError.
    """
    db = cshelve.open(config_file)

    key_pattern = "test_delete_object"

    with pytest.raises(cshelve.KeyNotFoundError):
        del db[key_pattern]

    db.close()


def test_unknown_auth_type():
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthTypeError):
        cshelve.open(
            "tests/configurations/azure-blob/simulator/error-handling/unknown-auth-type.ini"
        )


def test_no_connection_string_key_auth_type():
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthArgumentError):
        cshelve.open(
            "tests/configurations/azure-blob/simulator/error-handling/connection-string-without-connection-string.ini"
        )


def test_no_connection_string_in_env():
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthArgumentError):
        cshelve.open(
            "tests/configurations/azure-blob/simulator/error-handling/connection-string-without-env-var.ini"
        )
