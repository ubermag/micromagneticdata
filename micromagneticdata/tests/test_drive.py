import os
import types
import pandas as pd
import discretisedfield as df
import micromagneticdata as md

os.chdir(os.path.dirname(__file__))

name = 'test_sample'
number = 0
drive = md.Drive(name, number)


def test_m0():
    assert isinstance(drive.m0, df.Field)


def test_mif():
    assert isinstance(drive.mif, str)


def test_info():
    assert isinstance(drive.info, dict)


def test_dt():
    assert isinstance(drive.dt, pd.DataFrame)


def test_step_number():
    assert isinstance(drive.step_number, int)


def test_step_filenames():
    assert isinstance(drive.step_filenames, types.GeneratorType)
    assert all(isinstance(fn, str) for fn in drive.step_filenames)


def test_step_fields():
    assert isinstance(drive.step_fields, types.GeneratorType)
    assert all(isinstance(f, df.Field) for f in drive.step_fields)
