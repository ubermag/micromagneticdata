import os
import glob
import ipywidgets
import pandas as pd
import ubermagtable as ut
from .drive import Drive
import ubermagutil.typesystem as ts


@ts.typesystem(name=ts.Typed(expected_type=str),
               dirname=ts.Typed(expected_type=str))
class Data:
    def __init__(self, name, dirname='./'):
        self.name = name
        self.dirname = dirname

        self.path = os.path.join(dirname, name)

        if not os.path.exists(self.path):
            msg = f'System directory {self.dirname} does not exist.'
            raise IOError(msg)

    @property
    def n(self):
        return len(list(glob.iglob(os.path.join(self.path, 'drive-*'))))

    def drive(self, n):
        return Drive(name=self.name, number=n, dirname=self.dirname)

    def __iter__(self):
        for i in range(self.n):
            yield self.drive(i)

    @property
    def info(self):
        mdata = []
        for i in self:
            info = i.info
            info['t'] = info['args'].get('t', float('NaN'))
            info['n'] = info['args'].get('n', float('NaN'))
            info.pop('args')
            mdata.append(info)

        return pd.DataFrame.from_records(mdata)

    def selector(self, description='drive', **kwargs):
        return ipywidgets.BoundedIntText(value=0,
                                         min=0,
                                         max=self.n,
                                         step=1,
                                         description=description,
                                         **kwargs)
