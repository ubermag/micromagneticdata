import abc

import discretisedfield as df
import xarray as xr


class AbstractDrive(abc.ABC):
    """Drive class.

    This class provides utility for the analysis of individual drives.

    """

    @abc.abstractmethod
    def __repr__(self):
        """Representation string."""
        pass  # pragma: no cover

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
    @abc.abstractmethod
    def info(self):
        """Drive information."""

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
        return df.Field.fromfile(self._m0_path)

    @property
    @abc.abstractmethod
    def _m0_path(self):
        """Path to m0 file."""

    @property
    @abc.abstractmethod
    def table(self):
        """Table object."""

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
        return len(self.table.data)

    @property
    @abc.abstractmethod
    def _step_files(self):
        """List of filenames of individual snapshots."""

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
        yield from map(df.Field.fromfile, self._step_files)

    @abc.abstractmethod
    def __lshift__(self, other):
        """Concatenate multiple drives of the same type.

        Multiple drives with the same independent variable (typically drives of the same
        type, e.g. TimeDriver) can be concatenated into one combined drive. The
        resulting object has one large table with scalar values and allows iterating
        over all magnetisation files of the individual drives.

        Parameters
        ----------
        other : micromagneticdata.Drive, micromagneticdata.CombinedDrive

            The drive to append to the current object.

        Returns
        -------
        micromagneticdata.CombinedDrive

            The concatenated drives.

        Examples
        --------
        1. Concatenating two drives

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive_0 = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> drive_1 = md.Drive(name='system_name', number=1, dirname=dirname)
        >>> drive_0 << drive_1
        CombinedDrive...

        """

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
        the rest three represents the components along the respective axes. For a
        ``micromagneticdata.Drive`` with a single ``discretisedfield.Field``, the value
        of the single ``discretisedfield.Field.to_xarray`` is returned.

        ``micromagneticdata.Drive.info`` is returned as the output ``xarray.DataArray``
        attributes, besides the ones derived from
        ``discretisedfield.Field.to_xarray``.

        Parameters
        ----------
        args: any

            Arguments to ``discretisedfield.Field.to_xarray``

        kwargs: any

            Named arguments to ``discretisedfield.Field.to_xarray``

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
