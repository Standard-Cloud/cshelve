import sys
from unittest.mock import Mock
import pytest
from cshelve._sftp import SFTP


class DummyLogger:
    def debug(self, msg):
        pass

    def error(self, msg):
        pass

    def info(self, msg):
        pass


def test_importerror_when_paramiko_missing(monkeypatch):
    """
    Test that ImportError is raised if paramiko is not installed when accessing SFTP._paramiko.
    This test restores sys.modules after execution to avoid impacting other tests.
    """
    # Save and remove paramiko from sys.modules if present
    paramiko_saved = sys.modules.pop("paramiko", None)
    # Patch __import__ to raise ImportError for paramiko
    orig_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "paramiko":
            raise ImportError("No module named paramiko")
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    try:
        sftp = SFTP(DummyLogger())
        with pytest.raises(ImportError, match="paramiko"):
            _ = sftp._paramiko()
    finally:
        # Restore sys.modules to avoid impacting other tests
        if paramiko_saved is not None:
            sys.modules["paramiko"] = paramiko_saved
        else:
            sys.modules.pop("paramiko", None)


def test_accept_unknown_host_keys_can_be_overridden():
    """
    Test that accept_unknown_host_keys can be set to True via configure_default.
    """
    default_params = {
        "hostname": "host",
        "port": "22",
        "username": "user",
        "password": "pass",
        "auth_type": "password",
    }
    sftp = SFTP(DummyLogger())
    config = {**default_params, "accept_unknown_host_keys": "true"}
    sftp.configure_default(config)
    sftp.set_provider_params({})
    assert sftp.accept_unknown_host_keys is True

    sftp2 = SFTP(DummyLogger())
    config2 = {**default_params, "accept_unknown_host_keys": "false"}
    sftp2.configure_default(config2)
    sftp2.set_provider_params({})
    assert sftp2.accept_unknown_host_keys is False


def test_accept_unknown_host_keys_can_be_overridden_with_set_provider_params():
    """
    Test that accept_unknown_host_keys can be set via set_provider_params and that precedence is correct.
    - If configure_default sets accept_unknown_host_keys, set_provider_params should not override it.
    - If configure_default does not set accept_unknown_host_keys, set_provider_params should set it if provided.
    - If neither sets it, default should be False.
    """
    default_params = {
        "hostname": "host",
        "port": "22",
        "username": "user",
        "password": "pass",
        "auth_type": "password",
    }
    # Case 1: configure_default sets to false, set_provider_params tries to set to True (should remain False)
    sftp = SFTP(DummyLogger())
    sftp.configure_default({**default_params, "accept_unknown_host_keys": "false"})
    sftp.set_provider_params({"accept_unknown_host_keys": True, **default_params})
    assert sftp.accept_unknown_host_keys is False

    # Case 2: configure_default sets to true, set_provider_params tries to set to False (should remain True)
    sftp2 = SFTP(DummyLogger())
    sftp2.configure_default({**default_params, "accept_unknown_host_keys": "true"})
    sftp2.set_provider_params({"accept_unknown_host_keys": False, **default_params})
    assert sftp2.accept_unknown_host_keys is True

    # Case 3: configure_default does not set, set_provider_params sets to True (should be True)
    sftp3 = SFTP(DummyLogger())
    sftp3.configure_default(default_params)
    sftp3.set_provider_params({"accept_unknown_host_keys": True, **default_params})
    assert sftp3.accept_unknown_host_keys is True

    # Case 4: configure_default does not set, set_provider_params sets to False (should be False)
    sftp4 = SFTP(DummyLogger())
    sftp4.configure_default(default_params)
    sftp4.set_provider_params({"accept_unknown_host_keys": False, **default_params})
    assert sftp4.accept_unknown_host_keys is False

    # Case 5: neither sets, should be False
    sftp5 = SFTP(DummyLogger())
    sftp5.configure_default(default_params)
    sftp5.set_provider_params(default_params)
    assert sftp5.accept_unknown_host_keys is False


def test_set_provider_params_assigns_timeouts():
    """
    Test that set_provider_params assigns timeout-related parameters correctly.
    """
    sftp = SFTP(DummyLogger())
    config = {
        "hostname": "host",
        "port": "22",
        "username": "user",
        "password": "pass",
        "auth_type": "password",
    }
    sftp.configure_default(config)
    provider_params = {
        "timeout": 10,
        "banner_timeout": 20,
        "auth_timeout": 30,
        "channel_timeout": 40,
    }
    sftp.set_provider_params(provider_params)
    # Patch SFTP._paramiko to return a mock paramiko module
    paramiko_mock = Mock()
    ssh_client_mock = Mock()
    paramiko_mock.client.SSHClient.return_value = ssh_client_mock
    sftp._paramiko = lambda: paramiko_mock

    # Access sftp_client to trigger connect
    _ = sftp.sftp_client

    args = ssh_client_mock.connect.call_args[1]
    print(args)
    assert args["timeout"] == provider_params["timeout"]
    assert args["banner_timeout"] == provider_params["banner_timeout"]
    assert args["channel_timeout"] == provider_params["channel_timeout"]
    assert args["auth_timeout"] == provider_params["auth_timeout"]


def test_sftp_client_connect_uses_default_timeouts():
    """
    Test that sftp_client passes default timeout values to SSHClient.connect when not set in provider_params.
    """
    from cshelve._sftp import DEFAULT_TIMEOUT

    sftp = SFTP(DummyLogger())
    config = {
        "hostname": "host",
        "port": "22",
        "username": "user",
        "password": "pass",
        "auth_type": "password",
    }
    sftp.configure_default(config)
    sftp.set_provider_params({})
    paramiko_mock = Mock()
    ssh_client_mock = Mock()
    paramiko_mock.client.SSHClient.return_value = ssh_client_mock
    sftp._paramiko = lambda: paramiko_mock

    _ = sftp.sftp_client

    args = ssh_client_mock.connect.call_args[1]
    assert args["timeout"] == DEFAULT_TIMEOUT
    assert args["banner_timeout"] == DEFAULT_TIMEOUT
    assert args["auth_timeout"] == DEFAULT_TIMEOUT
