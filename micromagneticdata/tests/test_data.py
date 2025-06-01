import os
import textwrap
from pathlib import Path

import ipywidgets
import pandas as pd
import pytest

import micromagneticdata as md


class TestData:
    def setup_method(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "rectangle"
        self.data = md.Data(name=self.name, dirname=self.dirname)
        self.N_SAMPLES = 7

    def test_init(self):
        assert isinstance(self.data, md.Data)

        with pytest.raises(IOError):
            md.Data(path=Path(self.dirname) / "nonexistent")

        with pytest.raises(IOError):
            md.Data(name="wrong", dirname=self.dirname)

    def test_repr(self):
        assert isinstance(repr(self.data), str)
        assert "Data" in repr(self.data)

    def test_info(self):
        assert isinstance(self.data.info, pd.DataFrame)
        assert len(self.data.info.index) == self.N_SAMPLES

    def test_info_missing_corrupt(self, tmp_path):
        for i in range(3):
            (tmp_path / "system" / f"drive-{i}").mkdir(parents=True)

        # missing info.json for drive-0

        # broken info.json for drive-1
        (tmp_path / "system" / "drive-1" / "info.json").write_text('{"drive_number": 1')

        # correct info.json for drive-2
        info_text = textwrap.dedent(
            """
            {
                "drive_number": 2,
                "date": "2025-05-31",
                "time": "20:29:33",
                "start_time": "2025-05-31T20:29:33",
                "adapter": "oommfc",
                "adapter_version": "0.65.0",
                "driver": "MinDriver",
                "end_time": "2025-05-31T20:29:33",
                "elapsed_time": "00:00:01",
                "success": true}
            """
        )
        (tmp_path / "system" / "drive-2" / "info.json").write_text(info_text)

        data = md.Data(name="system", dirname=str(tmp_path))
        info = data.info
        assert info["info.json"].to_list() == ["missing", "corrupt", "available"]

    def test_n(self):
        assert self.data.n == self.N_SAMPLES

    def test_getitem(self):
        for i in range(-self.N_SAMPLES, self.N_SAMPLES):
            assert isinstance(self.data[i], md.Drive)

    def test_iter(self):
        assert len(list(self.data)) == self.N_SAMPLES

    def test_selector(self):
        assert isinstance(self.data.selector(), ipywidgets.BoundedIntText)
