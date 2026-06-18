"""Tests for plugins"""

import discretisedfield as df
import pytest
import ubermagtable as ut


def test_n(drive):
    assert isinstance(drive.n, int)


def test_x(drive, drive_x):
    assert isinstance(drive.x, str)
    assert drive.x == drive_x

    with pytest.raises(ValueError):
        drive.x = "not_a_valid_column_name"


def test_set_x(drive, drive_x, new_drive_x):
    assert drive.x == drive_x
    drive.x = new_drive_x

    assert drive.x == new_drive_x


def test_calculator_script(drive, calculator_script_content):
    assert isinstance(drive.calculator_script, str)
    assert calculator_script_content in drive.calculator_script


def test_table(drive):
    assert isinstance(drive.table, ut.Table)
    assert drive.table.x == drive.x


def test_m0(drive):
    assert isinstance(drive.m0, df.Field)


def test_getitem(drive):
    for i in range(drive.n):
        assert isinstance(drive[i], df.Field)


def test_iter(drive):
    for m in drive:
        assert isinstance(m, df.Field)
