import os
import re
import json
import glob
import pandas as pd
import micromagneticmodel as mm
from .analysis import PlotFig
from .drive import Drive
from .util import drives_number


class MicromagneticData:
    """
    Examples
    --------
    Simple import.

    >>> import micromagneticdata

    """
    def __init__(self, name, numbers=None):
        self.name = name

        if numbers is None:
            self.numbers = self._all_drives
        else:
            self.numbers = numbers

    @property
    def _all_drives(self):
        dirs = glob.glob(os.path.join(self.name, 'drive-*'))
        numbers = [int(re.findall('[0-9]+', d)[0]) for d in dirs]
        return sorted(numbers)

    @property
    def drives(self):
        for n in self.numbers:
            yield Drive(self.name, n)

    @property
    def metadata(self):
        data = []
        for info in self.iter('info'):
            data.append(info)

        return pd.DataFrame.from_records(data)

    def subset(self, numbers):
        return self.__class__(self.name, numbers)

    def drive(self, number):
        return Drive(self.name, number)


    def iter(self, attribite):
        for drive in self.drives:
            yield getattr(drive, attribite)
