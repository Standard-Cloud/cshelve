import pytest

from cshelve._config import from_env
from cshelve import ConfigurationError


def test_from_env_with_env_variables(monkeypatch):
    monkeypatch.setenv("TEST_ENV_VAR", "test_value")
    input_dict = {"key1": "$TEST_ENV_VAR", "key2": "value2"}
    expected_output = {"key1": "test_value", "key2": "value2"}
    assert from_env(input_dict) == expected_output


def test_from_env_without_env_variables():
    input_dict = {"key1": "value1", "key2": "value2"}
    expected_output = {"key1": "value1", "key2": "value2"}
    assert from_env(input_dict) == expected_output


def test_from_env_with_missing_env_variable(monkeypatch):
    monkeypatch.delenv("MISSING_ENV_VAR", raising=False)
    input_dict = {"key1": "$MISSING_ENV_VAR", "key2": "value2"}
    with pytest.raises(ConfigurationError):
        from_env(input_dict)
    with pytest.raises(ConfigurationError):
        from_env("$MISSING_ENV_VAR")


def test_from_env_with_string_env_variable(monkeypatch):
    monkeypatch.setenv("TEST_ENV_VAR", "test_value")
    input_str = "$TEST_ENV_VAR"
    expected_output = "test_value"
    assert from_env(input_str) == expected_output


def test_from_env_with_string_non_env_variable():
    input_str = "TEST_ENV_VAR"
    expected_output = "TEST_ENV_VAR"
    assert from_env(input_str) == expected_output


def test_from_env_with_none():
    assert from_env(None) == None
