import os
import pytest
import tempfile
import ipywidgets
import ubermagtable as ut
import discretisedfield as df
import micromagneticdata as md


class TestDrive:
    def setup(self):
        self.dirname = os.path.join(os.path.dirname(__file__), 'test_sample')
        self.name = 'system_name'
        self.data = md.Data(name=self.name, dirname=self.dirname)

    def test_init(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)
        assert isinstance(drive, md.Drive)

        # Exception
        with pytest.raises(IOError):
            drive = md.Drive(name=self.name, number=9, dirname=self.dirname)

    def test_repr(self):
        for drive in self.data:
            assert isinstance(repr(drive), str)
            assert 'Drive' in repr(drive)

    def test_x(self):
        for drive in self.data:
            assert isinstance(drive.x, str)
            assert drive.x in ['t', 'iteration', 'B_hysteresis']

        self.data[0].x = 'mx'
        # Exception
        with pytest.raises(ValueError):
            self.data[0].x = 'wrong'

    def test_info(self):
        for i, drive in enumerate(self.data):
            assert isinstance(drive.info, dict)
            assert drive.info['drive_number'] == i

    def test_mif(self):
        for drive in self.data:
            assert isinstance(drive.mif, str)
            assert 'MIF' in drive.mif

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
