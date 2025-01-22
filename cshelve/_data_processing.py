"""
This module provides the DataProcessing class, which handles pre-processing and post-processing of data.

Examples:
    >>> dp = DataProcessing()
    >>> dp.add_pre_processing('add_1', lambda x: x + b'1')
    >>> dp.add_post_processing('add_2', lambda x: x + b'2')
    >>> pre_processed = dp.apply_pre_processing(b'0')
    >>> pre_processed
    b'01'
    >>> post_processed = dp.apply_post_processing(pre_processed)
    >>> post_processed
    b'012'
"""
from collections import namedtuple
from typing import Callable, List


_Process = namedtuple(
    "_Process",
    ["binary_signature", "function"],
)


# Algorithm signatures to applied to the data.
# Used with a XOR to ensure that the data is processed correctly.
SIGNATURES = {"COMPRESSION": 0b00000001, "ENCRYPTION": 0b00000010}


class DataProcessing:
    """
    A class to handle pre-processing and post-processing of data.
    """

    def __init__(self):
        """
        Initializes the DataProcessing class.

        Examples:
        >>> dp = DataProcessing()
        >>> dp.pre_processing
        []
        >>> dp.post_processing
        []
        """
        self.pre_processing: List[_Process] = []
        self.post_processing: List[_Process] = []

    def add_pre_processing(
        self, binary_signature: bytes, func: Callable[[bytes], bytes]
    ) -> None:
        """
        Adds a function to the pre-processing list.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001 # Please use the SIGNATURES dict
        >>> dp.add_pre_processing(signature, lambda x: x + 1)
        >>> len(dp.pre_processing)
        1
        """
        self.pre_processing.append(
            _Process(binary_signature=binary_signature, function=func)
        )

    def add_post_processing(
        self, binary_signature: bytes, func: Callable[[bytes], bytes]
    ) -> None:
        """
        Adds a function to the post-processing list.

        Args:
        func (function): A function to add to the post-processing list.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001 # Please use the SIGNATURES dict
        >>> dp.add_post_processing(signature, lambda x: x * 2)
        >>> len(dp.post_processing)
        1
        """
        self.post_processing.append(
            _Process(binary_signature=binary_signature, function=func)
        )

    def apply_pre_processing(self, data: bytes) -> bytes:
        """
        Applies all pre-processing functions to the data.

        Args:
        data: The data to process.

        Returns:
        The processed data.

        Examples:
        >>> dp = DataProcessing()
        >>> signature_add = 0b00000001 # Please use the SIGNATURES dict
        >>> signature_mult = 0b00000010 # Please use the SIGNATURES dict
        >>> dp.add_pre_processing(SIGNATURES["COMPRESSION"], lambda x: x + 1)
        >>> dp.add_pre_processing('mult_by_2', lambda x: x * 2)
        >>> dp.apply_pre_processing(1)
        4
        """
        for p in self.pre_processing:
            data = p.function(data)
        return data

    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Applies all post-processing functions to the data.

        Args:
        data: The data to process.

        Returns:
        The processed data.

        Examples:
        >>> dp = DataProcessing()
        >>> signature_minus = 0b00000001 # Please use the SIGNATURES dict
        >>> signature_div = 0b00000010 # Please use the SIGNATURES dict
        >>> dp.add_post_processing(signature_div, lambda x: x / 2)
        >>> dp.add_post_processing(signature_minus, lambda x: x - 1)
        >>> dp.apply_post_processing(4)
        1.0
        """
        for p in self.post_processing:
            data = p.function(data)
        return data

    def pre_processing_signature(self):
        return [p.binary_signature for p in self.pre_processing]
