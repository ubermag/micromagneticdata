import ubermagtable as ut
import ubermagutil as uu

import micromagneticdata as md


@uu.inherit_docs
class Mumax3Drive(md.Drive):
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
        super().__init__(name, number, dirname, x)

        self._mumax_output_path = self.drive_path / f"{name}.out"
        if not self._mumax_output_path.exists():
            msg = f"Output directory {self._mumax_output_path!r} does not exist."
            raise IOError(msg)

    @property
    def _step_files(self):
        return sorted(self._mumax_output_path.glob("*.ovf"))

    @property
    def input_script(self):
        with (self.drive_path / f"{self.name}.mx3").open() as f:
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
        return ut.Table.fromfile(str(self._mumax_output_path, "table.txt"), x=self.x)

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
            f"Mumax3Drive(name='{self.name}', number={self.number}, "
            f"dirname='{self.dirname}', x='{self.x}')"
        )
