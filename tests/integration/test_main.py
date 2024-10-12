import pytest

from cshelve import open


def test_write_and_read():
    db = open('tests/configurations/integration-azure.ini')

    key_pattern = 'test_write_and_read'
    data_pattern = 'test_write_and_read'

    for i in range(100):
        key = f'{key_pattern}{i}'
        db[key] = f'{data_pattern}{i}'
        assert db[key] == f'{data_pattern}{i}'
        del db[key]

    db.close()


def test_read_after_reopening():
    key_pattern = 'test_read_after_reopening'
    data_pattern = 'test_read_after_reopening'

    def write_data():
        db = open('tests/configurations/integration-azure.ini')

        for i in range(100):
            db[f'{key_pattern}{i}'] = f'{data_pattern}{i}'

    def read_data():
        db = open('tests/configurations/integration-azure.ini')

        for i in range(100):
            key = f'{key_pattern}{i}'
            assert db[key] == f'{data_pattern}{i}'
            del db[key]

    write_data()
    read_data()


def test_key_not_found():
    db = open('tests/configurations/integration-azure.ini')

    with pytest.raises(KeyError):
        db['test_key_not_found']


def test_delete_object():
    db = open('tests/configurations/integration-azure.ini')

    key_pattern = 'test_delete_object'
    data_pattern = 'test_delete_object'

    db[key_pattern] = data_pattern
    del db[key_pattern]

    with pytest.raises(KeyError):
        db[key_pattern]


def test_contains():
    db = open('tests/configurations/integration-azure.ini')

    key_pattern = 'test_contains'
    data_pattern = 'test_contains'

    db[key_pattern] = data_pattern

    assert key_pattern in db

    del db[key_pattern]


def test_len():
    db = open('tests/configurations/integration-azure-len.ini')

    key_pattern = 'test_len'
    data_pattern = 'test_len'

    for i in range(100):
        db[f'{key_pattern}{i}'] = f'{data_pattern}{i}'

    assert len(db) == 100

    for i in range(100):
        del db[f'{key_pattern}{i}']

    assert len(db) == 0


def test_iter():
    res = set()
    db = open('tests/configurations/integration-azure-iter.ini')

    key_pattern = 'test_iter'
    data_pattern = 'test_iter'

    for i in range(100):
        key = f'{key_pattern}{i}'
        db[key] = f'{data_pattern}{i}'
        res.add(key)

    keys = set(db)
    assert keys == res

    db.close()
