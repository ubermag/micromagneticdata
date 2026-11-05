# Mock data for tests in micromagneticadata; adapter packages don't need this
# and should instead test with real data
import importlib.metadata
import json
from importlib.metadata import entry_points as importlib_metadata_entry_points
from pathlib import Path

import discretisedfield as df
import numpy as np
import pandas as pd
import pyvista as pv
import ubermagtable as ut

import micromagneticdata as mdata


class SampleDrive(mdata.Drive):
    @mdata.AbstractDrive.x.setter
    def x(self, value):
        value = value or "t"  # fall back to time driver by default
        if value not in ["t", "iteration", "mx", "my", "mz"]:
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

    def _read_m(self, filename):
        field = df.Field.from_file(filename)
        field.valid = "norm"
        return field


class MockOOMMFDrive(SampleDrive):
    """Mock drive selected for legacy OOMMF data."""


class MockMumax3Drive(SampleDrive):
    """Mock drive selected for legacy MuMax3 data."""


def _unstructured_field(filename):
    points = np.array([[0, 0, 0], [1e-9, 0, 0], [0, 1e-9, 0], [0, 0, 1e-9]])
    field = pv.UnstructuredGrid(
        np.array([4, 0, 1, 2, 3]),
        np.array([pv.CellType.TETRA]),
        points,
    )
    field.point_data["m"] = np.tile((0.0, 0.0, 1.0), (field.n_points, 1))
    field.field_data["filename"] = [str(filename)]
    return field


class UnstructuredGridDrive(SampleDrive):
    """Drive returning unstructured-grid magnetisation fields."""

    def _read_m(self, filename):
        return _unstructured_field(filename)


def read_table(filename, x=None, rename=True):
    return ut.Table(
        pd.read_csv(filename), units={x: "s", "mx": "", "my": "", "mz": ""}, x=x
    )


def mock_entry_points(group):
    # micromagneticdata.Drive detects plugins to load a suitable drive.
    # For testing we mock this to use the SampleDrive class.
    if group == "micromagneticdata.plugins.CalculatorDrive":
        return importlib.metadata.EntryPoints(
            [
                importlib.metadata.EntryPoint(
                    name="discretisedfield_field_sample",
                    value="micromagneticdata.tests.mock_data:SampleDrive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
                importlib.metadata.EntryPoint(
                    name="pyvista_unstructured_grid_sample",
                    value="micromagneticdata.tests.mock_data:UnstructuredGridDrive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
                importlib.metadata.EntryPoint(
                    name="oommfc",
                    value="micromagneticdata.tests.mock_data:MockOOMMFDrive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
                importlib.metadata.EntryPoint(
                    name="mumax3c",
                    value="micromagneticdata.tests.mock_data:MockMumax3Drive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
            ]
        )
    elif group == "micromagneticdata.plugins.read_table":
        return importlib.metadata.EntryPoints(
            [
                importlib.metadata.EntryPoint(
                    name="micromagneticdata",
                    value="micromagneticdata.tests.mock_data:read_table",
                    group="micromagneticdata.plugins.read_table",
                ),
            ]
        )
    else:
        return importlib_metadata_entry_points(group=group)


def create_drive(
    base: Path,
    system_name,
    index,
    x,
    n_steps,
    adapter="discretisedfield_field_sample",
):
    """Create a drive with n_steps steps and metadata compatible with SampleDrive."""
    # support time driver and min driver
    driver_name = {
        "t": "TimeDriver",
        "iteration": "MinDriver",
    }
    drive_dir = base / system_name / f"drive-{index}"
    drive_dir.mkdir(parents=True)
    # minimalistic info json, incomplete but sufficient for tests
    (drive_dir / "info.json").write_text(
        json.dumps(
            {
                "drive_number": index,
                "adapter": adapter,
                "driver": driver_name[x],
            }
        )
    )
    # fake tabular data
    pd.DataFrame(
        {
            x: list(range(1, n_steps + 1)),
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
