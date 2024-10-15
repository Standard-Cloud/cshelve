import pytest

import cshelve


def test_read_only():
    key_pattern = "test_read_only"
    str_data_pattern = "test_read_only"

    def write_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-read.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{str_data_pattern}{i}"

        db.close()

    def read_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-read.ini", "r")

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{str_data_pattern}{i}"

        db.close()

    def raise_on_update_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-read.ini", "r")

        for i in range(100):
            key = f"{key_pattern}{i}"

            with pytest.raises(cshelve.ReadonlyShelfError):
                db[key] = str_data_pattern

        db.close()

    def del_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-read.ini")

        for i in range(100):
            del db[f"{key_pattern}{i}"]

        db.close()

    write_data()
    read_data()
    raise_on_update_data()
    del_data()
