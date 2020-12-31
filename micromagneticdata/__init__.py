"""Main package"""
import pytest
import pkg_resources
from .data import Data
from .drive import Drive


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


__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)
