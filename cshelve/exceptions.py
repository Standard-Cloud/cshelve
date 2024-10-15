from typing import Type


class UnknownProviderError(RuntimeError):
    """
    Raised when an unknown cloud provider is specified in the configuration.
    """

    pass


class KeyNotFoundError(KeyError):
    """
    Raised when a resource is not found.
    """

    pass


class ReadOnlyError(Exception):
    """
    Raised when an attempt is made to write to a read-only DB.
    """

    pass


class DBDoesNotExistsError(Exception):
    """
    Raised when an the DB does not exist and the flag does not allow creating it.
    """

    pass


class CanNotCreateDBError(Exception):
    """
    Raised when an attempt is made to create a DB and it fails.
    """

    pass


def key_access(exception: Type[Exception]) -> KeyNotFoundError:
    """
    Create a KeyNotFoundError exception if the key is not found.
    """

    def wrapper(func):
        def inner(self, key, *args, **kwargs):
            try:
                return func(self, key, *args, **kwargs)
            except exception as e:
                raise KeyNotFoundError(f"Key not found: {key}") from e

        return inner

    return wrapper
