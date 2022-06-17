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

        self.mumax_path = os.path.join(self.path, f"{name}.out")
        if not os.path.exists(self.mumax_path):
            msg = f"Directory {self.mumax_path=} does not exist."
            raise IOError(msg)

    @property
    def mx3(self):
        """mx3 file. TODO
        This property returns a string with the content of mx3 file.

        Returns
        -------
        str
            MIF file content.

        Examples
        --------
        1. Getting mx3 file.
        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> drive = md.Drive(name='system_name', number=6, dirname=dirname)
        """
        with open(os.path.join(self.path, f"{self.name}.mx3")) as f:
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
        return ut.Table.fromfile(os.path.join(self.mumax_path, "table.txt"), x=self.x)

    @property
    def _step_files(self):
        return sorted(glob.iglob(os.path.join(self.mumax_path, "*.ovf")))
