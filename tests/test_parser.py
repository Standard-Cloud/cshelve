from cshelve._parser import use_local_shelf, load


def test_use_local_shelf():
    """
    If the filename is not finishing by '.ini', the default shelve module must be used.
    """
    fallback_default_module = ['test.sqlite3', 'test.db', 'test.dat']
    
    for filename in fallback_default_module:
        assert use_local_shelf(filename) is True


def test_use_cloud_shelf():
    """
    If the filename is finishing by '.ini', the cloud shelve module must be used.
    """
    cloud_module = ['test.ini', 'cloud.ini', 'test.cloud.ini']
    
    for filename in cloud_module:
        assert use_local_shelf(filename) is False


def test_azure_configuration():
    """
    Load the Azure configuration file and return it as a dictionary.
    """
    provider, config = load('tests/configurations/azure.ini')

    assert provider == 'azure'
    assert config['auth_type'] == 'passwordless'
    assert config['account_url'] == 'https://myaccount.blob.core.windows.net'
    assert config['container_name'] == 'mycontainer'
