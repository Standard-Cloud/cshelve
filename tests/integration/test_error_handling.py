import pytest

import cshelve

from helpers import write_data, del_data


def test_key_not_found():
    """
    Ensure KeyError is raised when key is not found.
    """
    db = cshelve.open("tests/configurations/azure-integration/standard.ini")

    with pytest.raises(cshelve.KeyNotFoundError):
        db["test_key_not_found"]

    db.close()


def test_raise_delete_missing_object():
    """
    Ensure delete an non-existing object raises KeyError.
    """
    db = cshelve.open("tests/configurations/azure-integration/standard.ini")

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
            "tests/configurations/azure-integration/error-handling/unknown-auth-type.ini"
        )


def test_no_connection_string_key_auth_type():
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthArgumentError):
        cshelve.open(
            "tests/configurations/azure-integration/error-handling/connection-string-without-connection-string.ini"
        )


def test_no_connection_string_in_env():
    """
    Ensure exception is raised when auth type is unknown.
    """
    with pytest.raises(cshelve.AuthArgumentError):
        cshelve.open(
            "tests/configurations/azure-integration/error-handling/connection-string-without-env-var.ini"
        )
