from unittest.mock import patch

import pytest

from cshelve import UnknownProviderError
from cshelve._factory import factory


@patch("cshelve._azure.AzureMutableMapping")
def test_known_backend(azure_mock):
    """
    Test factory loading the Azure backend.
    """
    azure = factory("azure")

    azure_mock.assert_called_once()


def test_unknown_backend():
    """
    Ensure that the factory raises an error when an unknown backend is requested.
    """
    with pytest.raises(UnknownProviderError):
        factory("aws")
