import os
import glob
import json
import ipywidgets
import ubermagtable as ut
import discretisedfield as df
import ubermagutil.typesystem as ts


@ts.typesystem(name=ts.Typed(expected_type=str),
               number=ts.Scalar(expected_type=int, unsigned=True),
               dirname=ts.Typed(expected_type=str))
class Drive:
    def __init__(self, name, number, dirname='./'):
        self.name = name
        self.number = number
        self.dirname = dirname

        self.path = os.path.join(dirname, name, f'drive-{number}')

        if not os.path.exists(self.path):
            msg = f'Drive directory {self.path} does not exist.'
            raise IOError(msg)

    @property
    def info(self):
        with open(os.path.join(self.path, 'info.json')) as f:
            return json.load(f)

    @property
    def mif(self):
        with open(os.path.join(self.path, f'{self.name}.mif')) as f:
            return f.read()

    @property
    def m0(self):
        return df.Field.fromfile(os.path.join(self.path, 'm0.omf'))

    @property
    def table(self):
        return ut.Table.fromfile(os.path.join(self.path, f'{self.name}.odt'))

    @property
    def n(self):
        """Number of steps.

        Examples
        --------
        1. Getting the number of steps.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = os.path.join(os.path.dirname(__file__), 'tests')
        >>> name = 'test_sample'
        >>> drive = md.Drive(name, 0, dirname)
        >>> drive.n
        25

        """
        return len(list(self.step_filenames))

    @property
    def step_filenames(self):
        filenames = glob.iglob(os.path.join(self.path, f'{self.name}*.omf'))
        for filename in sorted(filenames):
            yield filename

    def step(self, n):
        return df.Field.fromfile(filename=list(self.step_filenames)[n])

    def __iter__(self):
        for filename in self.step_filenames:
            yield df.Field.fromfile(filename)

    def ovf2vtk(self):
        for i, filename in enumerate(self.step_filenames):
            vtkfilename = 'drive-{}-{:07d}.vtk'.format(self.number, i)
            df.Field.fromfile(filename).write(os.path.join(self.path,
                                                           vtkfilename))

    def slider(self, description='step', **kwargs):
        return ipywidgets.IntSlider(value=0,
                                    min=0,
                                    max=self.n-1,
                                    step=1,
                                    description=description,
                                    **kwargs)
