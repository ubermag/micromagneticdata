import glob
import json
import os

import discretisedfield as df
import ipywidgets
import ubermagtable as ut
import ubermagutil.typesystem as ts
import xarray as xr


@ts.typesystem(
    name=ts.Typed(expected_type=str),
    number=ts.Scalar(expected_type=int, unsigned=True),
    dirname=ts.Typed(expected_type=str),
)
class Drive:
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
        self.x = x

        if not os.path.exists(self.path):
            msg = f"Directory {self.path=} does not exist."
            raise IOError(msg)

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
    def x(self):
        """Independent variable name.

        Parameters
        ----------
        value : str

            Independent variable name.

        Returns
        -------
        str

            Representation string.

        Raises
        ------
        ValueError

            If the column name does not exist in table.

        Examples
        --------
        1. Getting and setting independent variable name.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=6, dirname=dirname)
        >>> drive.x
        'B_hysteresis'
        >>> drive.x = 'Bx_hysteresis'

        """
        return self._x

    @x.setter
    def x(self, value):
        if value is None:
            if self.info["driver"] == "TimeDriver":
                self._x = "t"
            elif self.info["driver"] == "MinDriver":
                self._x = "iteration"
            elif self.info["driver"] == "HysteresisDriver":
                self._x = "B_hysteresis"
        else:
            if value in self.table.data.columns:
                self._x = value
            else:
                msg = f"Column {value=} does not exist in data."
                raise ValueError(msg)

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
    def m0(self):
        """Inital magnetisation.

        This property returns a ``discretisedfield.Field`` object for the
        initial magnetisation field.

        Returns
        -------
        discretisedfield.Field

            Initial magnetisation field.

        Examples
        --------
        1. Getting initial magnetisation field.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive.m0
        Field(...)

        """
        return df.Field.fromfile(os.path.join(self.path, "m0.omf"))

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
    def n(self):
        """Number of steps.

        This property returns the number of rows in the drive table.

        Returns
        -------
        int

            Number of steps.

        Examples
        --------
        1. Getting the number of steps.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive.n
        25

        """
        return len(self.table.data.index)

    @property
    def _step_files(self):
        return sorted(glob.iglob(os.path.join(self.path, f"{self.name}*.omf")))

    def __getitem__(self, item):
        """Magnetisation field of an individual step.

        Returns
        -------
        int

            Step number.

        Examples
        --------
        1. Getting the field of a particular step.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive[5]
        Field(...)

        """
        return df.Field.fromfile(filename=self._step_files[item])

    def __iter__(self):
        """Iterator.

        This iterator iterates through all magnetisation field in drive and
        yields ``discretisedfield.Field`` objects.

        Returns
        -------
        discretisedfield.Field

            Magnetisation field.

        Examples
        --------
        1. Iterating drive.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> list(drive)
        [...]

        """
        for filename in self._step_files:
            yield df.Field.fromfile(filename)

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

    def to_xarray(self, *args, **kwargs):
        """Export ``micromagneticdata.Drive`` as ``xarray.DataArray``

        The method depends on ``discretisedfield.Field.to_xarray`` and derives the
        last four dimensions ``x``, ``y``, ``z``, and ``comp`` in the output
        ``xarray.DataArray`` from it. The arguments and named arguments to this method
        are passed on to ``discretisedfield.Field.to_xarray``.

        Depending on type of driver, the dimensions and coordinates of the output may
        change. If the number of stored steps in the ``micromagneticdata.Drive`` are
        more than one, the output contains an extra dimension named after
        ``micromagneticdata.Drive.table.x`` with proper coordinate values. For the case
        of ``HysteresisDriver``,  the new dimension has four coordinates, namely
        ``B_hysteresis``, ``Bx_hysteresis``, ``By_hysteresis``, and
        ``Bz_hysteresis``. The first represents the norm of the hysteresis field, while
        the rest three represents the components along the respective axes. For
        ``MinDriver`` with a single ``discretisedfield.Field``, the value of the single
        ``discretisedfield.Field.to_xarray`` is returned.

        ``micromagneticdata.Drive.info`` is returned as the output ``xarray.DataArray``
        attributes, besides the ones derived from
        ``discretisedfield.Field.to_xarray``.

        Parameters
        ----------
        args: any

            arguments to ``discretisedfield.Field.to_xarray``

        kwargs: any

            named arguments to ``discretisedfield.Field.to_xarray``

        Returns
        -------
        xarray.DataArray

            ``micromagneticdata.Drive`` as ``xarray.DataArray``

        Examples
        --------
        1. Drive to DataArray

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> xr_drive = drive.to_xarray(name='Mag')
        >>> xr_drive
        <xarray.DataArray 'Mag' (t: 25, x: 20, y: 10, z: 4, comp: 3)>
        ...

        2. Magnetization in a cell over time for ``TimeDriver``

        >>> xr_drive.isel(x=2, y=2, z=2)
        <xarray.DataArray 'Mag' (t: 25, comp: 3)>
        ...

        """
        if len(self._step_files) == 1:
            darray = self[0].to_xarray(*args, **kwargs)
        else:
            field_darrays = (field.to_xarray(*args, **kwargs) for field in self)
            darray = xr.concat(field_darrays, dim=self.table.data[self.table.x])
            darray[self.table.x].attrs["units"] = self.table.units[self.table.x]
            if self.info["driver"] == "HysteresisDriver":
                for i in "xyz":
                    darray = darray.assign_coords(
                        {
                            f"B{i}_hysteresis": (
                                "B_hysteresis",
                                self.table.data[f"B{i}_hysteresis"],
                            )
                        }
                    )
                    darray[f"B{i}_hysteresis"].attrs["units"] = self.table.units[
                        f"B{i}_hysteresis"
                    ]

        return darray.assign_attrs(**self.info)
