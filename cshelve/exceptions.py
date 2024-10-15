class UnknownProvider(Exception):
    """
    Raised when an unknown cloud provider is specified in the configuration.
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


class CanNotCreateDB(Exception):
    """
    Raised when an attempt is made to create a DB and it fails.
    """

    pass
