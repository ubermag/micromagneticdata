import os
import glob
import types
import pytest
import pandas as pd
import micromagneticmodel as mm
import micromagneticdata as md

os.chdir(os.path.dirname(__file__))

name = 'test_sample'
data = md.MicromagneticData(name)

def test_numbers():
    assert data.numbers == [0, 1, 2, 3, 4, 5]

def test_drives():
    assert isinstance(data.drives, types.GeneratorType)
    assert all(isinstance(d, md.Drive) for d in data.drives)

def test_metadata():
    assert isinstance(data.metadata, pd.DataFrame)

def test_subset():
    ss = data.subset([0, 2])
    assert isinstance(ss, md.MicromagneticData)
    assert ss.numbers == [0, 2]

def test_drive():
    assert isinstance(data.drive(0), md.Drive)

def test_iter():
    iterator = data.iter('info')
    assert isinstance(iterator, types.GeneratorType)
    assert all(isinstance(i, dict) for i in iterator)
