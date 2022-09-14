import pathlib

import ubermagtable as ut
import ubermagutil as uu

import micromagneticdata as md

from .abstract_drive import AbstractDrive


@uu.inherit_docs
class Mumax3Drive(md.Drive):
    """Drive class for Mumax3Drives (created automatically).

    This class provides utility for the analysis of individual mumax3 drives. It should
    not be created explicitly. Instead, use ``micromagneticdata.Drive`` which
    automatically creates a ``drive`` object of the correct sub-type.

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
    >>> drive = md.Drive(name='system_name', number=1, dirname=dirname)
    >>> drive
    Mumax3Drive(...)

    """

    def __init__(self, name, number, dirname="./", x=None, **kwargs):
        self._mumax_output_path = pathlib.Path(
            f"{dirname}/{name}/drive-{number}/{name}.out"
        )  # required to initialise self.x in super
        if not self._mumax_output_path.exists():
            raise IOError(
                f"Output directory {self._mumax_output_path!r} does not exist."
            )

        super().__init__(name, number, dirname, x, **kwargs)

    @AbstractDrive.x.setter
    def x(self, value):
        if value is None:
            # self.info["driver"] in ["TimeDriver", "RelaxDriver", "MinDriver"]:
            self._x = "t"
        else:
            # self.table reads self.x so self._x has to be defined first
            self._x = value
            if value not in self.table.data.columns:
                raise ValueError(f"Column {value=} does not exist in data.")

    @property
    def _step_files(self):
        return sorted(map(str, self._mumax_output_path.glob("*.ovf")))

    @property
    def calculator_script(self):
        with (self.drive_path / f"{self.name}.mx3").open() as f:
            return f.read()

    @property
    def table(self):
        return ut.Table.fromfile(str(self._mumax_output_path / "table.txt"), x=self.x)

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
        >>> drive = md.Drive(name='system_name', number=1, dirname=dirname)
        >>> drive
        Mumax3Drive(name='system_name', number=1, dirname='.../test_sample', x='t')

        """
        return (
            f"Mumax3Drive(name='{self.name}', number={self.number}, "
            f"dirname='{self.dirname}', x='{self.x}')"
        )
