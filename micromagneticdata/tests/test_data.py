import os

import ipywidgets
import pandas as pd
import pytest

import micromagneticdata as md


class TestData:
    def setup_method(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "system_name"
        self.data = md.Data(name=self.name, dirname=self.dirname)
        self.N_SAMPLES = 7

    def test_init(self):
        assert isinstance(self.data, md.Data)

        # Exception
        with pytest.raises(IOError):
            md.Data(name="wrong", dirname=self.dirname)

    def test_repr(self):
        assert isinstance(repr(self.data), str)
        assert "Data" in repr(self.data)

    def test_info(self):
        assert isinstance(self.data.info, pd.DataFrame)
        assert len(self.data.info.index) == self.N_SAMPLES

    def test_n(self):
        assert self.data.n == self.N_SAMPLES

    def test_getitem(self):
        for i in range(-self.N_SAMPLES, self.N_SAMPLES):
            assert isinstance(self.data[i], md.Drive)

    def test_iter(self):
        assert len(list(self.data)) == self.N_SAMPLES

    def test_selector(self):
        assert isinstance(self.data.selector(), ipywidgets.BoundedIntText)
