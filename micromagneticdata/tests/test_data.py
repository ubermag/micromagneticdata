import os
import types
import ipywidgets
import pandas as pd
import discretisedfield as df
import micromagneticdata as md


class TestData:
    def setup(self):
        self.dirname = os.path.dirname(__file__)
        self.name = 'test_sample'
        self.data = md.Data(name=self.name, dirname=self.dirname)

    def test_init(self):
        assert isinstance(self.data, md.Data)

    def test_n(self):
        assert self.data.n == 6

    def test_init(self):
        assert isinstance(self.data.drive(0), md.Drive)

    def test_iter(self):
        assert len(list(self.data)) == 6

    def test_info(self):
        assert isinstance(self.data.info, pd.DataFrame)

    def test_selector(self):
        assert isinstance(self.data.selector(), ipywidgets.BoundedIntText)
