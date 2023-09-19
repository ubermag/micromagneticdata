import os

import discretisedfield as df
import ipywidgets
import numpy as np
import pytest
import ubermagtable as ut
import xarray as xr
from discretisedfield.tests.test_field import check_hv

import micromagneticdata as md


class TestDrive:
    def setup_method(self):
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
        for i in [0, 5, 6]:
            drive = self.data[i]
            assert isinstance(drive.calculator_script, str)
            assert "MIF" in drive.calculator_script

    def test_mx3(self):
        for i in [1, 2, 3, 4]:
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

    def test_getitem_int(self):
        for i in range(self.data[0].n):
            assert isinstance(self.data[0][i], df.Field)

    def test_getitem_slice(self):
        drive = self.data[0]
        assert drive.n == 25

        sel = drive[:]
        assert isinstance(sel, md.Drive)
        assert sel.n == 25
        assert len(list(sel)) == 25
        assert sel.use_cache

        sel = drive[:1]
        assert isinstance(sel, md.Drive)
        assert sel.n == 1
        assert len(list(sel)) == 1
        assert sel.use_cache

        sel = drive[:-3]
        assert isinstance(sel, md.Drive)
        assert sel.n == 22
        assert len(list(sel)) == 22
        assert sel.use_cache

        sel = drive[4:8]
        assert isinstance(sel, md.Drive)
        assert sel.n == 4
        assert len(list(sel)) == 4
        assert sel.use_cache

        sel = drive[::2]
        assert isinstance(sel, md.Drive)
        assert sel.n == 13
        assert len(list(sel)) == 13
        assert sel.use_cache

    def test_iter(self):
        for drive in self.data:
            for m in drive:
                assert isinstance(m, df.Field)

        assert len(list(self.data[0])) == 25

    def test_ovf2vtk(self, tmp_path):
        self.data[0].ovf2vtk(dirname=tmp_path)

    def test_slider(self):
        for drive in self.data:
            assert isinstance(drive.slider(), ipywidgets.IntSlider)

    def test_lshift(self):
        # TimeDriver: 0, 1, 2, 5
        # MinDriver: 4, 6
        # RelaxDriver: 3
        # HysteresisDriver: 7 [CURRENTLY MISSING IN THE DATASET]
        for d1, d2 in [(0, 1), (6, 6), (3, 3)]:
            combined = self.data[d1] << self.data[d2]
            assert isinstance(combined, md.CombinedDrive)
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

        # min drive
        check_hv(
            self.data[4]
            .register_callback(lambda f: f.sel("z"))
            .hv.vector(kdims=["x", "y"]),
            ["VectorField [x,y]"],
        )

        # min drive with steps
        check_hv(
            self.data[6].hv.vector(kdims=["x", "y"]),
            ["DynamicMap [z,iteration]", "VectorField [x,y]"],
        )

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

    def test_cache(self, monkeypatch):
        ref = self.data[0]
        drive = md.Drive(ref.name, ref.number, ref.dirname, ref.x, use_cache=True)

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
                drive.table

            drive.use_cache = True  # check new caching (no old cache)

            assert drive._step_files == ["a.omf", "b.omf"]
            with pytest.raises(FileNotFoundError):
                drive[0]
            with pytest.raises(FileNotFoundError):
                drive.table

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
