import itertools
import os

import discretisedfield as df
import numpy as np
import pytest
import ubermagtable as ut
import xarray as xr

import micromagneticdata as md


class TestDrive:
    # drives 0, 1, 2, 4: TimeDriver
    # drives 3, 5: MinDriver
    # drives 6: HysteresisDriver
    def setup(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "system_name"
        self.data = md.Data(name=self.name, dirname=self.dirname)
        self.combined_drives = [
            self.data[0] << self.data[1] << self.data[2],
            self.data[3] << self.data[5],
            self.data[6] << self.data[6],
        ]

    def test_init(self):
        combined_drive = md.CombinedDrive(self.data[0], self.data[1])
        assert isinstance(combined_drive, md.CombinedDrive)
        with pytest.raises(ValueError):
            md.CombinedDrive(self.data[0])
        with pytest.raises(TypeError):
            md.CombinedDrive(self.data[0], "wrong type")

    def test_repr(self):
        for combined in self.combined_drives:
            assert isinstance(repr(combined), str)
            assert "CombinedDrive" in repr(combined)
            assert "Drive" in repr(combined)

    def test_x(self):
        for combined in self.combined_drives:
            assert isinstance(combined.x, str)

            assert combined.x in ["t", "iteration", "B_hysteresis"]

        self.combined_drives[0].x = "mx"
        with pytest.raises(ValueError):
            self.combined_drives[0].x = "wrong"

    def test_info(self):
        for combined in self.combined_drives:
            assert isinstance(combined.info, dict)
            assert isinstance(combined.info["drive_numbers"], list)
            assert combined.info["driver"] in [
                "MinDriver",
                "TimeDriver",
                "HysteresisDriver",
            ]

    def test_m0(self):
        for drive in self.combined_drives:
            assert isinstance(drive.m0, df.Field)

    def test_table(self):
        for drive in self.combined_drives:
            assert isinstance(drive.table, ut.Table)
            assert drive.table.x == drive.x

    def test_n(self):
        assert tuple(drive.n for drive in self.combined_drives) == (50, 15, 82)

    def test_getitem(self):
        assert all(
            isinstance(self.combined_drives[1][i], df.Field)
            for i in range(self.combined_drives[1].n)
        )

    def test_iter(self):
        for drive in self.combined_drives:
            for m in drive:
                assert isinstance(m, df.Field)

        assert len(list(self.combined_drives[0])) == 50

    def test_lshift(self):
        # drives 0, 1, 2, 4: TimeDriver
        # drives 3, 5: MinDriver
        # drives 6: HysteresisDriver
        for d1, d2, n_drives in itertools.chain(
            zip(self.combined_drives, self.combined_drives, [6, 4, 4]),
            zip(
                self.combined_drives,
                [self.data[0], self.data[3], self.data[6]],
                [4, 3, 3],
            ),
            zip(
                [self.data[0], self.data[3], self.data[6]],
                self.combined_drives,
                [4, 3, 3],
            ),
        ):
            combined = d1 << d2
            assert isinstance(combined, md.CombinedDrive)
            assert len(combined.drives) == n_drives
            assert combined.info["driver"] == d1.info["driver"]
            assert combined.x == d1.x
            assert len(combined.table.data) == combined.n

        # different independent variable
        with pytest.raises(ValueError):
            self.combined_drives[0] << self.data[3]
        with pytest.raises(ValueError):
            self.combined_drives[0] << self.combined_drives[1]
        with pytest.raises(TypeError):
            self.combined_drives[0] << 1

    def test_to_xarray(self):
        for drive in self.combined_drives:
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
