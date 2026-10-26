"""Tests for plugins.

Adapter packages should import these tests and implement the following fixtures:

- ``drive``: returns a single Drive subclass instance
- ``drive_with_reference``: returns a single Drive subclass instance and reference data:
  - name of the independent variable x
  - a suitable other column name to change the independent variable x to
  - a suitable substring of the calculator script to verify that it is loaded correctly

Data for the fixtures can either be generated dynamically or pre-computed and committed
to the repository. Consider pre-computing in particular for long-running simulations
or when setting up the environment/the calculator is difficult (or restricted to
specific hardware). For pre-computed data also commit the script to (re-)generate the
data.

The concrete magnetisation-state type is calculator-specific. Adapter packages should
add a focused assertion for their expected type and data contract.
"""

import pytest
import ubermagtable as ut

import micromagneticdata as mdata


def test_drive_fixture(drive):
    assert isinstance(drive, mdata.Drive)


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
    assert isinstance(drive.m0, type(drive[0]))


def test_getitem(drive):
    state_type = type(drive[0])
    for i in range(drive.n):
        assert isinstance(drive[i], state_type)


def test_iter(drive):
    state_type = type(drive[0])
    for state in drive:
        assert isinstance(state, state_type)
