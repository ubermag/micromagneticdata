import os
import glob
import json
import oommfodt
import discretisedfield as df


class Drive:

    def __init__(self, name, number):

        self.name = name
        self.dirname = os.path.join(name, 'drive-{}'.format(number))
        if not os.path.exists(self.dirname):
            raise IOError('Drive directory does not exist.')

    @property
    def mif(self):

        filename = '{}.mif'.format(self.name)
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
        else:
            raise IOError('File does not exist: {}'.format(filename))
        
        return data

    @property
    def m0(self):

        filename = 'm0.omf'
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            return df.read(path)
        else:
            raise IOError('File does not exist: {}'.format(filename))

    @property
    def dt(self):

        filename = '{}.odt'.format(self.name)
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
        else:
            raise IOError('File does not exist: {}'.format(filename))
        
        return oommfodt.oommfodt.read(path)
    
    @property
    def info(self):
        with open(os.path.join(self.dirname, 'info.json')) as f:
            return json.load(f)

    @property
    def step_number(self):
        return len(list(self.step_filenames))

    @property
    def step_filenames(self):
        for filename in sorted(glob.glob(os.path.join(self.dirname, '{}*.omf'.format(self.name)))):
            yield filename

    @property
    def step_fields(self):
        for filename in self.step_filenames:
            yield df.read(filename)
