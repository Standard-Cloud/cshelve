"""
This module provides the DataProcessing class, which handles pre-processing and post-processing of data.

Examples:
    >>> dp = DataProcessing(logger=None)
    >>> dp.add(lambda x: x + b'1', lambda x: x[:-1], 'a')
    >>> dp.add(lambda x: x + b'2', lambda x: x[:-1], 'b')
    >>> assert b'42' == dp.apply_post_processing(dp.apply_pre_processing(b'42'))
"""
from collections import namedtuple
import struct
from typing import Callable, List

from .exceptions import DataProcessingSignatureError


_DataProcessing = namedtuple("DataProcessing", ["post_processes", "data"])
_DataProcessingMetadata = namedtuple(
    "DataProcessingMetadata", ["len_post_processes", "len_data", "data_processing"]
)

# Algorithm signatures to applied to the data.
SIGNATURES = {"COMPRESSION": b"c", "ENCRYPTION": b"e"}


class DataProcessing:
    """
    A class to handle pre-processing and post-processing of data.
    """

    def __init__(self, logger):
        """
        Initializes the DataProcessing class.
        """
        self.logger = logger
        self.pre_processing: List[Callable[[bytes], bytes]] = []
        self.post_processing: List[Callable[[bytes], bytes]] = []
        self.post_processing_signature = b""

    def add(
        self,
        pre_processing: Callable[[bytes], bytes],
        post_processing: Callable[[bytes], bytes],
        signature: bytes,
    ):
        """
        Adds functions for processing.
        The signature is used to generate the signature of the data. If the processing functions don't interact with the data, it should be set to None.
        """
        self.pre_processing.append(pre_processing)
        # Add to the beginning of the list to ensure the order is correct.
        self.post_processing.insert(0, post_processing)
        self.post_processing_signature = signature + self.post_processing_signature

    def apply_pre_processing(self, data: bytes) -> bytes:
        """
        Applies all pre-processing functions to the data.
        """
        for fct in self.pre_processing:
            data = fct(data)

        len_data_proc_signature = len(self.post_processing_signature)
        len_data = len(data)

        data_processing = struct.pack(
            f"<{len_data_proc_signature}s{len_data}s",
            self.post_processing_signature,
            data,
        )
        # We are using unsigned long long due to the potential size of the data.
        metadata = struct.pack(
            f"<QQ{len_data_proc_signature + len_data}s",
            len_data_proc_signature,
            len_data,
            data_processing,
        )
        return metadata

    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Applies all post-processing functions to the data.
        """
        metadata = _DataProcessingMetadata._make(
            struct.unpack(f"<QQ{len(data) - 2 * 8}s", data)
        )
        data_processing = _DataProcessing._make(
            struct.unpack(
                f"<{metadata.len_post_processes}s{metadata.len_data}s",
                metadata.data_processing,
            )
        )

        if data_processing.post_processes != self.post_processing_signature:
            self.logger.error(
                "Data processing signature: %s, expected: %s",
                data_processing.post_processes,
                self.post_processing_signature,
            )
            raise DataProcessingSignatureError("Wrong data processing signature.")

        data = data_processing.data
        for fct in self.post_processing:
            data = fct(data)
        return data
