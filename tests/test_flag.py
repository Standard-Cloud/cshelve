from unittest.mock import Mock

import pytest

import cshelve
from cshelve._flag import can_create, can_write, clear_db


def test_read_only():
    mock = Mock()
    mock.flag = "r"

    with pytest.raises(cshelve.ReadonlyError):
        can_write(lambda x: x)(mock)


def test_can_write():
    mock = Mock()

    for flag in ("w", "c", "n"):
        mock.flag = flag
        assert can_write(lambda x: True)(mock) == True


def test_can_create():
    mock = Mock()

    for flag in ("c", "n"):
        mock.flag = flag
        assert can_create(lambda x: True)(mock) == True


def test_can_not_create():
    mock = Mock()

    for flag in ("w", "r"):
        mock.flag = flag
        with pytest.raises(cshelve.DBDoesnotExistsError):
            can_create(lambda x: x)(mock)


def test_do_not_clear_db():
    assert clear_db("n") == True


def test_do_not_clear_db():
    for flag in ("w", "r", "c"):
        assert clear_db(flag) == False
