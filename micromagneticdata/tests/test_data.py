import importlib.metadata
import textwrap

import ipywidgets
import pandas as pd
import pytest

import micromagneticdata as mdata
from .mock_data import create_drive, mock_entry_points


@pytest.fixture
def data(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

    system_name = "test_system"
    create_drive(tmp_path, system_name, 0, "iteration", n_steps=1)
    create_drive(tmp_path, system_name, 1, "t", n_steps=20)
    create_drive(tmp_path, system_name, 2, "t", n_steps=5)
    create_drive(tmp_path, system_name, 3, "iteration", n_steps=10)
    return mdata.Data(name=system_name, dirname=tmp_path)


def test_init(data):
    assert isinstance(data, mdata.Data)

    with pytest.raises(IOError):
        mdata.Data(path=data.dirname / "nonexistent")

    with pytest.raises(IOError):
        mdata.Data(name="wrong", dirname=data.dirname)


def test_repr(data):
    assert isinstance(repr(data), str)
    assert "Data" in repr(data)


def test_info(data):
    assert isinstance(data.info, pd.DataFrame)
    assert len(data.info.index) == 4


def test_info_missing_corrupt(monkeypatch, tmp_path):
    monkeypatch.setattr(importlib.metadata, "entry_points", mock_entry_points)

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
            "adapter": "micromagneticdata",
            "adapter_version": "0.65.0",
            "driver": "MinDriver",
            "end_time": "2025-05-31T20:29:33",
            "elapsed_time": "00:00:01",
            "success": true}
        """
    )
    (tmp_path / "system" / "drive-2" / "info.json").write_text(info_text)

    data = mdata.Data(name="system", dirname=str(tmp_path))
    info = data.info
    assert info["info.json"].to_list() == ["missing", "corrupt", "available"]


def test_n(data):
    assert data.n == 4


def test_getitem(data):
    for i in range(-4, 4):
        assert isinstance(data[i], mdata.Drive)


def test_iter(data):
    assert len(list(data)) == 4


def test_selector(data):
    assert isinstance(data.selector(), ipywidgets.BoundedIntText)
