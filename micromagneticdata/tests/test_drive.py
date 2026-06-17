# from micromagneticdata.testing.drive import *  # noqa: F403

import importlib.metadata
import os
from pathlib import Path

import discretisedfield as df
import ipywidgets
import numpy as np
import pytest
import ubermagtable as ut
import xarray as xr
from discretisedfield.tests.test_field import check_hv

import micromagneticdata as mdata


@pytest.fixture
def drive():
    """Fixture that returns a single drive.

    Parametrize the fixture to test different types of drives.
    """
    pass


@pytest.fixture
def drive_x():
    pass


@pytest.fixture
def new_drive_column():
    pass


#####################


@pytest.fixture
def sample_drive(monkeypatch):
    def mock_entry_points(*args, **kwargs):
        print("inside the mock")
        return importlib.metadata.EntryPoints(
            [
                importlib.metadata.EntryPoint(
                    name="test",
                    group="micromagneticdata.plugins.CalculatorDrive",
                    value="micromagneticdata.tests.test_drive:SampleDrive",
                )
            ]
        )

    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)
    # length 25
    return SampleDrive("abc", 0, adapter="test")


@pytest.fixture
def self():
    pass


#####################


class SampleDrive(mdata.Drive):
    @mdata.AbstractDrive.x.setter
    def x(self, value):
        self._x = value

    @property
    def _table_path(self):
        return self.drive_path / "table.csv"

    @property
    def _step_file_glob(self):
        return self.drive_path.glob("m-*.hdf5")

    @property
    def calculator_script():
        return "test calculator"


#####################

# TODO test plugin registration


def test_init(sample_drive):
    # str for dirname
    sample_drive = sample_drive
    drive = mdata.Drive(name=sample_drive.name, number=0, dirname=sample_drive.dirname)
    assert isinstance(drive, mdata.Drive)

    # Path for dirname
    drive2 = mdata.Drive(
        name=sample_drive.name, number=0, dirname=Path(sample_drive.dirname)
    )
    assert isinstance(drive2, mdata.Drive)
    assert drive.name == drive2.name
    assert drive.number == drive2.number
    assert drive.dirname == drive2.dirname

    # Exception
    with pytest.raises(IOError):
        drive = mdata.Drive(
            name=sample_drive.name, number=11, dirname=sample_drive.dirname
        )


def test_n(drive):
    assert isinstance(drive.n, int)


def test_repr(drive):
    assert isinstance(repr(drive), str)
    assert "Drive" in repr(drive)


def test_info(self):
    for i, drive in enumerate(self.data):
        assert isinstance(drive.info, dict)
        assert drive.info["drive_number"] == i


def test_valid(drive):
    dirname = os.path.join(os.path.dirname(__file__), "test_sample")
    name = "hysteresis"
    data = mdata.Data(name=name, dirname=dirname)
    m0_field = data[0].m0
    test_points = [
        m0_field.mesh.point2index(m0_field.mesh.region.pmin),
        m0_field.mesh.point2index(m0_field.mesh.region.center),
        m0_field.mesh.point2index(m0_field.mesh.region.pmax),
    ]
    expected_validity = [False, True, False]
    for point, expected in zip(test_points, expected_validity):
        actual_valid = m0_field.valid[point]
        assert actual_valid == expected

    drive = data[0]
    for d in drive:
        for point, expected in zip(test_points, expected_validity):
            actual_valid = d.valid[point]
            assert actual_valid == expected


def test_n_reference_data(sample_drive):
    assert sample_drive.n == 25


def test_iter_reference_data(sample_drive):
    assert len(list(sample_drive)) == 25


def test_getitem_slice(sample_drive):
    assert sample_drive.n == 25

    sel = sample_drive[:]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 25
    assert len(list(sel)) == 25
    assert sel.use_cache

    sel = sample_drive[:1]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 1
    assert len(list(sel)) == 1
    assert sel.use_cache

    sel = sample_drive[:-3]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 22
    assert len(list(sel)) == 22
    assert sel.use_cache

    sel = sample_drive[4:8]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 4
    assert len(list(sel)) == 4
    assert sel.use_cache

    sel = sample_drive[::2]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 13
    assert len(list(sel)) == 13
    assert sel.use_cache


def test_to_xarray(drive):
    assert isinstance(drive.to_xarray(), xr.DataArray)
    assert all(item in drive.to_xarray().attrs.items() for item in drive.info.items())
    if len(drive._step_files) != 1:
        assert len(drive.to_xarray()[drive.table.x]) == len(drive._step_files)
        assert np.allclose(
            drive.to_xarray()[drive.table.x].values,
            drive.table.data[drive.table.x].to_numpy(),
        )


def test_hv_time_drive(self):
    # time drive
    check_hv(
        self.data[0].hv(kdims=["y", "z"], vdims=["y", "z"]),
        ["DynamicMap [x,t]", "Image [y,z]", "VectorField [y,z]"],
    )
    check_hv(
        self.data[0].hv.scalar(kdims=["y", "z"]),
        ["DynamicMap [x,vdims,t]", "Image [y,z]"],
    )

    with pytest.raises(NotImplementedError):
        check_hv(self.data[0].hv.scalar(kdims=["x", "t"]), ...)


def test_hv_min_drive(self):
    # min drive
    check_hv(
        self.data[4]
        .register_callback(lambda f: f.sel("z"))
        .hv.vector(kdims=["x", "y"]),
        ["VectorField [x,y]"],
    )


def test_hv_min_drive_steps(self):
    # min drive with steps
    check_hv(
        self.data[6].hv.vector(kdims=["x", "y"]),
        ["DynamicMap [z,iteration]", "VectorField [x,y]"],
    )


def test_lshift(self):
    # TimeDriver: 0, 1, 2, 5
    # MinDriver: 4, 6
    # RelaxDriver: 3
    # HysteresisDriver: 7 [CURRENTLY MISSING IN THE DATASET]
    for d1, d2 in [(0, 1), (6, 6), (3, 3)]:
        combined = self.data[d1] << self.data[d2]
        assert isinstance(combined, mdata.CombinedDrive)
        assert len(combined.drives) == 2
        assert combined.info["driver"] == self.data[d1].info["driver"]
        assert combined.x == self.data[d1].x
        assert len(combined.table.data) == combined.n

    for d1, d2 in [(0, 6), (3, 6), (4, 6)]:
        # TODO
        # (0, 3), (0, 4) should be added and fail
        # (4, 6) mixes OOMMF and Mumax3 min drive which does not work because
        # they have different independent variables
        with pytest.raises(ValueError):
            self.data[d1] << self.data[d2]
    with pytest.raises(TypeError):
        self.data[0] << 1


def test_register_callback(self):
    for drive in self.data:
        drive_orientation = drive.register_callback(lambda field: field.orientation)
        assert isinstance(drive_orientation, drive.__class__)
        assert len(drive_orientation._callbacks) == 1
        for field in drive_orientation:
            assert np.max(field.array) <= 1.0
            assert np.min(field.array) >= -1.0

    drive = self.data[0]
    processed = drive.register_callback(lambda f: f.orientation)
    processed = processed.register_callback(lambda f: f.x)
    for field in processed:
        assert field.nvdim == 1
        assert np.max(field.array) <= 1.0
        assert np.min(field.array) >= -1.0

    assert len(processed.callbacks) == 2


def test_cache(sample_drive, monkeypatch):
    drive = mdata.Drive(
        sample_drive.name,
        sample_drive.number,
        sample_drive.dirname,
        sample_drive.x,
        use_cache=True,
    )

    assert len(list(drive)) == 25
    assert isinstance(drive[0], df.Field)
    assert isinstance(drive.table, ut.Table)

    with monkeypatch.context() as m:
        m.setattr(drive.__class__, "_step_file_glob", ["a.omf", "b.omf"])
        m.setattr(drive.__class__, "_table_path", "wrong_path")

        assert len(drive._step_files) == 25
        assert isinstance(drive[0], df.Field)
        assert isinstance(drive.table, ut.Table)

        drive.use_cache = False

        assert drive._step_files == ["a.omf", "b.omf"]
        with pytest.raises(FileNotFoundError):
            drive[0]
        with pytest.raises(FileNotFoundError):
            drive.table  # noqa: B018

        drive.use_cache = True  # check new caching (no old cache)

        assert drive._step_files == ["a.omf", "b.omf"]
        with pytest.raises(FileNotFoundError):
            drive[0]
        with pytest.raises(FileNotFoundError):
            drive.table  # noqa: B018

    # caching has effects outside monkeypatch context
    assert drive._step_files == ["a.omf", "b.omf"]
    with pytest.raises(FileNotFoundError):
        drive[0]
    # no table object is cached
    assert isinstance(drive.table, ut.Table)

    drive.use_cache = False  # remove cached monkeypatch
    drive.use_cache = True  # check new caching (no old cache)

    assert len(list(drive)) == 25
    assert isinstance(drive[0], df.Field)
    assert isinstance(drive.table, ut.Table)


def test_slider(drive):
    assert isinstance(drive.slider(), ipywidgets.IntSlider)
