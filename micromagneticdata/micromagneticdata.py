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
    def __init__(self, data):
        if isinstance(data, mm.System):
            self.name = data.name
        elif isinstance(data, str):
            self.name = data
        else:
            raise TypeError("Accept only mm.System or string")

    @property
    def drives(self):

        name = self.name
        info = []
        for directory in sorted(os.listdir(name)):
            file_name = '{}/{}/info.json'.format(name,directory)
            with open(file_name) as f:
                item = json.loads(f.read())
                info.append(item)

        return pd.DataFrame.from_records(info)

    @property
    def drives_number(self):
        return drives_number(self.name)


    def drive(self, number):
        return Drive(number, self.name)
