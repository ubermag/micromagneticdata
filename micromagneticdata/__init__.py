"""Analyse micromagnetic data."""
import pytest
import pkg_resources
from .data import Data
from .drive import Drive

__version__ = pkg_resources.get_distribution(__name__).version


def test():
    """Run all package tests.

    Examples
    --------
    1. Run all tests.

    >>> import micromagneticdata
    ...
    >>> # micromagneticdata.test()

    """
    return pytest.main(['-v', '--pyargs',
                        'micromagneticdata', '-l'])  # pragma: no cover
