import os
import glob
import json
import oommfodt as oo
import discretisedfield as df


class Drive:
    """
    Examples
    --------
    Simple import.

    >>> from micromagneticdata import Drive

    """
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.dirname = os.path.join(name, f'drive-{number}')
        if not os.path.exists(self.dirname):
            raise IOError(f'Drive directory {self.dirname} does not exist.')

    @property
    def mif(self):
        miffilename = f'{self.name}.mif'
        with open(os.path.join(self.dirname, miffilename)) as f:
            return f.read()

    @property
    def m0(self):
        m0filename = 'm0.omf'
        return df.read(os.path.join(self.dirname, m0filename))

    @property
    def dt(self):
        odtfilename = f'{self.name}.odt'
        return oo.read(os.path.join(self.dirname, odtfilename))

    @property
    def info(self):
        infofilename = 'info.json'
        with open(os.path.join(self.dirname, infofilename)) as f:
            return json.load(f)

    def step_filenames(self, extension='omf'):
        filename = f'{self.name}*.{extension}'
        filenames = glob.iglob(os.path.join(self.dirname, filename))
        for filename in sorted(filenames):
            yield filename

    @property
    def step_number(self):
        return len(list(self.step_filenames))

    @property
    def step_fields(self):
        for filename in self.step_filenames():
            yield df.read(filename)
