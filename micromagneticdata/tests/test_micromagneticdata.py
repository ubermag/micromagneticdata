import os
import types
import pandas as pd
import micromagneticdata as md

os.chdir(os.path.dirname(__file__))

name = 'test_sample'
data = md.MicromagneticData(name)


def test_numbers():
    assert data.numbers == list(range(6))


def test_drives():
    assert isinstance(data.drives, types.GeneratorType)
    assert all(isinstance(d, md.Drive) for d in data.drives)


def test_metadata():
    assert isinstance(data.metadata, pd.DataFrame)


def test_subset():
    subset = data.subset([0, 2])
    assert isinstance(subset, md.MicromagneticData)
    assert subset.numbers == [0, 2]


def test_drive():
    assert isinstance(data.drive(1), md.Drive)


def test_iterate():
    iterator = data.iterate('info')
    assert isinstance(iterator, types.GeneratorType)
    assert all(isinstance(i, dict) for i in iterator)
