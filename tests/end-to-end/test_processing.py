"""
"""
import pytest
import cshelve


CONFIG_FILES = [
    "tests/configurations/azure-blob/standard.ini",
]


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_data_processing(config_file: str):
    """ """
    processing = cshelve.DataProcessing(
        pre_processing=[lambda a: a + 1, lambda a: a * 2],
        post_processing=[lambda a: a / 2, lambda a: a - 1],
    )

    # Only odd numbers due to the division by 2.
    data = {"Bonemine": 1, "Astérix": 3, "Amérix": 5}
    data_processed = {"Bonemine": 4, "Astérix": 8, "Amérix": 12}

    db = cshelve.open(config_file, data_processing=processing)

    # Insert data.
    for k, v in data.items():
        db[k] = v

    # Ensure the data was processed before insertion.
    assert db.db == data_processed

    # Ensure the data was processed correctly during retrieval.
    for k, v in data.items():
        assert db[k] == v

    db.close()
