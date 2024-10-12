import configparser
from typing import Dict, Tuple


DEFAULT_CONFIG_STORE = 'default'
PROVIDER_KEY = 'provider'


def use_local_shelf(filename: str) -> bool:
    """
    If the user specify a filename with an extension different of '.ini', a local shelf (the standard library) must be used.
    """
    return not filename.endswith('.ini')


def load(filename: str) -> Tuple[str, Dict[str, str]]:
    """
    Load the configuration file and return it as a dictionary.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    c = config[DEFAULT_CONFIG_STORE]
    return c[PROVIDER_KEY], c
