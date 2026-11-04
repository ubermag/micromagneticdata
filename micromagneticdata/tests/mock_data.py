# Mock data for tests in micromagneticadata; adapter packages don't need this
# and should instead test with real data
import contextlib
import copy
import importlib.metadata
import json
import numbers
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

    def _read_field(self, filename):
        field = df.Field.from_file(filename)
        field.valid = "norm"
        return field

    @property
    def m0(self):
        return self._read_field(self._m0_path)

    def __getitem__(self, item):
        if isinstance(item, numbers.Integral):
            field = self._read_field(self._step_files[item])
            m0 = self.m0
            if not field.mesh.region.allclose(m0.mesh.region):
                field.mesh.translate(
                    m0.mesh.region.pmin - field.mesh.region.pmin, inplace=True
                )
            with contextlib.suppress(FileNotFoundError):
                field.mesh.load_subregions(self._m0_path)
            return self._apply_callbacks(field)
        elif isinstance(item, slice):
            step_files = self._step_files[item]
            table = copy.copy(self.table)
            table.data = table.data.iloc[item].reset_index()
            return self.__class__(
                self.name,
                self.number,
                self.dirname,
                self.x,
                use_cache=True,
                callbacks=self.callbacks,
                step_files=step_files,
                table=table,
            )
        else:
            raise TypeError(f"{type(item)=} is not supported")


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

    def _read_field(self, filename):
        return _unstructured_field(filename)

    def __getitem__(self, item):
        if isinstance(item, numbers.Integral):
            field = self._read_field(self._step_files[item])
            return self._apply_callbacks(field)
        return super().__getitem__(item)


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
                    name="micromagneticdata",
                    value="micromagneticdata.tests.mock_data:SampleDrive",
                    group="micromagneticdata.plugins.CalculatorDrive",
                ),
                importlib.metadata.EntryPoint(
                    name="unstructured_grid_adapter",
                    value="micromagneticdata.tests.mock_data:UnstructuredGridDrive",
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


def create_drive(base: Path, system_name, index, x, n_steps):
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
                "adapter": "micromagneticdata",
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
