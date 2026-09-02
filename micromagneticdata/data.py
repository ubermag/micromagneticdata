import glob
import json
import os
from pathlib import Path

import ipywidgets
import pandas as pd

import micromagneticdata as md


class Data:
    """Computational magnetism data class.

    It requires either the name of the system and optionally a directory `dirname` or
    alternatively a full path to the system directory to locate the system's data.

    Parameters
    ----------
    name : str

        System's name.

    dirname : str, optional

        Directory in which system's data is saved. Defults to ``'./'``.

    path : pathlib.Path

        Full path to where the data is stored. Defaults to `None`.

    Raises
    ------
    TypeError

        If the system's name or path cannot be found.

    Examples
    --------
    1. Creating data object using `path`

    >>> import micromagneticdata as mdata
    >>> from micromagneticdata import sample_data
    >>> data = mdata.Data(path=sample_data.dirname / "rectangle")

    2. Creating data object using `name` and `dirname`

    >>> data = mdata.Data(name='rectangle', dirname=sample_data.dirname)

    """

    def __init__(self, name=None, dirname="./", path=None):
        if path is not None:
            if name is not None:
                raise TypeError("'name' and 'path' cannot be used together.")
            self.path = path
        else:
            if name is None:
                raise TypeError("'name' must be provided if 'path' is not given.")
            self.path = Path(dirname) / name
        if not os.path.exists(self.path):
            msg = f"Directory {self.path} cannot be found."
            raise OSError(msg)

    @property
    def path(self):
        """Path to the simulation output."""
        return self._path

    @path.setter
    def path(self, path):
        if not isinstance(path, (str, Path)):
            raise TypeError(f"Unsupported {type(path)=}; expected str or pathlib.Path")
        self._path = Path(path).absolute()

    @property
    def name(self):
        """System/directory name containing simulation data of all drives."""
        return self.path.name

    @property
    def dirname(self):
        """Path to system directory, same as ``data.path.parent``."""
        return self.path.parent

    def __repr__(self):
        """Representation string.

        Returns
        -------
        str

            Representation string.

        Examples
        --------
        1. Representation string.

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data
        Data(path='...rectangle')

        """
        return f"Data(path='{self.path}')"

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data.info
           drive_number...
        """
        records = []
        for i in range(self.n):
            try:
                drive = self[i]
                with (drive.drive_path / "info.json").open() as f:
                    drive_info = json.load(f)
                drive_info["info.json"] = "available"
                records.append(drive_info)
            except RuntimeError as e:
                print(f"Warning: Missing adapter package: {e}")
                records.append({"drive_number": i, "info.json": "missing"})
            except FileNotFoundError:
                print(f"Warning: Missing info.json for drive-{i}")
                records.append({"drive_number": i, "info.json": "missing"})
            except json.JSONDecodeError:
                print(f"Warning: Corrupt info.json for drive-{i}")
                records.append({"drive_number": i, "info.json": "corrupt"})
        all_columns = set(col for record in records for col in record)
        for record in records:
            for col in all_columns:
                record.setdefault(col, pd.NA)

        return pd.DataFrame.from_records(records)

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data.n
        2

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data.n
        2
        >>> data[0]  # first drive
        OOMMFDrive(...)
        >>> data[-1]  # last drive
        OOMMFDrive(...)

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data.n
        2
        >>> len(list(data))
        2

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

        >>> import micromagneticdata as mdata
        >>> from micromagneticdata import sample_data
        >>> data = mdata.Data(path=sample_data.dirname / "rectangle")
        >>> data.selector()
        BoundedIntText(value=0, description='drive', max=1)

        """
        return ipywidgets.BoundedIntText(
            value=0, min=0, max=self.n - 1, step=1, description=description, **kwargs
        )
