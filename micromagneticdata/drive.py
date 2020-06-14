import os
import glob
import json
import ubermagtable as ut
import discretisedfield as df
import ubermagutil.typesystem as ts


@ts.typesystem(name=ts.Name(const=True),
               number=ts.Scalar(expected_type=0, unsigned=True))
class Drive:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.dirname = os.path.join(name, f'drive-{number}')

        if not os.path.exists(self.dirname):
            msg = f'Drive directory {self.dirname} does not exist.'
            raise IOError(msg)

    @property
    def info(self):
        with open(os.path.join(self.dirname, 'info.json')) as f:
            return json.load(f)

    @property
    def mif(self):
        with open(os.path.join(self.dirname, f'{self.name}.mif')) as f:
            return f.read()

    @property
    def m0(self):
        return df.Field.fromfile(os.path.join(self.dirname, 'm0.omf'))

    @property
    def table(self):
        return ut.Table.fromfile(os.path.join(self.dirname,
                                              f'{self.name}.odt'))

    @property
    def step_filenames(self):
        filename = f'{self.name}*.omf'
        filenames = glob.iglob(os.path.join(self.dirname, filename))
        for filename in sorted(filenames):
            yield filename

    @property
    def step_number(self):
        return len(list(self.step_filenames))

    @property
    def step_fields(self):
        for filename in self.step_filenames:
            yield df.read(filename)
