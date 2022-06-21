import os
import tempfile

import discretisedfield as df
import ipywidgets
import numpy as np
import pytest
import ubermagtable as ut
import xarray as xr

import micromagneticdata as md


class TestDrive:
    def setup(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "system_name"
        self.data = md.Data(name=self.name, dirname=self.dirname)

    def test_init(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)
        assert isinstance(drive, md.Drive)

        # Exception
        with pytest.raises(IOError):
            drive = md.Drive(name=self.name, number=11, dirname=self.dirname)

    def test_repr(self):
        for drive in self.data:
            assert isinstance(repr(drive), str)
            assert "Drive" in repr(drive)

    def test_x(self):
        for drive in self.data:
            assert isinstance(drive.x, str)
            assert drive.x in ["t", "iteration", "B_hysteresis"]

        self.data[0].x = "mx"
        # Exception
        with pytest.raises(ValueError):
            self.data[0].x = "wrong"

    def test_info(self):
        for i, drive in enumerate(self.data):
            assert isinstance(drive.info, dict)
            assert drive.info["drive_number"] == i

    def test_mif(self):
        for i in range(7):
            drive = self.data[i]
            assert isinstance(drive.calculator_script, str)
            assert "MIF" in drive.calculator_script

    def test_mx3(self):
        for i in range(7, 10):
            drive = self.data[i]
            assert isinstance(drive.calculator_script, str)
            assert "tableadd" in drive.calculator_script

    def test_m0(self):
        for drive in self.data:
            assert isinstance(drive.m0, df.Field)

    def test_table(self):
        for drive in self.data:
            assert isinstance(drive.table, ut.Table)
            assert drive.table.x == drive.x

    def test_n(self):
        for drive in self.data:
            assert isinstance(drive.n, int)
        assert self.data[0].n == 25

    def test_getitem(self):
        for i in range(self.data[0].n):
            assert isinstance(self.data[0][i], df.Field)

    def test_iter(self):
        for drive in self.data:
            for m in drive:
                assert isinstance(m, df.Field)

        assert len(list(self.data[0])) == 25

    def test_ovf2vtk(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.data[0].ovf2vtk(dirname=tmpdir)

    def test_slider(self):
        for drive in self.data:
            assert isinstance(drive.slider(), ipywidgets.IntSlider)

    def test_lshift(self):
        # drives 0, 1, 2, 4: TimeDriver
        # drives 3, 5: MinDriver
        # drives 6: HysteresisDriver
        for d1, d2 in [(0, 1), (3, 5), (6, 6)]:
            combined = self.data[d1] << self.data[d2]
            assert isinstance(combined, md.CombinedDrive)
            assert len(combined.drives) == 2
            assert combined.info["driver"] == self.data[d1].info["driver"]
            assert combined.x == self.data[d1].x
            assert len(combined.table.data) == combined.n

        for d1, d2 in [(0, 3), (0, 6), (3, 6)]:
            with pytest.raises(ValueError):
                self.data[d1] << self.data[d2]
        with pytest.raises(TypeError):
            self.data[0] << 1

    def test_to_xarray(self):
        for drive in self.data:
            assert isinstance(drive.to_xarray(), xr.DataArray)
            assert all(
                item in drive.to_xarray().attrs.items() for item in drive.info.items()
            )
            if len(drive._step_files) != 1:
                assert len(drive.to_xarray()[drive.table.x]) == len(drive._step_files)
                assert np.allclose(
                    drive.to_xarray()[drive.table.x].values,
                    drive.table.data[drive.table.x].to_numpy(),
                )

            if drive.info["driver"] == "HysteresisDriver":
                assert all(
                    np.allclose(
                        drive.to_xarray()[f"B{i}_hysteresis"].values,
                        drive.table.data[f"B{i}_hysteresis"].to_numpy(),
                    )
                    for i in "xyz"
                )

    def test_hv(self):
        for drive in self.data:
            # some drives have only one z layer -> only xy plane
            drive.hv(kdims=["x", "y"])
        # time drives: 0, 1, 2, 4
        plot = self.data[0].hv(kdims=["y", "z"], vdims=["y", "z"])
        assert len(plot.kdims) == 2
        assert "x" in plot.kdims
        assert "t" in plot.kdims

        plot = self.data[0].hv.scalar(kdims=["x", "t"])
        assert len(plot.kdims) == 3
        assert "comp" in plot.kdims
        assert "y" in plot.kdims
        assert "z" in plot.kdims

        plot = self.data[0].hv.vector(kdims=["x", "t"], vdims=["x", None], cdim="z")
        assert len(plot.kdims) == 2
        assert "y" in plot.kdims
        assert "z" in plot.kdims

        plot = self.data[2].hv.contour(kdims=["x", "t"])
        assert len(plot.kdims) == 3
        assert "comp" in plot.kdims
        assert "y" in plot.kdims
        assert "z" in plot.kdims
