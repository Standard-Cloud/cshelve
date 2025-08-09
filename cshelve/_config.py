import os
from typing import Any, Dict, Union

from .exceptions import ConfigurationError


def from_env(d: Union[Dict[str, Any], Any]) -> Union[Dict[str, Any], Any]:
    """
    Return a dictionary with the environment variables that are present in the input dictionary.
    A key is considered as an environment variable if it starts with '$'.
    If the input is a string, return the corresponding environment variable.
    """
    if d is None:
        return d
    if isinstance(d, str):
        return _get_from_env(d[1:]) if d.startswith("$") else d
    return {
        k: _get_from_env(v[1:]) if isinstance(v, str) and v.startswith("$") else v
        for k, v in d.items()
    }


def _get_from_env(env_var: str) -> str:
    try:
        return os.environ[env_var]
    except:
        raise ConfigurationError(f"Environment variable {env_var} not found.")
