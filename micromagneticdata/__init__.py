import pytest
import pkg_resources
from .micromagneticdata import MicromagneticData


def test():
    return pytest.main(["-v", "--pyargs", "micromagneticmodel"])  # pragma: no cover

__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)
