"""
This module is responsible for parsing the configuration file.
It reads the configuration file and returns the provider and its configuration as a dictionary.
It also provides a function to determine if a local shelf should be used based on the file extension.

At this level, the only necessary configuration is the provider name.
Other configurations are loaded into a dictionary and passed to the provider for further configuration.
"""
from logging import Logger
from collections import namedtuple
import configparser
from pathlib import Path

from ._config import from_env


# Default ini section containing the provider and its configuration.
DEFAULT_CONFIG_STORE = "default"
# Key containing the provider name.
PROVIDER_KEY = "provider"
# Key for multi-provider mode - list of provider names.
PROVIDERS_KEY = "providers"
# Key for multi-provider strategy.
STRATEGY_KEY = "strategy"
# Key indicating if the usage of pickle is activated (True by default).
USE_PICKLE = "use_pickle"
# Key indicating if the usage of the versionning is activated (True by default).
USE_VERSIONNING = "use_versionning"
# Logging configuration section.
LOGGING_KEY_STORE = "logging"
# Compression configuration section.
COMPRESSION_KEY_STORE = "compression"
# Encryption configuration section.
ENCRYPTION_KEY_STORE = "encryption"
# Provider parameter section.
PROVIDER_PARAMS = "provider_params"

# Tuple containing a single provider's configuration (used in multi-provider mode).
ProviderConfig = namedtuple(
    "ProviderConfig",
    [
        "provider",
        "use_pickle",
        "use_versionning",
        "default",
        "logging",
        "compression",
        "encryption",
        "provider_params",
    ],
)

# Tuple containing the top-level configuration.
# For single-provider mode: provider, use_pickle, etc. are set; strategy and providers are None.
# For multi-provider mode: strategy and providers are set; provider may be None.
Config = namedtuple(
    "Config",
    [
        "provider",
        "use_pickle",
        "use_versionning",
        "default",
        "logging",
        "compression",
        "encryption",
        "provider_params",
        "strategy",
        "providers",
    ],
)


def use_local_shelf(filename: Path) -> bool:
    """
    If the user specify a filename with an extension different of '.ini', a local shelf (the standard library) must be used.
    """
    return not filename.suffix == ".ini"


def load_from_file(logger: Logger, filename: Path) -> Config:
    """
    Load the configuration file and return it as a dictionary.
    """
    logger.debug(f"Loading configuration file: {filename}.")
    config = configparser.ConfigParser()
    config.read(filename)

    return _load_configuration(logger, config)


def load_from_dict(logger: Logger, config: dict) -> Config:
    """
    Load the configuration from a dict and return it.
    """
    logger.debug(f"Loading configuration from a dict.")
    return _load_configuration(logger, config)


def _load_configuration(logger: Logger, config: dict) -> Config:
    c = config[DEFAULT_CONFIG_STORE]

    # Check if multi-provider mode
    if PROVIDERS_KEY in c:
        logger.debug("Detected multi-provider configuration.")
        return _load_multi_provider_configuration(logger, config)
    else:
        logger.debug("Detected single-provider configuration.")
        return _load_single_provider_configuration(logger, config)


def _load_single_provider_configuration(logger: Logger, config: dict) -> Config:
    """
    Load configuration for single-provider mode (backward compatible).
    """
    c = config[DEFAULT_CONFIG_STORE]
    logging_config = config[LOGGING_KEY_STORE] if LOGGING_KEY_STORE in config else {}
    compression_config = (
        config[COMPRESSION_KEY_STORE] if COMPRESSION_KEY_STORE in config else {}
    )
    encryption_config = (
        config[ENCRYPTION_KEY_STORE] if ENCRYPTION_KEY_STORE in config else {}
    )
    provider_params = config[PROVIDER_PARAMS] if PROVIDER_PARAMS in config else {}

    logger.debug(f"Single-provider configuration loaded.")
    return Config(
        provider=c[PROVIDER_KEY],
        default=from_env(dict(c)),
        logging=from_env(dict(logging_config)),
        compression=from_env(dict(compression_config)),
        encryption=from_env(dict(encryption_config)),
        provider_params=from_env(dict(provider_params)),
        # These configurations is checked here to avoid redundant checks.
        use_pickle=c.get(USE_PICKLE, "true").lower() == "true",
        use_versionning=c.get(USE_VERSIONNING, "true").lower() == "true",
        # Multi-provider fields are None for single-provider mode
        strategy=None,
        providers=None,
    )


def _load_multi_provider_configuration(logger: Logger, config: dict) -> Config:
    """
    Load configuration for multi-provider mode.
    """
    c = config[DEFAULT_CONFIG_STORE]

    # Parse provider names and strategy
    provider_names = [name.strip() for name in c[PROVIDERS_KEY].split(",")]
    strategy = c.get(STRATEGY_KEY, "all")

    # Global settings (used as defaults for all providers)
    global_logging = config[LOGGING_KEY_STORE] if LOGGING_KEY_STORE in config else {}
    global_compression = (
        config[COMPRESSION_KEY_STORE] if COMPRESSION_KEY_STORE in config else {}
    )
    global_encryption = (
        config[ENCRYPTION_KEY_STORE] if ENCRYPTION_KEY_STORE in config else {}
    )
    global_provider_params = (
        config[PROVIDER_PARAMS] if PROVIDER_PARAMS in config else {}
    )

    # Parse each provider configuration
    provider_configs = []
    for provider_name in provider_names:
        provider_config = _load_provider_config(
            logger,
            config,
            provider_name,
            global_logging,
            global_compression,
            global_encryption,
            global_provider_params,
        )
        provider_configs.append(provider_config)

    logger.debug(
        f"Multi-provider configuration loaded with {len(provider_configs)} providers."
    )
    return Config(
        provider=None,  # Not used in multi-provider mode
        default=from_env(dict(c)),
        logging=from_env(dict(global_logging)),
        compression=from_env(dict(global_compression)),
        encryption=from_env(dict(global_encryption)),
        provider_params=from_env(dict(global_provider_params)),
        use_pickle=c.get(USE_PICKLE, "true").lower() == "true",
        use_versionning=c.get(USE_VERSIONNING, "true").lower() == "true",
        strategy=strategy,
        providers=provider_configs,
    )


def _load_provider_config(
    logger: Logger,
    config: dict,
    provider_name: str,
    global_logging: dict,
    global_compression: dict,
    global_encryption: dict,
    global_provider_params: dict,
) -> ProviderConfig:
    """
    Load configuration for a single provider in multi-provider mode.
    Merges provider-specific settings with global defaults.
    """
    # Get provider's base configuration
    if provider_name not in config:
        raise ValueError(
            f"Provider section [{provider_name}] not found in configuration."
        )

    provider_section = config[provider_name]

    # Check for provider-specific overrides (e.g., [provider-name.compression])
    provider_logging_key = f"{provider_name}.{LOGGING_KEY_STORE}"
    provider_compression_key = f"{provider_name}.{COMPRESSION_KEY_STORE}"
    provider_encryption_key = f"{provider_name}.{ENCRYPTION_KEY_STORE}"
    provider_params_key = f"{provider_name}.{PROVIDER_PARAMS}"

    # Merge global settings with provider-specific overrides
    logging_config = dict(global_logging)
    if provider_logging_key in config:
        logging_config.update(config[provider_logging_key])

    compression_config = dict(global_compression)
    if provider_compression_key in config:
        compression_config.update(config[provider_compression_key])

    encryption_config = dict(global_encryption)
    if provider_encryption_key in config:
        encryption_config.update(config[provider_encryption_key])

    provider_params = dict(global_provider_params)
    if provider_params_key in config:
        provider_params.update(config[provider_params_key])

    logger.debug(f"Loaded configuration for provider '{provider_name}'.")
    return ProviderConfig(
        provider=provider_section[PROVIDER_KEY],
        default=from_env(dict(provider_section)),
        logging=from_env(logging_config),
        compression=from_env(compression_config),
        encryption=from_env(encryption_config),
        provider_params=from_env(provider_params),
        use_pickle=provider_section.get(USE_PICKLE, "true").lower() == "true",
        use_versionning=provider_section.get(USE_VERSIONNING, "true").lower() == "true",
    )
