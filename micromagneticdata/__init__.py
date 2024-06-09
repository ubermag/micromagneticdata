"""Analyse micromagnetic data."""

import importlib.metadata

import pytest

from .abstract_drive import AbstractDrive as AbstractDrive
from .combined_drive import CombinedDrive as CombinedDrive
from .data import Data as Data
from .drive import Drive as Drive
from .mumax3drive import Mumax3Drive as Mumax3Drive
from .oommfdrive import OOMMFDrive as OOMMFDrive

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
