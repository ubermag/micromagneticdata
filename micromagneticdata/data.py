import glob
import os

import ipywidgets
import pandas as pd
import ubermagutil.typesystem as ts

import micromagneticdata as md


@ts.typesystem(name=ts.Typed(expected_type=str), dirname=ts.Typed(expected_type=str))
class Data:
    """Computational magnetism data class.

    It requires the name of the system to be passed. If `dirname` was used when
    the system was driven, it can be passed here via ``dirname``.

    Parameters
    ----------
    name : str

        System's name.

    dirname : str, optional

        Directory in which system's data is saved. Defults to ``'./'``.

    Raises
    ------
    IOError

        If the system's directory cannot be found.

    Examples
    --------
    1. Creating data object.

    >>> import os
    >>> import micromagneticdata as md
    ...
    >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
    ...                                'tests', 'test_sample')
    >>> data = md.Data(name='system_name', dirname=dirname)

    """

    def __init__(self, name, dirname="./"):
        self.name = name
        self.dirname = dirname
        self.path = os.path.join(dirname, name)

        if not os.path.exists(self.path):
            msg = f"Directory {self.path=} cannot be found."
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
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data
        Data(...)

        """
        return f"Data(name='{self.name}', dirname='{self.dirname}')"

    @property
    def info(self):
        """Data information.

        This property returns ``pandas.DataFrame`` with information about
        different drives found. If columns of different drives mismatch,
        ``NaN`` is added as the value.

        Returns
        -------
        pandas.DataFrame

            Data information.

        Examples
        --------
        1. Getting information about data.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data.info
           drive_number...
        """
        return pd.DataFrame.from_records([i.info for i in self])

    @property
    def n(self):
        """Number of drives in data.

        Returns
        -------
        int

            Number of drives.

        Examples
        --------
        1. Getting the number of drives.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data.n
        7

        """
        return len(list(glob.iglob(os.path.join(self.path, "drive-*"))))

    def __getitem__(self, item):
        """Get drive with number ``item``.

        If a negative value is passed as ``item``, the count starts from the end. For
        example, passing ``-1`` would return the last drive.

        Parameters
        ----------
        item : int

            Drive number.

        Returns
        -------
        micromagneticdata.Drive

            Drive object.

        Examples
        --------
        1. Getting drive.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data.n
        7
        >>> data[0]  # first (0th) drive
        Drive(...)
        >>> data[-1]  # last (6th) drive
        Drive(...)

        """
        return md.Drive(
            name=self.name,
            number=range(self.n)[item],
            dirname=self.dirname,
        )

    def __iter__(self):
        """Iterator.

        This method yields all drives found in data.

        Yields
        ------
        micromagneticdata.Drive

            Drive object.

        Examples
        --------
        1. Iterating data object.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data.n
        7
        >>> len(list(data))
        7

        """
        for i in range(self.n):
            yield self[i]

    def selector(self, description="drive", **kwargs):
        """Widget for selecting drive.

        This method is based on ``ipywidgets.BoundedIntText``, so any keyword
        argument accepted by it can be passed.

        Parameters
        ----------
        description : str, optional

            Widget description. Defaults to ``'drive'``.

        Returns
        -------
        ipywidgets.BoundedIntText

            Selection widget.

        Examples
        --------
        1. Selection widget.

        >>> import os
        >>> import micromagneticdata as md
        ...
        >>> dirname = dirname=os.path.join(os.path.dirname(__file__),
        ...                                'tests', 'test_sample')
        >>> data = md.Data(name='system_name', dirname=dirname)
        >>> data.selector()
        BoundedIntText(...)

        """
        return ipywidgets.BoundedIntText(
            value=0, min=0, max=self.n - 1, step=1, description=description, **kwargs
        )
