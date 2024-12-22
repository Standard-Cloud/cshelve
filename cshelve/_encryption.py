"""
Encryption module for cshelve.
"""
import os
import struct
from collections import namedtuple
from functools import partial
from logging import Logger
from typing import Dict

from ._data_processing import DataProcessing
from .exceptions import (
    UnknownEncryptionAlgorithmError,
    NoEncryptionKeyError,
    DataCorruptionError,
)


# Key that can be defined in the INI file.
ALGORITHMS_NAME_KEY = "algorithm"
## User can provide the key via the ini file or env variable.
KEY_KEY = "key"
ENVIRONMENT_KEY = "environment_key"


# Normally the 'tag' is using 16 bytes and the 'nonce' 12 bytes.
# But, by security and for the futur, we keep their length in a this dedicated data structure.
# With also keep the algorithm as a unsigned char.
MessageInformation = namedtuple(
    "MessageInformation", ["algorithm", "len_tag", "len_nonce", "message"]
)
# Hold the encrypted message.
Message = namedtuple("Message", ["tag", "nonce", "encrypted_data"])


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
        "aes256": (_aes256, 1),
    }

    if algorithm := supported_algorithms.get(algorithm):
        fct, algo_signature = algorithm
        logger.debug(f"Configuring encryption algorithm: {algorithm}")
        crypt_fct, decrypt_fct = fct(algo_signature, config, key)
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
        raise NoEncryptionKeyError(
            f"Environment variable '{ENVIRONMENT_KEY}' not found."
        )

    if key := config.get(KEY_KEY):
        logger.info(
            "Encryption is based on a key defined in the config file and not an environment variable."
        )
        return key.encode()

    logger.error("Encryption is specified without key.")
    raise NoEncryptionKeyError("Encryption is specified without key.")


def _aes256(signature, config: Dict[str, str], key: bytes):
    """
    Configure aes256 encryption.
    """
    from Crypto.Cipher import AES

    crypt = partial(_crypt, signature, AES, key)
    decrypt = partial(_decrypt, signature, AES, key)

    return crypt, decrypt


def _crypt(signature, AES, key: bytes, data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX)
    encrypted_data, tag = cipher.encrypt_and_digest(data)

    message = Message(tag=tag, nonce=cipher.nonce, encrypted_data=encrypted_data)

    info = MessageInformation(
        algorithm=signature,
        len_tag=len(tag),
        len_nonce=len(cipher.nonce),
        message=message.tag + message.nonce + message.encrypted_data,
    )

    return struct.pack(
        f"<bbb{len(info.message)}s",
        info.algorithm,
        info.len_tag,
        info.len_nonce,
        info.message,
    )


def _decrypt(signature, AES, key: bytes, data: bytes) -> bytes:
    message_len = len(data) - 3  # 3 bytes (b)
    info = MessageInformation._make(struct.unpack(f"<bbb{message_len}s", data))

    if info.algorithm != signature:
        raise DataCorruptionError("Algorithm used for the encryption is not AES256.")

    encrypted_data_len = len(info.message) - info.len_tag - info.len_nonce
    message = Message._make(
        struct.unpack(
            f"<{info.len_tag}s{info.len_nonce}s{encrypted_data_len}s", info.message
        )
    )

    cipher = AES.new(key, AES.MODE_EAX, nonce=message.nonce)

    plaintext = cipher.decrypt(message.encrypted_data)

    try:
        cipher.verify(message.tag)
    except ValueError:
        raise DataCorruptionError("The encrypted data was modified.")

    return plaintext
