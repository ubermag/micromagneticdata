import os
import glob
import json
from .util import drives_number
import oommfodt

class Drive:

    def __init__(self, number, name):

        if isinstance(number, int):
            if number in drives_number(name):
                self.number = number
            else:
                raise IndexError('Drive with this number do not exist')
        else:
            raise TypeError('Accept only int')

        self.name = name
        self.dirname = '{}/drive-{}'.format(name, number)

    @property
    def info(self):
        with open(os.path.join(self.dirname, 'info.json')) as f:
            return json.load(f)

    @property
    def step_number(self):
        return len(list(self.step_filenames))

    @property
    def step_filenames(self):
        for filename in glob.glob(os.path.join(self.dirname, '{}*.omf'.format(self.name))):
            yield filename

    @property
    def step_fields(self):
        for filename in self.step_filenames:
            yield df.read(filename)
