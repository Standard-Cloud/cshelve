"""
All tests related to the SFTP.
"""
import pytest

import cshelve

from helpers import unique_key


@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth.ini",
    ],
)
def test_sftp_authentication(config_file):
    """
    Test authentication methods.
    """
    with cshelve.open(config_file) as db:
        key = unique_key + "test_sftp_authentication"
        data = "test_sftp_authentication"

        # Write data to the DB.
        db[key] = data

        # Data must be accessible in the DB.
        assert db[key] == data

        # Delete the data from the DB.
        del db[key]

    db.close()


@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth.ini",
    ],
)
def test_sftp_authentication(config_file):
    """
    Test authentication methods.
    """
    provider_params = {
        "username": "wrong",
        "password": "wrong",
    }

    with pytest.raises(cshelve.AuthArgumentError):
        cshelve.open(config_file, provider_params=provider_params)

@pytest.mark.sftp
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/sftp/auth.ini",
    ],
)
def test_sftp_recursion_folder(config_file):
    """
    Test SFTP folder recursion.
    """
    with cshelve.open(config_file) as db:
        first_folder = "first_folder"
        key = first_folder + "/second_folder/third_folder" + unique_key + "test_sftp_recursion_folder"
        data = "test_sftp_recursion_folder"

        # Write data to the DB.
        db[key] = data

        # Data must be accessible in the DB.
        assert db[key] == data

        # Delete all the folders and data.
        del db[first_folder]

    db.close()
