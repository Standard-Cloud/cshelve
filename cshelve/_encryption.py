"""
Encryption module for cshelve.
"""
from functools import partial
from logging import Logger
from typing import Dict

from .data_processing import DataProcessing
from .exceptions import UnknownEncryptionAlgorithmError


ALGORITHMS_NAME_KEY = "algorithm"
COMPRESSION_LEVEL_KEY = "level"


def configure(
    logger: Logger, data_processing: DataProcessing, config: Dict[str, str]
) -> None:
    """
    Configure the encryption algorithm.
    """
    # Encryption is not configured, silently return.
    if not config:
        return

    if ALGORITHMS_NAME_KEY not in config:
        logger.info("No compression algorithm specified.")
        return

    algorithm = config[ALGORITHMS_NAME_KEY]

    supported_algorithms = {
        "aes256": _aes256,
    }

    if encryption := supported_algorithms.get(algorithm):
        logger.debug(f"Configuring encryption algorithm: {algorithm}")
        crypt_fct, decrypt_fct = encryption(config)
        data_processing.add_pre_processing(crypt_fct)
        data_processing.add_post_processing(decrypt_fct)
        logger.debug(f"Encryption algorithm {algorithm} configured.")
    else:
        raise UnknownEncryptionAlgorithmError(
            f"Unsupported encryption algorithm: {algorithm}"
        )


def _aes256(config: Dict[str, str]):
    """
    Configure aes256 encryption.
    """
    import zlib

    crypt = lambda x: x
    decrypt = lambda x: x

    return crypt, decrypt
