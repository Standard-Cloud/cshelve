class UnknownProvider(Exception):
    """
    Raised when an unknown cloud provider is specified in the configuration.
    """

    pass


class ReadonlyError(Exception):
    """
    Raised when an attempt is made to write to a read-only shelf.
    """

    pass


class DBDoesnotExistsError(Exception):
    """
    Raised when an attempt is made to write to a read-only shelf.
    """

    pass
