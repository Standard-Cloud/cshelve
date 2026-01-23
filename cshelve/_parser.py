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
from .exceptions import ConfigurationError


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
        "providers",
        "strategy",
        "use_pickle",
    ],
)


def _parse_ini_to_nested_dict(config_parser) -> dict:
    """
    Convert ConfigParser sections to nested dict using dot notation.
    Sections like [provider.encryption] become config['provider']['encryption'].
    """
    result = {}

    for section in config_parser.sections():
        if "." in section:
            # e.g., "azure.encryption" -> parent="azure", child="encryption"
            parent, child = section.split(".", 1)
            if parent not in result:
                result[parent] = {}
            result[parent][child] = dict(config_parser[section])
        else:
            # Regular section at top level
            result[section] = dict(config_parser[section])

    return result


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
    # Convert flat section names with dots into nested dicts
    config = _parse_ini_to_nested_dict(config)

    return _load_configuration(logger, config)


def load_from_dict(logger: Logger, config: dict) -> Config:
    """
    Load the configuration from a dict and return it.
    """
    logger.debug(f"Loading configuration from a dict.")
    return _load_configuration(logger, config)


def _load_configuration(logger: Logger, config: dict) -> Config:
    c = config[DEFAULT_CONFIG_STORE]

    # `provider` (single) and `providers` (multi) are mutually exclusive.
    if PROVIDER_KEY in c and PROVIDERS_KEY in c:
        raise ConfigurationError(
            "'provider' and 'providers' cannot be specified together in [default]."
        )

    # Check if multi-provider mode
    if PROVIDERS_KEY in c:
        logger.debug("Detected multi-provider configuration.")
        return _load_multi_provider_configuration(logger, config)
    else:
        logger.debug("Detected single-provider configuration.")
        return _load_single_provider_configuration(logger, config)


def _load_single_provider_configuration(logger: Logger, config: dict) -> Config:
    """
    Load configuration for single-provider mode.
    Transforms single-provider config dict into multi-provider format, then delegates to _load_multi_provider_configuration.
    """
    auto_generated_provider_name = "default_provider"
    transformed_config = {
        **config,
        auto_generated_provider_name: config[DEFAULT_CONFIG_STORE],
    }
    transformed_config[DEFAULT_CONFIG_STORE][
        PROVIDERS_KEY
    ] = auto_generated_provider_name

    logger.debug(f"Single-provider configuration transformed to multi-provider format.")
    return _load_multi_provider_configuration(logger, transformed_config)


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
        providers=provider_configs,
        strategy=strategy,
        use_pickle=c.get(USE_PICKLE, "true").lower() == "true",
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
        raise ConfigurationError(
            f"Provider section [{provider_name}] not found in configuration."
        )

    provider_section = config[provider_name]

    # Merge global settings with provider-specific overrides (nested dict access)
    logging_config = dict(global_logging)
    if LOGGING_KEY_STORE in provider_section:
        logging_config.update(provider_section[LOGGING_KEY_STORE])

    compression_config = dict(global_compression)
    if COMPRESSION_KEY_STORE in provider_section:
        compression_config.update(provider_section[COMPRESSION_KEY_STORE])

    encryption_config = dict(global_encryption)
    if ENCRYPTION_KEY_STORE in provider_section:
        encryption_config.update(provider_section[ENCRYPTION_KEY_STORE])

    provider_params = dict(global_provider_params)
    if PROVIDER_PARAMS in provider_section:
        provider_params.update(provider_section[PROVIDER_PARAMS])

    logger.debug(f"Loaded configuration for provider '{provider_name}'.")
    # Extract only scalar values for 'default' (skip nested dicts like compression, encryption, etc.)
    default_section = {
        k: v for k, v in provider_section.items() if not isinstance(v, dict)
    }
    return ProviderConfig(
        provider=provider_section[PROVIDER_KEY],
        default=from_env(default_section),
        logging=from_env(logging_config),
        compression=from_env(compression_config),
        encryption=from_env(encryption_config),
        provider_params=from_env(provider_params),
        use_versionning=provider_section.get(USE_VERSIONNING, "true").lower() == "true",
    )
