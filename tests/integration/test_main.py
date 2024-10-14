import pytest

import cshelve


def test_write_and_read():
    db = cshelve.open("tests/configurations/integration-azure.ini")

    key_pattern = "test_write_and_read"
    data_pattern = "test_write_and_read"

    for i in range(100):
        key = f"{key_pattern}{i}"
        db[key] = f"{data_pattern}{i}"
        assert db[key] == f"{data_pattern}{i}"
        del db[key]

    db.close()


def test_read_after_reopening():
    key_pattern = "test_read_after_reopening"
    data_pattern = "test_read_after_reopening"

    def write_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    def read_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            key = f"{key_pattern}{i}"
            assert db[key] == f"{data_pattern}{i}"
            del db[key]

    write_data()
    read_data()


def test_update_on_operator():
    key_pattern = "test_update_on_operator"
    str_data_pattern = "test_update_on_operator"
    list_data_pattern = [1]

    def write_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = str_data_pattern
            db[f"{key_pattern}{i}-list"] = list_data_pattern

    def update_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            key = f"{key_pattern}{i}"
            key_list = f"{key_pattern}{i}-list"
            assert db[key] == str_data_pattern
            assert db[key_list] == list_data_pattern
            db[key] += f"{i}"
            db[key_list] += [i]

    def read_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            key = f"{key_pattern}{i}"
            key_list = f"{key_pattern}{i}-list"
            assert db[key] == f"{str_data_pattern}{i}"
            assert db[key_list] == list_data_pattern + [i]
            del db[key]
            del db[key_list]

    write_data()
    update_data()
    read_data()


def test_key_not_found():
    db = cshelve.open("tests/configurations/integration-azure.ini")

    with pytest.raises(KeyError):
        db["test_key_not_found"]


def test_delete_object():
    db = cshelve.open("tests/configurations/integration-azure.ini")

    key_pattern = "test_delete_object"
    data_pattern = "test_delete_object"

    db[key_pattern] = data_pattern
    del db[key_pattern]

    with pytest.raises(KeyError):
        db[key_pattern]


def test_contains():
    db = cshelve.open("tests/configurations/integration-azure.ini")

    key_pattern = "test_contains"
    data_pattern = "test_contains"

    db[key_pattern] = data_pattern

    assert key_pattern in db

    del db[key_pattern]


def test_len():
    db = cshelve.open("tests/configurations/integration-azure-len.ini")

    key_pattern = "test_len"
    data_pattern = "test_len"

    for i in range(100):
        db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    assert len(db) == 100

    for i in range(100):
        del db[f"{key_pattern}{i}"]

    assert len(db) == 0


def test_iter():
    res = set()
    db = cshelve.open("tests/configurations/integration-azure-iter.ini")

    key_pattern = "test_iter"
    data_pattern = "test_iter"

    for i in range(100):
        key = f"{key_pattern}{i}"
        db[key] = f"{data_pattern}{i}"
        res.add(key)

    keys = set(db)
    assert keys == res

    db.close()


def test_writeback():
    key_pattern = "test_writeback"
    data_pattern = [1]

    def write_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            db[f"{key_pattern}{i}"] = data_pattern

        db.close()

    def update_data(writeback):
        db = cshelve.open(
            "tests/configurations/integration-azure.ini", writeback=writeback
        )

        for i in range(100):
            key = f"{key_pattern}{i}"
            value = db[key]
            value.append(i)

        db.close()

    def read_data(contains_index):
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            key = f"{key_pattern}{i}"
            if contains_index:
                assert db[key] == data_pattern + [i]
            else:
                assert db[key] == data_pattern

        db.close()

    def del_data():
        db = cshelve.open("tests/configurations/integration-azure.ini")

        for i in range(100):
            del db[f"{key_pattern}{i}"]

        db.close()

    write_data()
    update_data(writeback=False)
    read_data(contains_index=False)
    update_data(writeback=True)
    read_data(contains_index=True)
    del_data()
