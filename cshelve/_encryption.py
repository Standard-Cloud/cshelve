"""
Encryption module for cshelve.
"""
import os
from functools import partial
from logging import Logger
from typing import Dict

from ._data_processing import DataProcessing
from .exceptions import (
    UnknownEncryptionAlgorithmError,
    NoEncryptionKeyError,
    EncryptionKeyNotDefinedError,
)


# Key that can be defined in the INI file.
ALGORITHMS_NAME_KEY = "algorithm"
## User can provide the key via the ini file or env variable.
KEY_KEY = "key"
ENVIRONMENT_KEY = "environment_key"


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
        logger.info("No encryption algorithm specified.")
        return

    algorithm = config[ALGORITHMS_NAME_KEY]

    key = _get_key(logger, config)

    supported_algorithms = {
        "aes256": _aes256,
    }

    if encryption := supported_algorithms.get(algorithm):
        logger.debug(f"Configuring encryption algorithm: {algorithm}")
        crypt_fct, decrypt_fct = encryption(config, key)
        data_processing.add_pre_processing(crypt_fct)
        data_processing.add_post_processing(decrypt_fct)
        logger.debug(f"Encryption algorithm {algorithm} configured.")
    else:
        raise UnknownEncryptionAlgorithmError(
            f"Unsupported encryption algorithm: {algorithm}"
        )


def _get_key(logger, config) -> bytes:
    if env_key := config.get(ENVIRONMENT_KEY):
        if key := os.environ.get(env_key):
            return key.encode()
        logger.error(
            f"Encryption key is configured to use use environment variable but environment variable '{ENVIRONMENT_KEY}' doesn't not exists."
        )
        raise EncryptionKeyNotDefinedError(
            f"Environment variable '{ENVIRONMENT_KEY}' not found."
        )

    if key := config.get(KEY_KEY):
        logger.info(
            "Encryption is based on a key defined in the config file and not an environment variable."
        )
        return key.encode()

    logger.error("Encryption is specified without key.")
    raise NoEncryptionKeyError("Encryption is specified without key.")


def _aes256(config: Dict[str, str], key: bytes):
    """
    Configure aes256 encryption.
    """
    from Crypto.Cipher import AES

    crypt = partial(_crypt, AES, key)
    decrypt = partial(_decrypt, AES, key)

    return crypt, decrypt


def _crypt(AES, key: bytes, data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    res = bytes()
    res += tag
    res += cipher.nonce
    res += ciphertext

    return res


def _decrypt(AES, key: bytes, data: bytes) -> bytes:
    tag = data[:16]
    nonce = data[16 : 16 + 12]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(data)

    return plaintext
