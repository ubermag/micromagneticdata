import json
from .util import drives_number

class Drive:

    def __init__(self, number, name):

        if isinstance(number, int):
            if number in drives_number(name):
                self.number = number
            else:
                raise IndexError('Drive with this number do not exist')
        else:
            raise TypeError('Accept only int')

        self.dirname = '{}/drive-{}'.format(name, number)

    @property
    def show_json(self):

        filename = 'info.json'
        with open('{}/{}'.format(self.dirname, filename)) as f:
            info = json.loads(f.read())

        return print(json.dumps(info, indent=4))
    