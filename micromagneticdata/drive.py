import abc
import copy
import json
import numbers
import pathlib

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

    use_cache : bool, optional

        If ``True`` the Drive object will read tabular data and the names and number of
        magnetisation files only once. Note: this prevents Drive to detect new data when
        looking at the output of a running simulation. If set to ``False`` the data is
        read every time the user accesses it. Defaults to ``False``.

    Raises
    ------
    IOError

        If the drive directory cannot be found.

    Examples
    --------
    1. Getting drive object from data object.

    >>> import os
    >>> import micromagneticdata as md
    ...
    >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
    ...                                'tests', 'test_sample')
    >>> drive = md.Data(name='system_name', dirname=dirname)[0]
    >>> drive
    OOMMFDrive(...)

    2. Getting drive objet directly.

    >>> drive = md.Drive(name='system_name', number=1, dirname=dirname)
    >>> drive
    Mumax3Drive(...)

    """

    def __new__(cls, name, number, dirname=".", x=None, use_cache=False, **kwargs):
        """Create a new OOMMFDrive or Mumax3Drive depending on the directory structure.

        If a subdirectory <name>.out exists a Mumax3Drive is created else an
        OOMMFDrive.

        """
        if pathlib.Path(f"{dirname}/{name}/drive-{number}/{name}.out").exists():
            return super().__new__(md.Mumax3Drive)
        else:
            return super().__new__(md.OOMMFDrive)

    def __init__(self, name, number, dirname="./", x=None, use_cache=False, **kwargs):
        # use kwargs to not expose the following additional internal arguments to users
        self._step_file_list = kwargs.pop("step_files", [])
        self._table = kwargs.pop("table", None)

        super().__init__(**kwargs)
        self.drive_path = pathlib.Path(f"{dirname}/{name}/drive-{number}")
        if not self.drive_path.exists():
            msg = f"Directory {self.drive_path!r} does not exist."
            raise IOError(msg)

        self.use_cache = use_cache
        self.name = name
        self.number = number
        self.dirname = dirname
        self.x = x

    @property
    def use_cache(self):
        """Use caching for scalar data and the list of magnetisation files.

        The existing cache is cleared when set to ``False``.

        Parameters
        ----------
        use_cache : bool

            If ``True`` the Drive object will read tabular data and the names and number
            of magnetisation files only once. Note: this prevents Drive to detect new
            data when looking at the output of a running simulation. If set to ``False``
            the data is read every time the user accesses it. Defaults to ``False``.

        """
        return self._use_cache

    @use_cache.setter
    def use_cache(self, use_cache):
        if not use_cache:
            self._step_file_list = []
            self._table = None
        self._use_cache = use_cache

    @property
    def _m0_path(self):
        return self.drive_path / "m0.omf"

    @property
    @abc.abstractmethod
    def _table_path(self):
        pass

    @property
    def table(self):
        if not self.use_cache:
            return ut.Table.fromfile(str(self._table_path), x=self.x)

        if self._table is None:
            self._table = ut.Table.fromfile(str(self._table_path), x=self.x)
        return self._table

    @property
    @abc.abstractmethod
    def _step_file_glob(self):
        pass

    @property
    def _step_files(self):
        if not self.use_cache:
            return sorted(self._step_file_glob)

        if not self._step_file_list:
            self._step_file_list = sorted(self._step_file_glob)
        return self._step_file_list

    def __getitem__(self, item):
        """Magnetisation field of an individual step or subpart of the drive.

        If an ``int`` is passed a single magnetisation field (discretisedfield.Field
        object) is returned. Additional callbacks (if registered) are applied to this
        field before it is returned.

        If a slice is passed a new drive object with the magnetisation steps defined via
        the slice is returned. Additional callbacks (if registered) are passed to the
        new drive object.

        Returns
        -------
        discretisedfield.Field

            Magnetisation field if an int is passed.

        micromagneticdata.Drive

            Drive with selected data if a slice is passed.

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

        2. Selecting a part of the drive.
        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=0, dirname=dirname)
        >>> selection = drive[:8:2]
        >>> selection
        OOMMFDrive(...)
        >>> selection.n
        4

        """
        if isinstance(item, numbers.Integral):
            return super().__getitem__(item)
        elif isinstance(item, slice):
            step_files = self._step_files[item]
            table = copy.copy(self.table)
            table.data = table.data.iloc[item].reset_index()
            return self.__class__(
                self.name,
                self.number,
                self.dirname,
                self.x,
                use_cache=True,
                callbacks=self.callbacks,
                step_files=step_files,
                table=table,
            )
        else:
            raise TypeError(f"{type(item)=} is not supported")

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

        Parameters
        ----------

        dirname : pathlib.Path

            Directory in which files are saved.

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
            df.Field.from_file(filename).to_file(vtkfilename)

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
        if isinstance(other, md.Drive):
            # no use of self.__class__ to allow combining Mumax3 and OOMMF runs
            return md.CombinedDrive(self, other)
        elif isinstance(other, md.CombinedDrive):
            return md.CombinedDrive(self, *other.drives)
        raise TypeError(f"Invalid type {other=}.")

    def register_callback(self, callback):
        if not callable(callback):
            raise TypeError("Argument is not callable.")
        return self.__class__(
            name=self.name,
            number=self.number,
            dirname=self.dirname,
            x=self.x,
            callbacks=self.callbacks + [callback],
            use_cache=self.use_cache,
            step_files=self._step_files,
            table=self.table,
        )
