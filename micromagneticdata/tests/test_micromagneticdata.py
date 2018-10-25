import os
import glob
import shutil
import pytest
import pandas as pd
import micromagneticmodel as mm
import micromagneticdata as md

os.chdir(os.path.dirname(__file__))

@pytest.mark.oommf
def test_micromagneticdata():
    name = 'micromagneticdata'

    system = mm.System(name=name)

    assert md.MicromagneticData(system).name == name
    assert md.MicromagneticData('micromagneticdata').name == name

@pytest.mark.oommf
def test_drives_information():
    name = 'test_sample'

    data = md.MicromagneticData(name)
    df = data.drives

    assert isinstance(df, pd.DataFrame) == True
    assert len(df.index) == 6
    assert 'date' in df.columns

@pytest.mark.oommf
def test_drives_number():
    name = 'test_sample'

    data = md.MicromagneticData(name)

    assert len(data.drives_number) == 6
