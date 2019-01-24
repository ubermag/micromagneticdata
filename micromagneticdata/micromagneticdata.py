import os
import re
import glob
import pandas as pd
from .drive import Drive


class MicromagneticData:
    """
    Examples
    --------
    Simple import.

    >>> from micromagneticdata import MicromagneticData

    """
    def __init__(self, name, numbers=None):
        self.name = name
        if numbers is None:
            self.numbers = self._all_numbers
        else:
            self.numbers = numbers

    @property
    def _all_numbers(self):
        dirs = glob.iglob(os.path.join(self.name, 'drive-*'))
        return sorted([int(re.findall(r'\d+', d)[0]) for d in dirs])

    def drive(self, number):
        return Drive(self.name, number)

    @property
    def drives(self):
        for number in self.numbers:
            yield self.drive(number)

    def iterate(self, attribute):
        for drive in self.drives:
            yield getattr(drive, attribute)

    @property
    def metadata(self):
        mdata = []
        for info in self.iterate('info'):
            mdata.append(info)
        return pd.DataFrame.from_records(data)

    def subset(self, numbers):
        return self.__class__(self.name, numbers)
