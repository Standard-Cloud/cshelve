"""
Encryption module for cshelve.
"""
import os
import struct
from collections import namedtuple
from functools import partial
from logging import Logger
from typing import Dict

from ._data_processing import DataProcessing, SIGNATURES
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
DATA_PROCESSING_NAME = SIGNATURES["ENCRYPTION"]


# Normally the 'tag' uses 16 bytes and the 'nonce' 12 bytes.
# But, for security and future-proofing, we keep their lengths in this dedicated data structure.
# We also keep the algorithm as an unsigned char.
MessageDetails = namedtuple(
    "MessageDetails",
    ["algorithm", "len_tag", "len_nonce", "ciphered_message"],
)
# Holds the encrypted message.
CipheredMessage = namedtuple("CipheredMessage", ["tag", "nonce", "encrypted_data"])


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
        data_processing.add_pre_processing(DATA_PROCESSING_NAME, crypt_fct)
        data_processing.add_post_processing(DATA_PROCESSING_NAME, decrypt_fct)
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

    cipher = CipheredMessage(tag=tag, nonce=cipher.nonce, encrypted_data=encrypted_data)

    md = MessageDetails(
        algorithm=signature,
        len_tag=len(tag),
        len_nonce=len(cipher.nonce),
        ciphered_message=cipher.tag + cipher.nonce + cipher.encrypted_data,
    )

    return struct.pack(
        f"<bbb{len(md.ciphered_message)}s",
        md.algorithm,
        md.len_tag,
        md.len_nonce,
        md.ciphered_message,
    )


def _decrypt(signature, AES, key: bytes, data: bytes) -> bytes:
    md = _extract_message_details(signature, data)
    cm = _extract_ciphered_message(md)
    return _decrypt_data(AES, key, cm)


def _extract_message_details(signature, data: bytes) -> MessageDetails:
    message_len = len(data) - 3  # 3 bytes for the MessageInformation structure (b)

    if message_len > 1:
        md = MessageDetails._make(struct.unpack(f"<bbb{message_len}s", data))

        if md.algorithm != signature:
            raise EncryptedDataCorruptionError(
                "Algorithm used for the encryption is not the expected one."
            )

        return md

    raise EncryptedDataCorruptionError("The encrypted data is corrupted.")


def _extract_ciphered_message(md: MessageDetails) -> CipheredMessage:
    data_len = len(md.ciphered_message) - md.len_tag - md.len_nonce

    if data_len > 1:
        cm = CipheredMessage._make(
            struct.unpack(
                f"<{md.len_tag}s{md.len_nonce}s{data_len}s",
                md.ciphered_message,
            )
        )
        return cm

    raise EncryptedDataCorruptionError("The encrypted data is corrupted.")


def _decrypt_data(AES, key: bytes, cm: CipheredMessage) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX, nonce=cm.nonce)
    plaintext = cipher.decrypt(cm.encrypted_data)

    try:
        cipher.verify(cm.tag)
        return plaintext
    except ValueError:
        raise EncryptedDataCorruptionError("The encrypted data is corrupted.")
