"""Analyse micromagnetic data."""

import importlib.metadata

import pytest

from .abstract_drive import AbstractDrive
from .combined_drive import CombinedDrive
from .data import Data
from .drive import Drive
from .mumax3drive import Mumax3Drive
from .oommfdrive import OOMMFDrive

__version__ = importlib.metadata.version(__package__)


def test():
    """Run all package tests.

    Examples
    --------
    1. Run all tests.

    >>> import micromagneticdata
    ...
    >>> # micromagneticdata.test()

    """
    return pytest.main(
        ["-v", "--pyargs", "micromagneticdata", "-l"]
    )  # pragma: no cover
