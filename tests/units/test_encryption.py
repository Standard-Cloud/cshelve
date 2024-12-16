# """
# Test the encryption module.
# """
# from unittest.mock import Mock

# import pytest

# from cshelve import UnknownEncryptionAlgorithmError
# from cshelve._encryption import configure
# from cshelve._data_processing import DataProcessing


# @pytest.fixture
# def data_processing():
#     return DataProcessing()


# def test_no_encryption(data_processing):
#     """
#     Ensure nothing si configure when the config is empty.
#     """
#     logger = Mock()
#     config = {}

#     configure(logger, data_processing, config)

#     assert len(data_processing.post_processing) == 0
#     assert len(data_processing.pre_processing) == 0


# def test_default_aes256_config(data_processing):
#     """
#     Ensure AES256 is configured when defined.
#     """
#     logger = Mock()
#     config = {"algorithm": "aes256"}

#     configure(logger, data_processing, config)

#     assert len(data_processing.post_processing) == 1
#     assert len(data_processing.pre_processing) == 1
#     assert data_processing.pre_processing[0].func == None
#     assert data_processing.post_processing[0].func == None

#     first_pre_processing_applied = id(data_processing.pre_processing[0])
#     first_post_processing_applied = id(data_processing.post_processing[0])

#     # Ensure the same behaviours and order if configured twice.
#     configure(logger, data_processing, config)

#     assert len(data_processing.post_processing) == 2
#     assert len(data_processing.pre_processing) == 2
#     # Ensure the order is respected.
#     assert first_pre_processing_applied == id(data_processing.pre_processing[0])
#     assert first_post_processing_applied == id(data_processing.post_processing[0])


# def test_unknowned_algorithm(data_processing):
#     """
#     Ensure an exception is raised when an unknowed algorithm is provided.
#     """
#     logger = Mock()
#     config = {"algorithm": "unknow"}

#     with pytest.raises(UnknownEncryptionAlgorithmError):
#         configure(logger, data_processing, config)
