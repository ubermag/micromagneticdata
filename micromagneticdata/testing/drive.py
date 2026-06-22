"""Tests for plugins.

Adapter packages should import these tests and implement the following fixtures:

-

Data for the fixtures can either be generated dynamically or pre-computed and committed
to the repository. Consider pre-computing in particular for long-running simulations
or when setting up the environment/the calculator is difficult (or restricted to
specific hardware). For pre-computed data also commit the script to (re-)generate the
data.
"""

import discretisedfield as df
import pytest
import ubermagtable as ut


def test_n(drive):
    assert isinstance(drive.n, int)


def test_x(drive_with_reference):
    drive, (drive_x, _, _) = drive_with_reference
    assert isinstance(drive.x, str)
    assert drive.x == drive_x

    with pytest.raises(ValueError):
        drive.x = "not_a_valid_column_name"


def test_set_x(drive_with_reference):
    drive, (drive_x, new_drive_x, _) = drive_with_reference
    assert drive.x == drive_x
    drive.x = new_drive_x

    assert drive.x == new_drive_x


def test_calculator_script(drive_with_reference):
    drive, (_, _, calculator_script_content) = drive_with_reference
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
