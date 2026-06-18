import importlib.metadata
import json
import os
from pathlib import Path

import discretisedfield as df
import ipywidgets
import numpy as np
import pandas as pd
import pytest
import ubermagtable as ut
import xarray as xr
from discretisedfield.tests.test_field import check_hv

import micromagneticdata as mdata
from micromagneticdata.testing.drive import *  # noqa: F403


@pytest.fixture
def drive(tmp_path, monkeypatch):
    """Fixture that returns a single drive.

    Parametrize the fixture to test different types of drives.
    """
    # mock the plugin detection so that micromagneticadata can be tested without
    # any plugins; adapter packages must not do that
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system"
    index = 0
    _create_drive(tmp_path, system_name, index, n_steps=25)
    return SampleDrive(system_name, index, dirname=tmp_path)


@pytest.fixture
def drive_x():
    """Independent variable of the drive."""
    return "t"


@pytest.fixture
def new_drive_x():
    """An other column in drive.table, that can be used as indendent variable."""
    return "mx"


@pytest.fixture
def calculator_script_content():
    """Representative section of a calculator script."""
    return "run simulation"


#####################

# Mock data for tests in micromagneticadata; adapter packages don't need this section
# and should instead test with real data


class SampleDrive(mdata.Drive):
    @mdata.AbstractDrive.x.setter
    def x(self, value):
        value = value or "t"
        if value not in ["t", "mx", "my", "mz"]:
            raise ValueError(f"Unsupported x={value}")
        self._x = value

    @property
    def _table_path(self):
        return self.drive_path / "table.csv"

    @property
    def _step_file_glob(self):
        return self.drive_path.glob("m-*.hdf5")

    @property
    def calculator_script(self):
        return (self.drive_path / "script.txt").read_text()


def read_table(filename, x=None, rename=True):
    return ut.Table(
        pd.read_csv(filename), units={"t": "s", "mx": "", "my": "", "mz": ""}, x=x
    )


def mock_entry_points(group):
    # micromagneticdata.Drive detects plugins to load a suitable drive.
    # For testing we mock this to use the SampleDrive class.
    if group == "micromagneticdata.plugins.CalculatorDrive":
        return importlib.metadata.EntryPoints(
            [
                importlib.metadata.EntryPoint(
                    name="micromagneticdata",
                    value="micromagneticdata.tests.test_drive:SampleDrive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
            ]
        )
    elif group == "micromagneticdata.plugins.read_table":
        return importlib.metadata.EntryPoints(
            [
                importlib.metadata.EntryPoint(
                    name="micromagneticdata",
                    value="micromagneticdata.tests.test_drive:read_table",
                    group="micromagneticdata.plugins.read_table",
                ),
            ]
        )
    else:
        raise NotImplementedError(f"Group {group} not supported.")


def _create_drive(base: Path, system_name, index, n_steps):
    """Create a drive with 25 steps and metadata compatible with SampleDrive."""
    drive_dir = base / system_name / f"drive-{index}"
    drive_dir.mkdir(parents=True)
    # minimalistic info json, incomplete but sufficient for tests
    (drive_dir / "info.json").write_text(
        json.dumps(
            {
                "drive_number": index,
                "adapter": "micromagneticdata",
                "driver": "SampleDriver",
            }
        )
    )
    # fake tabular data
    pd.DataFrame(
        {
            "t": list(range(1, n_steps + 1)),
            "mx": [0] * n_steps,
            "my": [0] * n_steps,
            "mz": [1] * n_steps,
        }
    ).to_csv(drive_dir / "table.csv")
    m = df.Field(
        mesh=df.Mesh(p1=(0, 0, 0), p2=(1, 1, 1), n=(5, 5, 5)),
        nvdim=3,
        value=(0, 1, 1),
        norm=1e5,
    )
    # initial magnetisation
    m.to_file(drive_dir / "m0.omf")
    # fake output magnetisation
    for i in range(1, n_steps + 1):
        m.to_file(drive_dir / f"m-{i:03}.hdf5")
    # fake simulation script for the calculator
    (drive_dir / "script.txt").write_text("run simulation")


#####################

# TODO test plugin registration


def test_init(drive):
    # str for dirname
    created_drive = mdata.Drive(name=drive.name, number=0, dirname=drive.dirname)
    assert isinstance(created_drive, mdata.Drive)

    # Path for dirname
    drive2 = mdata.Drive(name=drive.name, number=0, dirname=Path(drive.dirname))
    assert isinstance(drive2, mdata.Drive)
    assert created_drive.name == drive2.name
    assert created_drive.number == drive2.number
    assert created_drive.dirname == drive2.dirname

    # Exception
    with pytest.raises(OSError):
        created_drive = mdata.Drive(name=drive.name, number=1, dirname=drive.dirname)


def test_repr(drive):
    assert isinstance(repr(drive), str)
    assert "Drive" in repr(drive)


def test_info(drive):
    assert isinstance(drive.info, dict)
    assert drive.info["drive_number"] == 0


@pytest.mark.skip
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


def test_n_reference_data(drive):
    assert drive.n == 25


def test_iter_reference_data(drive):
    assert len(list(drive)) == 25


def test_getitem_slice(drive):
    assert drive.n == 25

    sel = drive[:]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 25
    assert len(list(sel)) == 25
    assert sel.use_cache

    sel = drive[:1]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 1
    assert len(list(sel)) == 1
    assert sel.use_cache

    sel = drive[:-3]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 22
    assert len(list(sel)) == 22
    assert sel.use_cache

    sel = drive[4:8]
    assert isinstance(sel, mdata.Drive)
    assert sel.n == 4
    assert len(list(sel)) == 4
    assert sel.use_cache

    sel = drive[::2]
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


def test_hv_drive_scalar(drive):
    check_hv(
        drive.hv.scalar(kdims=["y", "z"]),
        ["DynamicMap [x,vdims,t]", "Image [y,z]"],
    )


def test_hv_drive_vector(drive):
    check_hv(
        drive.hv.vector(kdims=["x", "y"]),
        ["DynamicMap [z,t]", "VectorField [x,y]"],
    )


def test_hv_drive_combined(drive):
    check_hv(
        drive.hv(kdims=["y", "z"], vdims=["y", "z"]),
        ["DynamicMap [x,t]", "Image [y,z]", "VectorField [y,z]"],
    )


def test_hv_drive_t_not_as_kdim(drive):
    with pytest.raises(NotImplementedError):
        check_hv(drive.hv.scalar(kdims=["x", "t"]), ...)


def test_hv_drive_single_m(drive):
    # create a drive with a single element -> slider for t is omitted
    drive = drive[:1]
    check_hv(
        drive.register_callback(lambda f: f.sel("z")).hv.vector(kdims=["x", "y"]),
        ["VectorField [x,y]"],
    )


def test_lshift(drive):
    combined = drive << drive
    assert isinstance(combined, mdata.CombinedDrive)
    assert len(combined.drives) == 2
    assert combined.info["driver"] == drive.info["driver"]
    assert combined.x == drive.x
    assert len(combined.table.data) == combined.n

    with pytest.raises(TypeError):
        drive << 1


def test_register_callback(drive):
    drive_orientation = drive.register_callback(lambda field: field.orientation)
    assert isinstance(drive_orientation, drive.__class__)
    assert len(drive_orientation._callbacks) == 1
    for field in drive_orientation:
        assert np.max(field.array) <= 1.0
        assert np.min(field.array) >= -1.0
        assert field.nvdim == 3

    processed = drive_orientation.register_callback(lambda f: f.x)
    for field in processed:
        assert field.nvdim == 1
        assert np.max(field.array) <= 1.0
        assert np.min(field.array) >= -1.0
        assert field.nvdim == 1

    assert len(processed.callbacks) == 2


def test_cache(drive, monkeypatch):
    generated_drive = mdata.Drive(
        drive.name,
        drive.number,
        drive.dirname,
        drive.x,
        use_cache=True,
    )

    assert len(list(generated_drive)) == 25
    assert isinstance(generated_drive[0], df.Field)
    assert isinstance(generated_drive.table, ut.Table)

    with monkeypatch.context() as m:
        m.setattr(generated_drive.__class__, "_step_file_glob", ["a.omf", "b.omf"])
        m.setattr(generated_drive.__class__, "_table_path", "wrong_path")

        assert len(generated_drive._step_files) == 25
        assert isinstance(generated_drive[0], df.Field)
        assert isinstance(generated_drive.table, ut.Table)

        generated_drive.use_cache = False

        assert generated_drive._step_files == ["a.omf", "b.omf"]
        with pytest.raises(FileNotFoundError):
            generated_drive[0]
        with pytest.raises(FileNotFoundError):
            generated_drive.table  # noqa: B018

        generated_drive.use_cache = True  # check new caching (no old cache)

        assert generated_drive._step_files == ["a.omf", "b.omf"]
        with pytest.raises(FileNotFoundError):
            generated_drive[0]
        with pytest.raises(FileNotFoundError):
            generated_drive.table  # noqa: B018

    # caching has effects outside monkeypatch context
    assert generated_drive._step_files == ["a.omf", "b.omf"]
    with pytest.raises(FileNotFoundError):
        generated_drive[0]
    # no table object is cached
    assert isinstance(generated_drive.table, ut.Table)

    generated_drive.use_cache = False  # remove cached monkeypatch
    generated_drive.use_cache = True  # check new caching (no old cache)

    assert len(list(generated_drive)) == 25
    assert isinstance(generated_drive[0], df.Field)
    assert isinstance(generated_drive.table, ut.Table)


def test_slider(drive):
    assert isinstance(drive.slider(), ipywidgets.IntSlider)
