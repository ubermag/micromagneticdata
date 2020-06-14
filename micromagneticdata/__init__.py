import pytest
import pkg_resources
from .data import Data
from .drive import Drive

__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)


def test():
    return pytest.main(['-v', '--pyargs',
                        'micromagneticdata'])  # pragma: no cover
