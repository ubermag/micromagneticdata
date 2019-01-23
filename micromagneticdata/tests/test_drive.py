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
    assert 'MIF 2.1' in drive.mif

def test_info():
    assert isinstance(drive.info, dict)
    assert drive.info.get('date')

def test_dt():
    assert isinstance(drive.dt, pd.DataFrame)
    assert 't' in drive.dt.columns

def test_step_number():
    assert isinstance(drive.step_number, int)

def test_step_filenames():
    assert isinstance(drive.step_filenames, types.GeneratorType)
    assert all(isinstance(x, str) for x in drive.step_filenames)

def test_step_fields():
    assert isinstance(drive.step_fields, types.GeneratorType)
    assert all(isinstance(x, df.Field) for x in drive.step_fields)

