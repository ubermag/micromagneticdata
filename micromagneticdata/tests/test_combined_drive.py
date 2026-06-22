import importlib.metadata
import os

import discretisedfield as df
import numpy as np
import pytest
import ubermagtable as ut
import xarray as xr
from discretisedfield.tests.test_field import check_hv

import micromagneticdata as md
from .mock_data import SampleDrive, create_drive, mock_entry_points


@pytest.fixture
def time_drive_1(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system"
    index = 0
    create_drive(tmp_path, system_name, index, "t", n_steps=25)
    return SampleDrive(system_name, index, dirname=tmp_path, x="t")


@pytest.fixture
def time_drive_2(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system"
    index = 1
    create_drive(tmp_path, system_name, index, "t", n_steps=20)
    return SampleDrive(system_name, index, dirname=tmp_path, x="t")


@pytest.fixture
def min_drive_1(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system"
    index = 2
    create_drive(tmp_path, system_name, index, "iteration", n_steps=1)
    return SampleDrive(system_name, index, dirname=tmp_path, x="iteration")


@pytest.fixture
def min_drive_2(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system2"
    index = 0
    create_drive(tmp_path, system_name, index, "iteration", n_steps=10)
    return SampleDrive(system_name, index, dirname=tmp_path, x="iteration")


@pytest.fixture
def combined_time_drive(time_drive_1, time_drive_2):
    return md.CombinedDrive(time_drive_1, time_drive_2)


@pytest.fixture
def combined_min_drive(min_drive_1, min_drive_2):
    return md.CombinedDrive(min_drive_1, min_drive_2)


def old():
    # TimeDriver: 0, 1, 2, 5
    # MinDriver: 4, 6
    # RelaxDriver: 3
    # HysteresisDriver: 7 [CURRENTLY MISSING IN THE DATASET]
    def setup_method(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "rectangle"
        self.data = md.Data(name=self.name, dirname=self.dirname)
        self.combined_drives = [
            self.data[0] << self.data[1] << self.data[2],
            self.data[3] << self.data[3],
            self.data[6] << self.data[6],
        ]
        data = md.Data(name="hysteresis", dirname=self.dirname)
        self.combined_drives.append(data[0] << data[0])


def test_init(time_drive_1, time_drive_2):
    combined_drive = md.CombinedDrive(time_drive_1, time_drive_2)
    assert isinstance(combined_drive, md.CombinedDrive)

    # at least two drives must be passed
    with pytest.raises(ValueError):
        md.CombinedDrive(time_drive_1)

    with pytest.raises(TypeError):
        md.CombinedDrive(time_drive_1, "wrong type")


def test_repr(combined_time_drive):
    assert isinstance(repr(combined_time_drive), str)
    assert "CombinedDrive" in repr(combined_time_drive)
    assert "Drive" in repr(combined_time_drive)


def test_x_time_drive(combined_time_drive):
    assert combined_time_drive.x == "t"

    combined_time_drive.x = "mx"
    assert combined_time_drive.x == "mx"

    with pytest.raises(ValueError):
        combined_time_drive.x = "wrong"


def test_x_min_drive(combined_min_drive):
    assert combined_min_drive.x == "iteration"


def test_info_time_drive(combined_time_drive):
    assert isinstance(combined_time_drive.info, dict)
    assert combined_time_drive.info["drive_numbers"] == [0, 1]
    assert combined_time_drive.info["driver"] == "TimeDriver"


def test_info_min_drive(combined_min_drive):
    assert isinstance(combined_min_drive.info, dict)
    assert combined_min_drive.info["drive_numbers"] == [2, 0]
    assert combined_min_drive.info["driver"] == "MinDriver"


def test_m0(combined_time_drive):
    assert isinstance(combined_time_drive.m0, df.Field)


def test_table_time_drive(combined_time_drive):
    assert isinstance(combined_time_drive.table, ut.Table)
    assert combined_time_drive.table.x == combined_time_drive.x


def test_n(combined_time_drive, combined_min_drive):
    assert combined_time_drive.n == 45
    assert combined_min_drive.n == 11


def test_getitem(combined_min_drive):
    assert all(
        isinstance(combined_min_drive[i], df.Field) for i in range(combined_min_drive.n)
    )


def test_iter(combined_min_drive):
    for m in combined_min_drive:
        assert isinstance(m, df.Field)

    assert len(list(combined_min_drive)) == 11


def test_lshift(combined_time_drive, time_drive_1, combined_min_drive, min_drive_1):
    # two combined drives with independent variable t
    combined = combined_time_drive << combined_time_drive
    assert isinstance(combined, md.CombinedDrive)
    assert len(combined.drives) == 4
    assert combined.info["driver"] == "TimeDriver"
    assert combined.x == "t"
    assert combined.n == 90
    assert len(combined.table.data) == 90

    for drive1, drive2 in [
        (combined_time_drive, time_drive_1),
        (time_drive_1, combined_time_drive),
    ]:
        combined = drive1 << drive2
        assert isinstance(combined, md.CombinedDrive)
        assert len(combined.drives) == 3
        assert combined.info["driver"] == "TimeDriver"
        assert combined.x == "t"
        assert combined.n == 70
        assert len(combined.table.data) == 70

    combined = combined_min_drive << combined_min_drive
    assert isinstance(combined, md.CombinedDrive)
    assert len(combined.drives) == 4
    assert combined.info["driver"] == "MinDriver"
    assert combined.x == "iteration"
    assert combined.n == 22
    assert len(combined.table.data) == 22

    for drive1, drive2 in [
        (combined_min_drive, min_drive_1),
        (min_drive_1, combined_min_drive),
    ]:
        combined = drive1 << drive2
        assert isinstance(combined, md.CombinedDrive)
        assert len(combined.drives) == 3
        assert combined.info["driver"] == "MinDriver"
        assert combined.x == "iteration"
        assert combined.n == 12
        assert len(combined.table.data) == 12

    with pytest.raises(ValueError):
        combined_min_drive << combined_time_drive
    with pytest.raises(ValueError):
        combined_time_drive << min_drive_1
    with pytest.raises(TypeError):
        combined_time_drive << "wrong type"


def test_to_xarray(combined_min_drive):
    assert isinstance(combined_min_drive.to_xarray(), xr.DataArray)
    assert all(
        item in combined_min_drive.to_xarray().attrs.items()
        for item in combined_min_drive.info.items()
    )
    assert len(combined_min_drive.to_xarray()[combined_min_drive.table.x]) == 11
    assert np.allclose(
        combined_min_drive.to_xarray()[combined_min_drive.table.x].values,
        combined_min_drive.table.data[combined_min_drive.table.x].to_numpy(),
    )

    def test_register_callback(combined_min_drive):
        drive_orientation = combined_min_drive.register_callback(
            lambda field: field.orientation
        )
        assert isinstance(drive_orientation, combined_min_drive.__class__)
        assert len(drive_orientation._callbacks) == 1
        for field in drive_orientation:
            assert np.max(field.array) <= 1.0
            assert np.min(field.array) >= -1.0

        processed = drive_orientation.register_callback(lambda f: f.x)
        for field in processed:
            assert field.nvdim == 1
            assert np.max(field.array) <= 1.0
            assert np.min(field.array) >= -1.0

        assert len(processed.callbacks) == 2


def test_hv(combined_time_drive, combined_min_drive):
    # time drive
    check_hv(
        combined_time_drive.hv(kdims=["y", "z"], vdims=["y", "z"]),
        ["DynamicMap [x,t]", "Image [y,z]", "VectorField [y,z]"],
    )
    check_hv(
        combined_time_drive.hv.scalar(kdims=["y", "z"]),
        ["DynamicMap [x,vdims,t]", "Image [y,z]"],
    )

    with pytest.raises(NotImplementedError):
        check_hv(combined_time_drive.hv.scalar(kdims=["x", "t"]), ...)

    # min drive with steps
    check_hv(
        combined_min_drive.register_callback(lambda f: f.sel("y")).hv.vector(
            kdims=["x", "z"]
        ),
        ["DynamicMap [iteration]", "VectorField [x,z]"],
    )
