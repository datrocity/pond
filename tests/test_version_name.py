from datetime import datetime

from unittest.mock import patch
import pytest

from pond.exceptions import IncompatibleVersionName
from pond.version_name import (
    DateTimeVersionName,
    SimpleVersionName,
    VersionName,
)


def test_simple_version_name_from_string():
    name = VersionName.from_string('v1')
    assert isinstance(name, SimpleVersionName)
    assert str(name) == 'v1'


def test_simple_version_name_first():
    name = SimpleVersionName.next(prev=None)
    assert name == SimpleVersionName(1)


def test_simple_version_name_next():
    prev = SimpleVersionName(37)
    assert SimpleVersionName.next(prev) == SimpleVersionName(38)


def test_simple_version_name_next_not_compatible():
    prev = DateTimeVersionName.from_string('2020-01-22 01:02:03')
    with pytest.raises(IncompatibleVersionName):
        SimpleVersionName.next(prev)


def test_date_time_version_name_from_string():
    name = VersionName.from_string('2020-01-22 01:02:03')
    assert isinstance(name, DateTimeVersionName)
    assert str(name) == '2020-01-22 01:02:03'


def test_date_time_version_name_first():
    target_datetime = datetime(2022, 6, 12, 1, 32, 12)
    with patch('datetime.datetime', return_value=target_datetime):
        name = DateTimeVersionName.next(prev=None)
        assert name == DateTimeVersionName(target_datetime)


def test_date_time_version_name_next_collision():
    prev = DateTimeVersionName(datetime(2022, 6, 12, 1, 32, 11))
    next_ = DateTimeVersionName.next(prev)
    expected = DateTimeVersionName(datetime(2022, 6, 12, 1, 32, 12))
    assert next_ == expected


def test_date_time_version_name_next_no_collision():
    target_datetime = datetime(2022, 6, 12, 1, 32, 12)
    with patch('datetime.datetime', return_value=target_datetime):
        prev = DateTimeVersionName(datetime(2022, 1, 1, 1, 0, 0))
        next_ = DateTimeVersionName.next(prev)
    expected = DateTimeVersionName(target_datetime)
    assert next_ == expected


def test_date_time_version_name_next_not_compatible():
    prev = SimpleVersionName(version_number=3)
    with pytest.raises(IncompatibleVersionName):
        DateTimeVersionName.next(prev)


def test_ordering():
    versions = [
        "2018-12-04 03:28:12",
        "v1",
        "2018-01-01 10:00:12",
        "v10",
        "v2",
        "2018-01-01",
    ]
    names = sorted([VersionName.from_string(version) for version in versions])

    expected = [
        "2018-01-01 00:00:00",
        '2018-01-01 10:00:12',
        '2018-12-04 03:28:12',
        'v1',
        'v2',
        'v10',
    ]
    assert [str(name) for name in names] == expected
