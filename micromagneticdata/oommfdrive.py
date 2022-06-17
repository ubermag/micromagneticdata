import glob
import os

import ubermagtable as ut
import ubermagutil as uu

import micromagneticdata as md


@uu.inherit_docs
class OOMMFDrive(md.Drive):
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

    @property
    def _step_files(self):
        return sorted(glob.iglob(os.path.join(self.drive_path, f"{self.name}*.omf")))

    @property
    def input_script(self):
        with open(os.path.join(self.drive_path, f"{self.name}.mif")) as f:
            return f.read()

    @property
    def table(self):
        return ut.Table.fromfile(
            os.path.join(self.drive_path, f"{self.name}.odt"), x=self.x
        )
