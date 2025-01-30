"""
Ensure migration are possible and invisible for users.
"""
import pickle
from unittest.mock import Mock
from cshelve._data_processing import DataProcessing
from cshelve._database import _Database


def test_migration_to_v1():
    """
    Ensure the smooth migration from no version to version 1.
    """
    key = "key"
    value = "Raw pickle simulating no version."

    db = {key: pickle.dumps(value)}

    logger = Mock()
    data_processing = DataProcessing(logger)
    database = _Database(logger, db, "c", data_processing)

    assert pickle.loads(database[key]) == value
