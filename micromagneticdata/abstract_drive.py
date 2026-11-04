import abc
import functools
import inspect

import discretisedfield as df
import discretisedfield.plotting as dfp
import numpy as np
import xarray as xr
from discretisedfield.plotting.util import hv_key_dim


def _required_m_type(m_type, *, operation=None):
    """Supply a field-type validator to a method as ``_require_m``.

    The method validates each field where it is used. This avoids extra reads
    and allows checking either raw fields or callback results as appropriate.
    The injected parameter is omitted from the public method signature.
    """

    def decorate(method):
        operation_name = operation or method.__name__
        type_name = f"{m_type.__module__.split('.')[0]}.{m_type.__name__}"

        def require_m(m):
            if not isinstance(m, m_type):
                raise NotImplementedError(
                    f"{operation_name} requires a {type_name}, but received "
                    f"{type(m).__name__}."
                )
            return m

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            return method(self, *args, _require_m=require_m, **kwargs)

        signature = inspect.signature(method)
        wrapper.__signature__ = signature.replace(
            parameters=[
                parameter
                for name, parameter in signature.parameters.items()
                if name != "_require_m"
            ]
        )
        return wrapper

    return decorate


class AbstractDrive(abc.ABC):
    """Drive class.

    This class provides utility for the analysis of individual drives.

    Parameters
    ----------

    callbacks : list of callables, optional

        List of callback functions that are applied to individual fields of the drive
        when accessing them. Callbacks are applied in registration order and may
        change the returned type.

    """

    def __init__(self, callbacks=None):
        self._callbacks = callbacks or []

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> drive = mdata.Data(name='vortex', dirname=sample_data.dirname)[0]
        >>> drive.x
        'iteration'
        >>> drive.x = 'mx'

        """
        return self._x

    @x.setter
    @abc.abstractmethod
    def x(self, value):
        pass

    @property
    @abc.abstractmethod
    def info(self):
        """Drive information."""

    @property
    @abc.abstractmethod
    def m0(self):
        """Initial magnetisation field.

        Registered callbacks are not applied to the initial magnetisation.

        Returns
        -------
        discretisedfield.Field or pyvista.UnstructuredGrid

            Initial magnetisation field.

        Examples
        --------
        1. Getting initial magnetisation field.

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive.m0
        Field(...)

        """

    @property
    @abc.abstractmethod
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

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive.table  # doctest: +SKIP
        E...

        """

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

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive.n
        25

        """
        return len(self.table.data)

    @property
    @abc.abstractmethod
    def _step_files(self):
        """List of filenames of individual snapshots."""

    @abc.abstractmethod
    def __getitem__(self, item):
        """Magnetisation field of an individual step.

        Returns
        -------
        discretisedfield.Field or pyvista.UnstructuredGrid

            Magnetisation field if no callbacks are registered. Otherwise, the
            result of applying the callbacks, which may have a different type.

        Examples
        --------
        1. Getting the field of a particular step.

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive[5]
        Field(...)

        """

    def __iter__(self):
        """Iterator.

        This iterator yields all magnetisation fields in the drive, with
        registered callbacks applied.

        Yields
        ------
        discretisedfield.Field or pyvista.UnstructuredGrid

            Magnetisation field if no callbacks are registered. Otherwise, the
            result of applying the callbacks, which may have a different type.

        Examples
        --------
        1. Iterating drive.

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> list(drive)
        [...]

        """
        # self.n and self._step_files might have different length from restart
        # or if data is missing; therefore self._step_files is used
        for i in range(len(self._step_files)):
            yield self[i]

    @property
    def callbacks(self):
        """Return all registered callbacks."""
        return self._callbacks

    @abc.abstractmethod
    def register_callback(self, callback):
        """Register a callback applied before a step is returned.

        Callbacks are applied in registration order. The first callback receives
        the magnetisation field; each subsequent callback receives the result
        of the previous callback. Callbacks may change the returned type.
        """

    def _apply_callbacks(self, field):
        for callback in self._callbacks:
            field = callback(field)
        return field

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

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive_0 = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive_1 = md.Drive(name='rectangle', number=1, dirname=sample_data.dirname)
        >>> drive_0 << drive_1
        CombinedDrive...

        """

    @_required_m_type(df.Field)
    def to_xarray(self, *args, _require_m, **kwargs):
        """Export ``micromagneticdata.Drive`` as ``xarray.DataArray``

        The method depends on ``discretisedfield.Field.to_xarray`` and derives the last
        four dimensions ``x``, ``y``, ``z``, and ``comp`` in the output
        ``xarray.DataArray`` from it. The arguments and named arguments to this method
        are passed on to ``discretisedfield.Field.to_xarray``.

        Depending on type of driver, the dimensions and coordinates of the output may
        change. If the number of stored steps in the ``micromagneticdata.Drive`` are
        more than one, the output contains an extra dimension named after
        ``micromagneticdata.Drive.table.x`` with proper coordinate values. For the case
        of ``HysteresisDriver``, the new dimension has four coordinates, namely
        ``B_hysteresis``, ``Bx_hysteresis``, ``By_hysteresis``, and ``Bz_hysteresis``.
        The first represents the norm of the hysteresis field, while the rest three
        represents the components along the respective axes. For a
        ``micromagneticdata.Drive`` with a single ``discretisedfield.Field``, the value
        of the single ``discretisedfield.Field.to_xarray`` is returned.

        ``micromagneticdata.Drive.info`` is returned as the output ``xarray.DataArray``
        attributes, besides the ones derived from ``discretisedfield.Field.to_xarray``.

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

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> xr_drive = drive.to_xarray(name='Mag')
        >>> xr_drive
        <xarray.DataArray 'Mag' (t: 25, x: 20, y: 10, z: 4, vdims: 3)>...

        2. Magnetization in a cell over time for ``TimeDriver``

        >>> xr_drive.isel(x=2, y=2, z=2)
        <xarray.DataArray 'Mag' (t: 25, vdims: 3)>...

        """
        fields = iter(self)
        field_0 = _require_m(next(fields))
        if len(self._step_files) == 1:
            darray = field_0.to_xarray(*args, **kwargs)
        else:
            # xr.stack (below) is too slow and needs twice the amount of memory
            # field_darrays = (field.to_xarray(*args, **kwargs) for field in self)
            # darray = xr.concat(field_darrays, dim=self.table.data[self.table.x])
            array = np.empty(
                (self.n, *field_0.mesh.n, field_0.nvdim), dtype=field_0.array.dtype
            )
            array[0] = field_0.array
            for i, field in enumerate(fields, start=1):
                field = _require_m(field)
                array[i] = field.array
            # remove "comp" dimension for scalar fields
            if field_0.nvdim == 1:
                array = np.squeeze(array, axis=-1)

            field_darray = field_0.to_xarray(*args, **kwargs)
            coords = dict(field_darray.coords)
            coords[self.table.x] = self.table.data[self.table.x]

            darray = xr.DataArray(
                array, coords=coords, dims=[self.table.x, *field_darray.dims]
            )
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
            darray.name = field_darray.name
            darray.assign_attrs(**field_darray.attrs)

        return darray.assign_attrs(**self.info)

    @property
    def hv(self):
        """Plot interface, Holoviews/hvplot based.

        This property provides access to the different plotting methods. It is also
        callable to quickly generate plots. It is based on
        ``discretisedfield.plotting.Hv``. For more details and the available methods
        refer to the documentation linked below.

        .. seealso::

            :py:func:`~discretisedfield.plotting.Hv.__call__`
            :py:func:`~discretisedfield.plotting.Hv.scalar`
            :py:func:`~discretisedfield.plotting.Hv.vector`
            :py:func:`~discretisedfield.plotting.Hv.contour`

        Examples
        --------

        1. Visualising a drive using ``hv``.

        >>> import micromagneticdata as md
        >>> from micromagneticdata import sample_data
        >>> drive = md.Drive(name='rectangle', number=0, dirname=sample_data.dirname)
        >>> drive.hv(kdims=['x', 'y'])
        :DynamicMap...

        """
        return dfp.Hv(self._hv_key_dims, self._hv_data_selection, self._hv_vdims_guess)

    @_required_m_type(df.Field, operation="hv")
    def _hv_data_selection(self, *, _require_m, **kwargs):
        """Select one field for plotting in holoviews."""
        if self.x in self._hv_key_dims:
            if self.x not in kwargs:
                raise NotImplementedError(
                    f"The dimension {self.x} cannot be a key dimension"
                )
            value = kwargs.pop(self.x)
            n = self.table.data.loc[self.table.data[self.x] == value].index[0]
        else:
            n = -1
        field = _require_m(self[n])
        return field._hv_data_selection(**kwargs)

    @_required_m_type(df.Field, operation="hv")
    def _hv_vdims_guess(self, kdims, *, _require_m):
        """Try to find vector components matching the given kdims."""
        if self.x in kdims:
            return None
        field = _require_m(self[0])
        return field._hv_vdims_guess(kdims)

    @property
    @_required_m_type(df.Field, operation="hv")
    def _hv_key_dims(self, *, _require_m):
        """Key dimensions for holoviews.

        Key dimensions are the independent variable of the drive and all field key
        dimensions.

        """
        field = _require_m(self[0])
        key_dims = field._hv_key_dims
        if len(self.table.data) > 1:
            key_dims[self.x] = hv_key_dim(
                self.table.data[self.x].to_numpy(),
                self.table.units[self.x],
            )
        return key_dims
