"""
Depending on the filename, either the native shelve module or the cloud shelve module is used.
The cloud shelve module is used when the filename has a specific extension, and we must ensure that the correct module is used.
"""
from cshelve._parser import load, use_local_shelf


def test_use_local_shelf():
    """
    If the filename is not finishing by '.ini', the default shelve module must be used.
    """
    fallback_default_module = ["test.sqlite3", "test.db", "test.dat"]

    for filename in fallback_default_module:
        assert use_local_shelf(filename) is True
        # assert use_local_shelf(Path(filename)) is True


def test_use_cloud_shelf():
    """
    If the filename is finishing by '.ini', the cloud shelve module must be used.
    """
    cloud_module = ["test.ini", "cloud.ini", "test.cloud.ini"]

    for filename in cloud_module:
        assert use_local_shelf(filename) is False


def test_azure_configuration():
    """
    Load the Azure configuration file and return it as a dictionary.
    """
    provider, config = load("tests/configurations/azure-blob/simulator/standard.ini")

    assert provider == "azure-blob"
    assert config["auth_type"] == "connection_string"
    assert config["environment_key"] == "AZURE_STORAGE_CONNECTION_STRING"
    assert config["container_name"] == "standard"
