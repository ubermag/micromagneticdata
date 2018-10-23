import os
import glob
import shutil
import pytest
import oommfc as oc
import micromagneticmodel as mm
import pytest
import micromagneticdata as md

@pytest.mark.oommf
def test_micromagneticdata():
    name = "micromagneticdata"

    system = oc.System(name=name)

    assert md.MicromagneticData(system).name == name
    assert md.MicromagneticData('micromagneticdata').name == name
