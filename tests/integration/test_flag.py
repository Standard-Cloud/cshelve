import pytest

import cshelve


def test_read_only():
    key_pattern = "test_read_only"
    str_data_pattern = "test_read_only"

    def write_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-r.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{str_data_pattern}{i}"

        db.close()

    def read_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-r.ini", "r")

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{str_data_pattern}{i}"

        db.close()

    def raise_on_update_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-r.ini", "r")

        for i in range(100):
            key = f"{key_pattern}{i}"

            with pytest.raises(cshelve.ReadonlyError):
                db[key] = str_data_pattern

        db.close()

    def del_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-r.ini")

        for i in range(100):
            del db[f"{key_pattern}{i}"]

        db.close()

    write_data()
    read_data()
    raise_on_update_data()
    del_data()


def test_clear_db():
    key_pattern = "test_clear_db"
    str_data_pattern = "test_clear_db"

    def write_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-n.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{str_data_pattern}{i}"

        db.close()

    def rewrite_db():
        db = cshelve.open("tests/configurations/flag/integration-azure-n.ini", "n")

        assert len(db) == 0

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{str_data_pattern}{i}"

        db.close()

    def read_data():
        db = cshelve.open("tests/configurations/flag/integration-azure-n.ini", "r")

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{str_data_pattern}{i}"

        db.close()

    def del_data():
        cshelve.open("tests/configurations/flag/integration-azure-n.ini", "n").close()

    write_data()
    rewrite_db()
    read_data()
    del_data()


def test_container_does_not_exists():
    key_pattern = "test_container_does_not_exists"
    str_data_pattern = "test_container_does_not_exists"

    with pytest.raises(cshelve.DBDoesnotExistsError):
        cshelve.open("tests/configurations/flag/integration-azure-w.ini", "w")
