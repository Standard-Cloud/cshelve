from cshelve import DataProcessing


def test_add_pre_processing():
    dp = DataProcessing()
    dp.add_pre_processing(lambda x: x + 1)
    assert len(dp.pre_processing) == 1
    assert dp.pre_processing[0](1) == 2


def test_add_post_processing():
    dp = DataProcessing()
    dp.add_post_processing(lambda x: x * 2)
    assert len(dp.post_processing) == 1
    assert dp.post_processing[0](2) == 4


def test_apply_pre_processing():
    dp = DataProcessing(pre_processing=[lambda x: x + 1, lambda x: x * 2])
    result = dp.apply_pre_processing(1)
    assert result == 4  # (1 + 1) * 2


def test_apply_post_processing():
    dp = DataProcessing(post_processing=[lambda x: x / 2, lambda x: x - 1])
    result = dp.apply_post_processing(4)
    assert result == 1  # (4 / 2) - 1


def test_full_processing():
    dp = DataProcessing(
        pre_processing=[lambda x: x + 1, lambda x: x * 2],
        post_processing=[lambda x: x / 2, lambda x: x - 1],
    )

    data = 1
    pre_processed_data = dp.apply_pre_processing(data)
    final_data = dp.apply_post_processing(pre_processed_data)

    assert pre_processed_data == 4  # (1 + 1) * 2
    assert final_data == 1  # (4 / 2) - 1
