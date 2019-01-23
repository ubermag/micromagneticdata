import os
import re
import json
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
    def __init__(self, data, drives=None):
        if isinstance(data, mm.System):
            self.name = data.name
        elif isinstance(data, str):
            self.name = data
        else:
            raise TypeError("Accept only mm.System or string")

        if drives is None:
            self.drives = self._get_all_drives
        else:
            self.drives = drives

        self.metadata = self._get_metadata

    @property
    def _get_all_drives(self):
        return drives_number(self.name)

    @property
    def _get_metadata(self):
        info = []
        for drive in self.drives:
            file_name = '{}/drive-{}/info.json'.format(self.name, drive)
            with open(file_name) as f:
                item = json.loads(f.read())
                item['id'] = drive
                info.append(item)

        return pd.DataFrame.from_records(info)

    def get_drives(self, drives):
        return self.__class__(self.name, drives)

    def drive(self, number):
        return Drive(number, self.name)
