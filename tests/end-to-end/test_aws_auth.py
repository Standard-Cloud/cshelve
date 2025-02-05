"""
All tests related to the authentication mechanism.
"""
import pytest

import cshelve

from helpers import unique_key


@pytest.mark.aws
@pytest.mark.parametrize(
    "config_file",
    [
        "tests/configurations/aws-s3/auth.ini",
    ],
)
def test_aws_authentication(config_file):
    """
    Test authentication methods.
    """
    with cshelve.open(config_file) as db:
        key = unique_key + "test_aws_authentication"
        data = "test_aws_authentication"

        # Write data to the DB.
        db[key] = data

        # Data must be accessible in the DB.
        assert db[key] == data

        # Delete the data from the DB.
        del db[key]

    db.close()


@pytest.mark.aws
@pytest.mark.skip(reason="not implemented")
def test_aws_authentication_read_only():
    """
    Test the read-only authentication.
    """
    can_write_config_file = "tests/configurations/azure-blob/writeable-anonymous.ini"
    read_only_config_file = "tests/configurations/azure-blob/anonymous.ini"

    key = unique_key + "test_authentication_read_only"
    data = "test_authentication_read_only"

    with cshelve.open(can_write_config_file) as db:
        # Write data to the DB.
        db[key] = data

    # The read-only flag is not mandatory, but the underlying implementation will raise an exception if we try to write.
    with cshelve.open(read_only_config_file) as db:
        # Data must be present in the DB.
        assert db[key] == data

    with cshelve.open(can_write_config_file) as db:
        # Delete the data from the DB.
        del db[key]

    db.close()
