"""
All tests related to the SFTP.
"""
from pathlib import Path
import pytest

import cshelve

from helpers import unique_key


@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth_error.ini",
    ],
)
def test_sftp_authentication(config_file):
    """
    Test authentication methods.
    """
    with pytest.raises(cshelve.AuthError):
        cshelve.open(config_file)


@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth.ini",
        "tests/configurations/sftp/auth_ssh_rsa.ini",
    ],
)
def test_sftp_auth_methods(config_file):
    """
    Test SFTP auth methods.
    """
    import os

    with cshelve.open(config_file) as db:
        key = f"{unique_key}-cshelve-{config_file}"
        data = "test_sftp_auth_methods"

        # Write data to the DB.
        db[key] = data

        # Data must be accessible in the DB.
        assert db[key] == data

        del db[key]

    db.close()


@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth.ini",
    ],
)
def test_sftp_recursion(config_file):
    """
    Test SFTP auth methods.
    """
    with cshelve.open(config_file) as db:
        key = f"{unique_key}-cshelve-{config_file}"
        folder = str(Path(key).parent)
        data = "test_sftp_recursion"

        # Write data to the DB.
        db[key] = data

        # Data must be accessible in the DB.
        assert db[key] == data

        # Can not delete the folder.
        with pytest.raises(cshelve.KeyNotFoundError):
            del db[folder]

        # delete the key.
        del db[key]

    db.close()
