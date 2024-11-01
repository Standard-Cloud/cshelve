from collections.abc import MutableMapping
from concurrent.futures import ThreadPoolExecutor

from .cloud_database import CloudDatabase
from ._flag import can_create, can_write, clear_db
from .exceptions import (
    CanNotCreateDBError,
    DBDoesNotExistsError,
    DBDoesNotExistsError,
)


__all__ = ["_Database", "init"]


class _Database(MutableMapping):
    """
    Wrapper around the cloud database to provide a MutableMapping interface.
    """

    def __init__(self, db: CloudDatabase, flag: str) -> None:
        super().__init__()
        self.db = db
        self.flag = flag

    def __getitem__(self, key: bytes) -> bytes:
        return self.db.get(key)

    @can_write
    def __setitem__(self, key: bytes, value: bytes) -> None:
        self.db.set(key, value)

    @can_write
    def __delitem__(self, key: bytes) -> None:
        self.db.delete(key)

    def __iter__(self):
        return iter(self.db.iter())

    def __len__(self) -> int:
        return self.db.len()

    def close(self) -> None:
        """
        Close the cloud database.
        """
        self.db.close()

    def sync(self) -> None:
        """
        Sync the cloud database.
        """
        self.db.sync()


def init(db: CloudDatabase, flag: str) -> _Database:
    """
    Open a cloud database based on the configuration file.
    """
    # Create container if not exists and it is configured or if the flag allow it.
    if not db.exists():
        if can_create(flag):
            try:
                db.create()
            except Exception as e:
                raise CanNotCreateDBError(f"Can't create database.") from e
        else:
            raise DBDoesNotExistsError(f"Can't create database.")

    # If the flag parameter indicates, clear the database.
    if clear_db(flag):
        # Retrieve all the keys and delete them.
        # Retrieving keys is quick, but the deletion synchronously is slow so we use threads to speed up the process.
        with ThreadPoolExecutor() as executor:
            for _ in executor.map(db.delete, db.iter()):
                pass

    return _Database(db, flag)
