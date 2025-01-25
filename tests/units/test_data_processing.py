from cshelve import DataProcessing


def test_processing():
    dp = DataProcessing()
    dp.add_pre_processing(lambda x: x + 1, 0b00000001)
    dp.add_pre_processing(lambda x: x * 2, 0b00000010)
    dp.add_post_processing(lambda x: x / 2, 0b00000010)
    dp.add_post_processing(lambda x: x - 1, 0b00000001)

    assert dp.validate_signature()

    data = 1
    pre_processed_data = dp.apply_pre_processing(data)
    final_data = dp.apply_post_processing(pre_processed_data)

    assert pre_processed_data == 4  # (1 + 1) * 2
    assert final_data == 1  # (4 / 2) - 1


def test_signature_validation():
    dp = DataProcessing()

    dp.add_pre_processing(lambda x: x + 1, 0b00000001)
    assert False == dp.validate_signature()
    dp.add_post_processing(lambda x: x / 2, 0b00000001)
    assert dp.validate_signature()

    dp = DataProcessing()
    dp.add_pre_processing(lambda x: x + 1, 0b00000001)
    assert False == dp.validate_signature()
    dp.add_post_processing(lambda x: x - 1, 0b00000010)
    assert False == dp.validate_signature()


def test_verify_signature():
    signature = 0b00000001
    dp = DataProcessing()

    dp.add_pre_processing(lambda x: x + 1, signature)
    dp.add_post_processing(lambda x: x - 1, signature)

    assert dp.validate_signature()
    assert dp.verify_signature(signature)
    assert False == dp.verify_signature(signature << 1)
