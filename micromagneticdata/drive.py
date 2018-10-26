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
    def show_json(self):

        filename = 'info.json'
        path = os.path.join(self.dirname, filename)
        with open(path) as f:
            data = json.loads(f.read())

        return print(json.dumps(data, indent=4))


    @property
    def show_mif(self):

        filename = '{}.mif'.format(self.name)
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
        else:
            raise IOError('File does not exist: {}'.format(filename))
        
        return print(data)


    @property
    def show_m0(self):

        filename = 'm0.omf'
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
        else:
            raise IOError('File does not exist: {}'.format(filename))
        
        return print(data)


    @property
    def show_odt(self):

        filename = '{}.odt'.format(self.name)
        path = os.path.join(self.dirname, filename)

        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
        else:
            raise IOError('File does not exist: {}'.format(filename))
        
        return oommfodt.oommfodt.read(path)
    
