import glob
import json
import os

import discretisedfield as df
import ipywidgets
import ubermagtable as ut
import ubermagutil as uu
import ubermagutil.typesystem as ts

import micromagneticdata as md


@uu.inherit_docs
@ts.typesystem(
    name=ts.Typed(expected_type=str),
    number=ts.Scalar(expected_type=int, unsigned=True),
    dirname=ts.Typed(expected_type=str),
)
class Drive(md.AbstractDrive):
    """Drive class.

    This class provides utility for the analysis of individual drives.

    Parameters
    ----------
    name : str

        System's name.

    number : int

        Drive number.

    dirname : str, optional

        Directory in which system's data is saved. Defults to ``'./'``.

    x : str, optional

        Independent variable column name. Defaults to ``None`` and depending on
        the driver used, one is found automatically.

    Raises
    ------
    IOError

        If the drive directory cannot be found.

    Examples
    --------
    1. Getting drive object.

    >>> import os
    >>> import micromagneticdata as md
    ...
    >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
    ...                                'tests', 'test_sample')
    >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)

    """

    def __init__(self, name, number, dirname="./", x=None):
        self.name = name
        self.number = number
        self.dirname = dirname

        self.path = os.path.join(dirname, name, f"drive-{number}")
        if not os.path.exists(self.path):
            msg = f"Directory {self.path=} does not exist."
            raise IOError(msg)

        self.x = x

    @property
    def _m0_path(self):
        return os.path.join(self.path, "m0.omf")

    def __repr__(self):
        """Representation string.

        Returns
        -------
        str

            Representation string.

        Examples
        --------
        1. Representation string.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive
        Drive(...)

        """
        return (
            f"Drive(name='{self.name}', number={self.number}, "
            f"dirname='{self.dirname}', x='{self.x}')"
        )

    @property
    def info(self):
        """Drive information.

        This property returns a dictionary with information about the drive.

        Returns
        -------
        dict

            Drive information.

        Examples
        --------
        1. Getting information about drive.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=6, dirname=dirname)
        >>> drive.info
        {...}

        """
        with open(os.path.join(self.path, "info.json")) as f:
            return json.load(f)

    @property
    def mif(self):
        """MIF file.
        This property returns a string with the content of MIF file.

        Returns
        -------
        str
            MIF file content.

        Examples
        --------
        1. Getting MIF file.
        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=6, dirname=dirname)
        >>> drive.mif
        '# MIF 2...'
        """
        with open(os.path.join(self.path, f"{self.name}.mif")) as f:
            return f.read()

    @property
    def table(self):
        """Table object.

        This property returns an ``ubermagtable.Table`` object. As an
        independent variable ``x``, the column chosen via ``x`` property is
        selected.

        Returns
        -------
        ubermagtable.Table

            Table object.

        Examples
        --------
        1. Getting table object.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive.table
                       E...

        """
        return ut.Table.fromfile(os.path.join(self.path, f"{self.name}.odt"), x=self.x)

    @property
    def _step_files(self):
        return sorted(glob.iglob(os.path.join(self.path, f"{self.name}*.omf")))

    def ovf2vtk(self, dirname=None):
        """OVF to VTK conversion.

        This method iterates through all magnetisation fields in the drive and
        generates a VTK file for each of them.

        Examples
        --------
        1. Iterating drive.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive.ovf2vtk()

        """
        if dirname is None:
            dirname = self.path
        for i, filename in enumerate(self._step_files):
            vtkfilename = "drive-{}-{:07d}.vtk".format(self.number, i)
            df.Field.fromfile(filename).write(os.path.join(dirname, vtkfilename))

    def slider(self, description="step", **kwargs):
        """Widget for selecting individual steps.

        This method is based on ``ipywidgets.IntSlider``, so any keyword
        argument accepted by it can be passed.

        Parameters
        ----------
        description : str, optional

            Widget description. Defaults to ``'step'``.

        Returns
        -------
        ipywidgets.IntSlider

            Slider widget.

        Examples
        --------
        1. Slider widget.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive.slider()
        IntSlider(...)

        """
        return ipywidgets.IntSlider(
            value=0, min=0, max=self.n - 1, step=1, description=description, **kwargs
        )

    def __lshift__(self, other):
        if isinstance(other, self.__class__):
            return md.CombinedDrive(self, other)
        elif isinstance(other, md.CombinedDrive):
            return md.CombinedDrive(self, *other.drives)
        raise TypeError(f"Invalid type {other=}.")
