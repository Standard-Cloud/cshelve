"""
The `CloudMutableMapping` class is an abstract class that defines the interface for cloud storage backends supporting the `MutableMapping` interface.
This class is used by the `Shelf` class to interact with the cloud storage backend.
"""
from abc import abstractmethod
from collections.abc import MutableMapping
from typing import Dict


class CloudMutableMapping(MutableMapping):
    """
    This class defines the interface for cloud storage backends that support the MutableMapping interface.
    Except for the custom configure method, all methods are inherited from the MutableMapping class.
    """

    # The flag parameter verifies permissions but is not directly utilized by the subclasses.
    flag = None

    @abstractmethod
    def configure(self, config: Dict[str, str]) -> None:
        """
        Configure the cloud storage backend.
        """
        raise NotImplementedError
