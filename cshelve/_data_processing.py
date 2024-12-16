"""
This module provides the DataProcessing class, which handles pre-processing and post-processing of data.

Examples:
    >>> dp = DataProcessing()
    >>> dp.add_pre_processing(lambda x: x + b'1')
    >>> dp.add_post_processing(lambda x: x + b'2')
    >>> pre_processed = dp.apply_pre_processing(b'0')
    >>> pre_processed
    b'01'
    >>> post_processed = dp.apply_post_processing(pre_processed)
    >>> post_processed
    b'012'
"""
from typing import Callable, Optional, List


class DataProcessing:
    """
    A class to handle pre-processing and post-processing of data.
    """

    def __init__(
        self,
        pre_processing: Optional[List[Callable[[bytes], bytes]]] = None,
        post_processing: Optional[List[Callable[[bytes], bytes]]] = None,
    ):
        """
        Initializes the DataProcessing class with optional pre-processing and post-processing lists.

        Examples:
        >>> dp = DataProcessing()
        >>> dp.pre_processing
        []
        >>> dp.post_processing
        []
        """
        self.pre_processing = pre_processing if pre_processing is not None else []
        self.post_processing = post_processing if post_processing is not None else []

    def add_pre_processing(self, func: Callable[[bytes], bytes]) -> None:
        """
        Adds a function to the pre-processing list.

        Examples:
        >>> dp = DataProcessing()
        >>> dp.add_pre_processing(lambda x: x + 1)
        >>> len(dp.pre_processing)
        1
        """
        self.pre_processing.append(func)

    def add_post_processing(self, func: Callable[[bytes], bytes]) -> None:
        """
        Adds a function to the post-processing list.

        Args:
        func (function): A function to add to the post-processing list.

        Examples:
        >>> dp = DataProcessing()
        >>> dp.add_post_processing(lambda x: x * 2)
        >>> len(dp.post_processing)
        1
        """
        self.post_processing.append(func)

    def apply_pre_processing(self, data: bytes) -> bytes:
        """
        Applies all pre-processing functions to the data.

        Args:
        data: The data to process.

        Returns:
        The processed data.

        Examples:
        >>> dp = DataProcessing(pre_processing=[lambda x: x + 1, lambda x: x * 2])
        >>> dp.apply_pre_processing(1)
        4
        """
        for func in self.pre_processing:
            data = func(data)
        return data

    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Applies all post-processing functions to the data.

        Args:
        data: The data to process.

        Returns:
        The processed data.

        Examples:
        >>> dp = DataProcessing(post_processing=[lambda x: x / 2, lambda x: x - 1])
        >>> dp.apply_post_processing(4)
        1.0
        """
        for func in self.post_processing:
            data = func(data)
        return data
