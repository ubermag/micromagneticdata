import os
import glob
import shutil
import pytest
import micromagneticmodel as mm
import micromagneticdata as md

@pytest.mark.oommf
def test_micromagneticdata():
    name = "micromagneticdata"

    system = mm.System(name=name)

    assert md.MicromagneticData(system).name == name
    assert md.MicromagneticData('micromagneticdata').name == name
