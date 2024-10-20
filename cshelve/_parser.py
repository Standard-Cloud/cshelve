"""
This module is responsible for parsing the configuration file.
It reads the configuration file and returns the provider and its configuration as a dictionary.
It also provides a function to determine if a local shelf should be used based on the file extension.

At this level, the only necessary configuration is the provider name.
Other configurations are loaded into a dictionary and passed to the provider for further configuration.
"""
import configparser
from typing import Dict, Tuple


# Default ini section containing the provider and its configuration.
DEFAULT_CONFIG_STORE = "default"
# Key containing the provider name.
PROVIDER_KEY = "provider"


def use_local_shelf(filename: str) -> bool:
    """
    If the user specify a filename with an extension different of '.ini', a local shelf (the standard library) must be used.
    """
    return not filename.endswith(".ini")


def load(filename: str) -> Tuple[str, Dict[str, str]]:
    """
    Load the configuration file and return it as a dictionary.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    c = config[DEFAULT_CONFIG_STORE]
    return c[PROVIDER_KEY], c
