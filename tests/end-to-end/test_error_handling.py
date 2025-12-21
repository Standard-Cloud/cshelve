"""
Verify error handling in the library.
"""
import pytest

import cshelve


CONFIG_FILES_KEY_NOT_FOUND = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/filesystem/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
    "tests/configurations/aws-s3/standard.ini",
]

CONFIG_FILES_DELETE = [
    "tests/configurations/azure-blob/standard.ini",
    "tests/configurations/filesystem/standard.ini",
    "tests/configurations/in-memory/persisted.ini",
]

CONFIG_FILES_AUTH_ERROR = [
    "tests/configurations/azure-blob/error-handling/unknown-auth-type.ini",
    "tests/configurations/azure-blob/error-handling/connection-string-without-connection-string.ini",
    "tests/configurations/azure-blob/error-handling/connection-string-without-env-var.ini",
    "tests/configurations/aws-s3/error-handling/unknown-auth-type.ini",
    "tests/configurations/aws-s3/error-handling/access-key-without-secret.ini",
]


@pytest.mark.parametrize(
    "config_file",
    CONFIG_FILES_KEY_NOT_FOUND,
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
    CONFIG_FILES_DELETE,
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


@pytest.mark.parametrize("config_file", CONFIG_FILES_AUTH_ERROR)
def test_unknown_auth_type(config_file):
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthError):
        cshelve.open(config_file)
