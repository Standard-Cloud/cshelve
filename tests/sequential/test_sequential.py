"""
Following tests verify behavior at a global level on the database and must tested in a sequential way.
"""
import cshelve
from tests.integration.helpers import del_data, write_data


def test_clear_db():
    """
    Ensure the database is cleared when using the 'n' flag.
    """
    config_file = "tests/configurations/azure-integration/flag-n.ini"
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


def test_del():
    """
    Ensure we can delete a record from the DB.
    """
    config_file = "tests/configurations/azure-integration/del.ini"
    key_pattern = "test_del"
    data_pattern = "test_del"

    def _del_data():
        db = cshelve.open(config_file)

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

        assert len(db) == 0
        db.close()

    write_data(config_file, key_pattern, data_pattern)
    _del_data()


def test_len():
    """
    Ensure __len__ works as expected.
    """
    config = "tests/configurations/azure-integration/len.ini"
    db = cshelve.open(config)

    key_pattern = "test_len"
    data_pattern = "test_len"

    del_data(config)

    for i in range(100):
        db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    assert len(db) == 100

    for i in range(100):
        del db[f"{key_pattern}{i}"]

    assert len(db) == 0


def test_iter():
    """
    Ensure the __iter__ method works as expected.
    """
    config = "tests/configurations/azure-integration/iter.ini"
    res = set()
    db = cshelve.open(config)

    key_pattern = "test_iter"
    data_pattern = "test_iter"
    del_data(config)

    for i in range(100):
        key = f"{key_pattern}{i}"
        db[key] = f"{data_pattern}{i}"
        res.add(key)

    keys = set(db)
    assert keys == res

    db.close()
    del_data(config)
