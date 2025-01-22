from cshelve import DataProcessing


def test_add_pre_processing():
    binary_signature = 0b00000001
    dp = DataProcessing()
    dp.add_pre_processing(binary_signature, lambda x: x + 1)
    assert len(dp.pre_processing) == 1
    assert dp.pre_processing[0].binary_signature == binary_signature
    assert dp.pre_processing[0].function(1) == 2


def test_add_post_processing():
    binary_signature = 0b00000010
    dp = DataProcessing()
    dp.add_post_processing(binary_signature, lambda x: x * 2)
    assert len(dp.post_processing) == 1
    assert dp.post_processing[0].binary_signature == binary_signature
    assert dp.post_processing[0].function(2) == 4


def test_apply_pre_processing():
    dp = DataProcessing()
    dp.add_pre_processing("add_1", lambda x: x + 1)
    dp.add_pre_processing("mult_by_2", lambda x: x * 2)
    result = dp.apply_pre_processing(1)
    assert result == 4  # (1 + 1) * 2


def test_apply_post_processing():
    dp = DataProcessing()
    dp.add_post_processing("div_by_2", lambda x: x / 2)
    dp.add_post_processing("minus_1", lambda x: x - 1)
    result = dp.apply_post_processing(4)
    assert result == 1  # (4 / 2) - 1


def test_full_processing():
    dp = DataProcessing()
    dp.add_pre_processing("add_1", lambda x: x + 1)
    dp.add_pre_processing("mult_by_2", lambda x: x * 2)
    dp.add_post_processing("div_by_2", lambda x: x / 2)
    dp.add_post_processing("minus_1", lambda x: x - 1)

    data = 1
    pre_processed_data = dp.apply_pre_processing(data)
    final_data = dp.apply_post_processing(pre_processed_data)

    assert pre_processed_data == 4  # (1 + 1) * 2
    assert final_data == 1  # (4 / 2) - 1
