"""
This module provides the DataProcessing class, which handles pre-processing and post-processing of data.

Examples:
    >>> dp = DataProcessing()
    >>> dp.add_pre_processing(lambda x: x + b'1', 0b00000001)
    >>> dp.add_post_processing(lambda x: x + b'2', 0b00000010)
    >>> pre_processed = dp.apply_pre_processing(b'0')
    >>> pre_processed
    b'01'
    >>> post_processed = dp.apply_post_processing(pre_processed)
    >>> post_processed
    b'012'
"""
from collections import namedtuple
from typing import Callable, List


_Process = namedtuple("Process", ["binary_signature", "function"])

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
        # XOR of all signatures to ensure that the data is processed correctly.
        self.signature = 0b0

    def add_pre_processing(
        self, func: Callable[[bytes], bytes], binary_signature: bytes = None
    ) -> None:
        """
        Adds a function to the pre-processing list.
        The binary_signature is used to generate the signature of the data. It the pre-processing function doesn't interact with the data, it should be set to None.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001 # Please use the SIGNATURES dict
        >>> dp.add_pre_processing(lambda x: x + 1, signature)
        >>> assert 1 == len(dp.pre_processing)
        >>> dp.add_pre_processing(print)
        >>> assert 2 == len(dp.pre_processing)
        """
        self.pre_processing.append(
            _Process(binary_signature=binary_signature, function=func)
        )

    def add_post_processing(
        self, func: Callable[[bytes], bytes], binary_signature: bytes = None
    ) -> None:
        """
        Adds a function to the post-processing list.
        The binary_signature of the inversal operation of the pre-processing function should be used if exists.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001 # Please use the SIGNATURES dict
        >>> dp.add_post_processing(lambda x: x * 2, signature)
        >>> assert 1 == len(dp.post_processing)
        >>> dp.add_post_processing(print)
        >>> assert 2 == len(dp.post_processing)
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
        >>> dp.add_pre_processing(lambda x: x + 1, signature_add)
        >>> dp.add_pre_processing(lambda x: x * 2, signature_mult)
        >>> dp.add_post_processing(print)
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
        >>> dp.add_post_processing(lambda x: x / 2, signature_minus)
        >>> dp.add_post_processing(lambda x: x - 1, signature_div)
        >>> dp.add_post_processing(print)
        >>> dp.apply_post_processing(4)
        1.0
        """
        for p in self.post_processing:
            data = p.function(data)
        return data

    def validate_signature(self) -> None:
        """
        Validates the signature of the pre-processing and post-processing functions.
        They must be the same to ensure that the data is processed correctly.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001
        >>> dp.add_pre_processing(lambda x: x + 1, signature)
        >>> assert False == dp.validate_signature()
        >>> dp.add_post_processing(lambda x: x - 1, signature)
        >>> assert dp.validate_signature()
        >>> dp.add_pre_processing(print, None) # This function doesn't interact with the data
        >>> assert dp.validate_signature()
        """
        self.signature = self._compute_signature(self.pre_processing)
        post_processing_signature = self._compute_signature(self.post_processing)

        return self.signature == post_processing_signature

    def verify_signature(self, signature: bytes) -> None:
        """
        Verifies the provided signature is the same as the current signature.

        Examples:
        >>> dp = DataProcessing()
        >>> signature = 0b00000001
        >>> dp.add_pre_processing(lambda x: x + 1, signature)
        >>> dp.add_post_processing(lambda x: x - 1, signature)
        >>> assert dp.validate_signature()
        >>> assert dp.verify_signature(signature)
        >>> assert False == dp.verify_signature(0b10000000)
        """
        return self.signature == signature

    @staticmethod
    def _compute_signature(fcts: List[_Process]) -> bytes:
        signature = 0b0
        for f in fcts:
            if f.binary_signature is not None:
                signature |= f.binary_signature
        return signature
