import pytest

import cshelve

from helpers import write_data, del_data


def test_read_only():
    config_file = "tests/configurations/integration-azure-flag.ini"
    key_pattern = "test_read_only"
    data_pattern = "test_read_only"

    def cant_update():
        db = cshelve.open(config_file, "r")

        for i in range(100):
            key = f"{key_pattern}{i}"

            assert db[key] == f"{data_pattern}{i}"

            with pytest.raises(cshelve.ReadOnlyError):
                db[key] = data_pattern

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    cant_update()
    del_data(config_file, key_pattern)


def test_clear_db():
    config_file = "tests/configurations/integration-azure-flag-n.ini"
    key_pattern = "test_clear_db"
    data_pattern = "test_clear_db"

    def rewrite_db():
        db = cshelve.open(config_file, "n")

        assert len(db) == 0

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

        db.close()

    def read_data():
        db = cshelve.open(config_file, "r")

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"

        db.close()

    write_data(config_file, key_pattern, data_pattern)
    rewrite_db()
    read_data()
    del_data(config_file, key_pattern)


def test_container_does_not_exists():
    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/integration-azure-container-does-not-exists.ini", "w"
        )

    with pytest.raises(cshelve.DBDoesNotExistsError):
        cshelve.open(
            "tests/configurations/integration-azure-container-does-not-exists.ini", "r"
        )
