import os
import re
import glob
import pandas as pd
import ubermagtable as ut
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

    def subset(self, numbers):
        return self.__class__(self.name, numbers)

    @property
    def metadata(self):
        mdata = []
        for info in self.iterate('info'):
            info['drive_time'] = info['args'].get('t', float('NaN'))
            info['step_number'] = info['args'].get('n', float('NaN'))
            info.pop('args')
            mdata.append(info)
        return pd.DataFrame.from_records(mdata)

    @property
    def dt(self):
        dfs = []
        for df in self.iterate('dt'):
            dfs.append(df)

        return oo.merge(dfs, timedriver=True)
