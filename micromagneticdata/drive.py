import abc
import json
import pathlib

import discretisedfield as df
import ipywidgets
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
    >>> drive
    OOMMFDrive(...)
    >>> drive = md.Drive(name='system_name', number=9, dirname=dirname)
    >>> drive
    Mumax3Drive(...)

    """

    def __new__(cls, name, number, dirname=".", x=None):
        """Create a new OOMMFDrive or Mumax3Drive depending on the directory structure.

        If a subdirectory <name>.out exists a Mumax3Drive is created else an
        OOMMFDrive.

        """
        if pathlib.Path(f"{dirname}/{name}/drive-{number}/{name}.out").exists():
            return super().__new__(md.Mumax3Drive)
        else:
            return super().__new__(md.OOMMFDrive)

    def __init__(self, name, number, dirname="./", x=None):
        self.drive_path = pathlib.Path(f"{dirname}/{name}/drive-{number}")
        if not self.drive_path.exists():
            msg = f"Directory {self.drive_path!r} does not exist."
            raise IOError(msg)

        self.name = name
        self.number = number
        self.dirname = dirname
        self.x = x

    @property
    def _m0_path(self):
        return self.drive_path / "m0.omf"

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
        with (self.drive_path / "info.json").open() as f:
            return json.load(f)

    @property
    @abc.abstractmethod
    def calculator_script(self):
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
        >>> drive.calculator_script
        '# MIF 2...'

        2. Getting mx3 file

        TODO add mumax3 output to the pre-computed data
        """

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
        dirname = pathlib.Path(dirname) if dirname is not None else self.drive_path
        for i, filename in enumerate(self._step_files):
            vtkfilename = dirname / f"drive-{self.number}-{i:07d}.vtk"
            df.Field.fromfile(filename).write(str(vtkfilename))

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
