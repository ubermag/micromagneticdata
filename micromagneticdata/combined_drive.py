import functools
import operator

import ubermagutil as uu

import micromagneticdata as md


@uu.inherit_docs
# @ts.typesystem(
#     name=ts.Typed(expected_type=str),
#     number=ts.Scalar(expected_type=int, unsigned=True),
#     dirname=ts.Typed(expected_type=str),
# )
class CombinedDrive(md.AbstractDrive):
    """Drive class.

    This class provides utility for the analysis of individual drives.

    Parameters
    ----------
    drives : List[Drive]

    Raises
    ------
    ValueError

        If the drives have different independent variables or less than two drives are
        passed.

    TypeError

        If the passed objects are not of type ``micromagneticdata.Drive``.

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

    def __init__(self, *drives):
        if len(drives) < 2:
            raise ValueError("At least two drives must be pased.")
        for drive in drives:
            if not isinstance(drive, md.Drive):
                raise TypeError(f"Object {drive}, {type(drive)=} is not of type Drive.")

        self._table = functools.reduce(
            operator.lshift, (drive.table for drive in drives)
        )
        self.drives = drives

        # self.name = name
        # self.number = number
        self.x = self.table.x

    @property
    def _m0_path(self):
        return self.drives[0]._m0_path

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
        drives = ",\n".join(f"  {drive!r}" for drive in self.drives)
        return f"{self.__class__.__name__}(\n{drives}\n)"

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
        return {
            "drive_numbers": [drive.info["drive_number"] for drive in self.drives],
            "driver": self.drives[0].info["driver"],
        }

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
        return self._table

    @property
    def _step_files(self):
        return sum((drive._step_files for drive in self.drives), start=[])

    def __lshift__(self, other):
        if isinstance(other, md.Drive):
            return self.__class__(*self.drives, other)
        elif isinstance(other, self.__class__):
            return self.__class__(*self.drives, *other.drives)
        raise TypeError(f"Invalid type {other=}.")
