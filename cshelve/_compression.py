"""
Compression module for cshelve.
"""
from functools import partial
from logging import Logger
from typing import Dict

from ._data_processing import DataProcessing, SIGNATURES
from .exceptions import UnknownCompressionAlgorithmError


ALGORITHMS_NAME_KEY = "algorithm"
COMPRESSION_LEVEL_KEY = "level"
DATA_PROCESSING_NAME = SIGNATURES["COMPRESSION"]


def configure(
    logger: Logger, data_processing: DataProcessing, config: Dict[str, str]
) -> None:
    """
    Configure the compression algorithm.
    """
    # Compression is not configured, silently return.
    if not config:
        return

    if ALGORITHMS_NAME_KEY not in config:
        logger.info("No compression algorithm specified.")
        return

    algorithm = config[ALGORITHMS_NAME_KEY]

    supported_algorithms = {
        "zlib": _zlib,
    }

    if compression := supported_algorithms.get(algorithm):
        logger.debug(f"Configuring compression algorithm: {algorithm}")
        compression_fct, decompression_fct = compression(config)
        data_processing.add(compression_fct, decompression_fct, DATA_PROCESSING_NAME)
        logger.debug(f"Compression algorithm {algorithm} configured.")
    else:
        raise UnknownCompressionAlgorithmError(
            f"Unsupported compression algorithm: {algorithm}"
        )


def _zlib(config: Dict[str, str]):
    """
    Configure zlib compression.
    """
    import zlib

    level = int(config.get(COMPRESSION_LEVEL_KEY, zlib.Z_DEFAULT_COMPRESSION))

    compress = partial(zlib.compress, level=level)
    decompress = partial(zlib.decompress)

    return compress, decompress
