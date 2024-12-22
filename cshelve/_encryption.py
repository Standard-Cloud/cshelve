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
    MissingEncryptionKeyError,
    EncryptedDataCorruptionError,
)


# Key that can be defined in the INI file.
ALGORITHMS_NAME_KEY = "algorithm"
# User can provide the key via the INI file or environment variable.
KEY_KEY = "key"
ENVIRONMENT_KEY = "environment_key"


# Normally the 'tag' uses 16 bytes and the 'nonce' 12 bytes.
# But, for security and future-proofing, we keep their lengths in this dedicated data structure.
# We also keep the algorithm as an unsigned char.
EncryptedMessageInformation = namedtuple(
    "EncryptedMessageInformation",
    ["algorithm", "len_tag", "len_nonce", "encrypted_message"],
)
# Holds the encrypted message.
EncryptedMessage = namedtuple("EncryptedMessage", ["tag", "nonce", "encrypted_data"])


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

    if algorithm in supported_algorithms:
        fct, algo_signature = supported_algorithms[algorithm]
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
            f"Encryption key is configured to use the environment variable but the environment variable '{env_key}' does not exist."
        )
        raise MissingEncryptionKeyError(
            f"Environment variable '{ENVIRONMENT_KEY}' not found."
        )

    if key := config.get(KEY_KEY):
        logger.info(
            "Encryption is based on a key defined in the config file and not an environment variable."
        )
        return key.encode()

    logger.error("Encryption is specified without a key.")
    raise MissingEncryptionKeyError("Encryption is specified without a key.")


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

    encrypted_message = EncryptedMessage(
        tag=tag, nonce=cipher.nonce, encrypted_data=encrypted_data
    )

    encrypted_message_information = EncryptedMessageInformation(
        algorithm=signature,
        len_tag=len(tag),
        len_nonce=len(cipher.nonce),
        encrypted_message=encrypted_message.tag
        + encrypted_message.nonce
        + encrypted_message.encrypted_data,
    )

    return struct.pack(
        f"<bbb{len(encrypted_message_information.encrypted_message)}s",
        encrypted_message_information.algorithm,
        encrypted_message_information.len_tag,
        encrypted_message_information.len_nonce,
        encrypted_message_information.encrypted_message,
    )


def _decrypt(signature, AES, key: bytes, data: bytes) -> bytes:
    message_information = _extract_encrypted_message_information(signature, data)
    message = _extract_encrypted_message(message_information)
    return _decrypt_data(AES, key, message)


def _extract_encrypted_message_information(
    signature, data: bytes
) -> EncryptedMessageInformation:
    message_len = len(data) - 3  # 3 bytes for the MessageInformation structure (b)

    if message_len > 1:
        info = EncryptedMessageInformation._make(
            struct.unpack(f"<bbb{message_len}s", data)
        )

        if info.algorithm != signature:
            raise EncryptedDataCorruptionError(
                "Algorithm used for the encryption is not the expected one."
            )

        return info

    raise EncryptedDataCorruptionError("The encrypted data is corrupted.")


def _extract_encrypted_message(info: EncryptedMessageInformation) -> EncryptedMessage:
    encrypted_data_len = len(info.encrypted_message) - info.len_tag - info.len_nonce

    if encrypted_data_len > 1:
        encrypted_message = EncryptedMessage._make(
            struct.unpack(
                f"<{info.len_tag}s{info.len_nonce}s{encrypted_data_len}s",
                info.encrypted_message,
            )
        )
        return encrypted_message

    raise EncryptedDataCorruptionError("The encrypted data is corrupted.")


def _decrypt_data(AES, key: bytes, message: EncryptedMessage) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX, nonce=message.nonce)
    plaintext = cipher.decrypt(message.encrypted_data)

    try:
        cipher.verify(message.tag)
        return plaintext
    except ValueError:
        raise EncryptedDataCorruptionError("The encrypted data is corrupted.")
