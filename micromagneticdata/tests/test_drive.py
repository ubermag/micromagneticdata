import os
import types
import ipywidgets
import discretisedfield as df
import micromagneticdata as md


class TestDrive:
    def setup(self):
        self.dirname = os.path.dirname(__file__)
        self.name = 'test_sample'

    def test_init(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)

        assert isinstance(drive, md.Drive)

    def test_info(self):
        drive = md.Drive(name=self.name, number=1, dirname=self.dirname)

        assert isinstance(drive.info, dict)
        assert drive.info['drive_number'] == 1

    def test_mif(self):
        drive = md.Drive(name=self.name, number=2, dirname=self.dirname)

        assert isinstance(drive.mif, str)
        assert 'MIF' in drive.mif

    def test_m0(self):
        drive = md.Drive(name=self.name, number=3, dirname=self.dirname)

        assert isinstance(drive.m0, df.Field)

    def test_n(self):
        drive = md.Drive(name=self.name, number=4, dirname=self.dirname)

        assert isinstance(drive.n, int)
        assert drive.n == 5

    def test_step_filenames(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)

        assert isinstance(drive.step_filenames, types.GeneratorType)
        assert len(list(drive.step_filenames)) == 25
        assert all([isinstance(i, str) for i in drive.step_filenames])

    def test_step(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)

        for i in range(drive.n):
            assert isinstance(drive.step(i), df.Field)

    def test_iter(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)

        assert len(list(drive)) == 25
        assert all([isinstance(i, df.Field) for i in drive])

    def test_ovf2vtk(self):
        drive = md.Drive(name=self.name, number=2, dirname=self.dirname)

        drive.ovf2vtk()

    def test_slider(self):
        drive = md.Drive(name=self.name, number=0, dirname=self.dirname)

        assert isinstance(drive.slider(), ipywidgets.IntSlider)
