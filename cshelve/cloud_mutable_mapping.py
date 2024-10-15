from abc import abstractmethod
from collections.abc import MutableMapping
from typing import Dict


class CloudMutableMapping(MutableMapping):
    flag = None

    @abstractmethod
    def configure(self, config: Dict[str, str]) -> None:
        """
        Configure the cloud storage backend.
        """
        raise NotImplementedError
