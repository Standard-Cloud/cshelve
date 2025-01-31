import pickle
from unittest.mock import Mock

import pytest
from cshelve import DataProcessing, DataProcessingSignatureError


def add_one(x):
    return pickle.dumps(pickle.loads(x) + 1)


def minus_one(x):
    return pickle.dumps(pickle.loads(x) - 1)


def add_one_dict(x):
    return pickle.dumps({k: v + 1 for k, v in pickle.loads(x).items()})


def minus_one_dict(x):
    return pickle.dumps({k: v - 1 for k, v in pickle.loads(x).items()})


def test_processing():
    """
    Test the processing of data.
    """
    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    run_int_processing(dp)

    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(minus_one, add_one, b"b")
    run_int_processing(dp)

    dp = DataProcessing(Mock())
    dp.add(add_one_dict, minus_one_dict, b"a")
    run_dict_processing(dp)

    dp = DataProcessing(Mock())
    dp.add(add_one_dict, minus_one_dict, b"a")
    dp.add(minus_one_dict, add_one_dict, b"b")
    run_dict_processing(dp)


def test_wrong_processing():
    """
    Test that the signature must be in the correct order.
    """
    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(add_one, minus_one, b"b")
    dp.add(add_one, minus_one, b"c")

    data = pickle.dumps(1)

    data_pre_processed = dp.apply_pre_processing(data)

    # Change the signature to an incorrect one.
    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(add_one, minus_one, b"c")
    dp.add(add_one, minus_one, b"b")

    with pytest.raises(DataProcessingSignatureError):
        dp.apply_post_processing(data_pre_processed)


def test_signature_compatible():
    """
    Signature are compatibles when the signature that must be applied is a subset of the current signature in the correct order.
    """
    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")

    data = pickle.dumps(1)

    data_pre_processed = dp.apply_pre_processing(data)

    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(add_one, minus_one, b"b")
    dp.apply_post_processing(data_pre_processed)

    # With a longer signature.
    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(add_one, minus_one, b"b")

    data = pickle.dumps(1)

    data_pre_processed = dp.apply_pre_processing(data)

    dp = DataProcessing(Mock())
    dp.add(add_one, minus_one, b"a")
    dp.add(add_one, minus_one, b"b")
    dp.add(add_one, minus_one, b"c")
    dp.apply_post_processing(data_pre_processed)


def run_int_processing(dp):
    for i in (-100_000, -100, 1, 100, 100_000):
        data = pickle.dumps(i)

        data_pre_processed = dp.apply_pre_processing(data)
        data_post_processed = dp.apply_post_processing(data_pre_processed)

        assert i == pickle.loads(data_post_processed)


def run_dict_processing(dp):
    for i in (
        {"a": 1, "b": 2},
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 2, "c": 3, "d": 4},
    ):
        data = pickle.dumps(i)

        data_pre_processed = dp.apply_pre_processing(data)
        data_post_processed = dp.apply_post_processing(data_pre_processed)

        assert i == pickle.loads(data_post_processed)
