"""
The factory ensures that the correct backend is loaded based on the provider.
"""
from unittest.mock import patch, Mock

import pytest

from cshelve import UnknownProviderError
from cshelve._factory import factory


@patch("cshelve._azure_blob_storage.AzureBlobStorage")
def test_known_backend(azure_mock):
    """
    Test factory loading the Azure backend.
    """
    factory(Mock(), "azure-blob")

    azure_mock.assert_called_once()


def test_unknown_backend():
    """
    Ensure that the factory raises an error when an unknown backend is requested.
    """
    with pytest.raises(UnknownProviderError):
        factory(Mock(), "aws")
