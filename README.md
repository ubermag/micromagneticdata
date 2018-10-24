# micromagneticmodel
Marijan Beg<sup>1,2</sup>, Sergii Mamedov<sup>1</sup>, Ryan A. Pepper<sup>2</sup>, Thomas Kluyver<sup>1</sup>, and Hans Fangohr<sup>1,2</sup>

<sup>1</sup> *European XFEL GmbH, Holzkoppel 4, 22869 Schenefeld, Germany*  
<sup>2</sup> *Faculty of Engineering and the Environment, University of Southampton, Southampton SO17 1BJ, United Kingdom*  

| Description | Badge |
| --- | --- |
| Latest release | [![PyPI version](https://badge.fury.io/py/micromagneticdata.svg)](https://badge.fury.io/py/micromagneticdata) |
|                | [![Anaconda-Server Badge](https://anaconda.org/conda-forge/micromagneticdata/badges/version.svg)](https://anaconda.org/conda-forge/micromagneticdata) |
| Build | [![Build Status](https://travis-ci.org/joommf/micromagneticdata.svg?branch=master)](https://travis-ci.org/joommf/micromagneticdata) |
|       | [![Build status](https://ci.appveyor.com/api/projects/status/8umknqjg7cvlupsk?svg=true)](https://ci.appveyor.com/project/marijanbeg/micromagneticdata) |
| Coverage | [![codecov](https://codecov.io/gh/joommf/micromagneticdata/branch/master/graph/badge.svg)](https://codecov.io/gh/joommf/micromagneticdata) |
| Documentation | [![Documentation Status](https://readthedocs.org/projects/micromagneticdata/badge/?version=latest)](http://micromagneticdata.readthedocs.io/en/latest/?badge=latest) |
| Binder | [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/joommf/micromagneticdata/master?filepath=index.ipynb) |
| Dependecies | [![Requirements Status](https://requires.io/github/joommf/micromagneticdata/requirements.svg?branch=master)](https://requires.io/github/joommf/micromagneticdata/requirements/?branch=master) |
| License | [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) |

## About

`micromagneticdata` is a Python package that provides:

- The analysis of micromagnetic data

It is available on all major operating systems (Windows, MacOS, Linux) and requires Python 3.5 or higher.

## Installation

We recommend installing `micromagneticdata` by using either of the `pip` or `conda` package managers.

#### Python requirements

Before installing `micromagneticdata` via `pip`, please make sure you have Python 3.5 or higher on your system. You can check that by running

    python3 --version

If you are on Linux, it is likely that you already have Python installed. However, on MacOS and Windows, this is usually not the case. If you do not have Python 3.5 or higher on your machine, we strongly recommend installing the [Anaconda](https://www.anaconda.com/) Python distribution. [Download Anaconda](https://www.anaconda.com/download) for your operating system and follow instructions on the download page. Further information about installing Anaconda can be found [here](https://conda.io/docs/user-guide/install/download.html).

#### `pip`

After installing Anaconda on MacOS or Windows, `pip` will also be installed. However, on Linux, if you do not already have `pip`, you can install it with

    sudo apt install python3-pip

To install the `micromagneticdata` version currently in the Python Package Index repository [PyPI](https://pypi.org/project/micromagneticdata/) on all operating systems run:

    python3 -m pip install micromagneticdata

#### `conda`

`micromagneticdata` is installed using `conda` by running

    conda install --channel conda-forge micromagneticdata

For further information on the `conda` package, dependency, and environment management, please have a look at its [documentation](https://conda.io/docs/). 

## Updating

If you used pip to install `micromagneticdata`, you can update to the latest released version in [PyPI](https://pypi.org/project/micromagneticdata/) by running

    python3 -m pip install --upgrade micromagneticdata

On the other hand, if you used `conda` for installation, update `micromagneticdata` with

    conda upgrade micromagneticdata

#### Development version

The most recent development version of `micromagneticdata` that is not yet released can be installed/updated with

    git clone https://github.com/joommf/micromagneticdata.git
    python3 -m pip install --upgrade micromagneticdata

**Note**: If you do not have `git` on your system, it can be installed by following the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Binder

`micromagneticdata` can be used in the cloud via Binder. This does not require you to have anything installed and no files will be created on your machine. To use `micromagneticdata` in the cloud, follow this [link](https://mybinder.org/v2/gh/joommf/micromagneticdata/master?filepath=index.ipynb).

## Documentation

Documentation for `micromagneticdata` is available [here](http://micromagneticdata.readthedocs.io/en/latest/?badge=latest), where APIs and tutorials (in the form of Jupyter notebooks) are available.

## Support

If you require support on installation or usage of `micromagneticdata` or if you want to report a problem, you are welcome to raise an issue in our [joommf/help](https://github.com/joommf/help) repository.

## License

Licensed under the BSD 3-Clause "New" or "Revised" License. For details, please refer to the [LICENSE](LICENSE) file.

## How to cite

If you use `micromagneticdata` in your research, please cite it as:

1. M. Beg, R. A. Pepper, and H. Fangohr. User interfaces for computational science: A domain specific language for OOMMF embedded in Python. [AIP Advances, 7, 56025](http://aip.scitation.org/doi/10.1063/1.4977225) (2017).

2. DOI will be available soon

## Acknowledgements

`micromagneticdata` was developed as a part of [OpenDreamKit](http://opendreamkit.org/) – Horizon 2020 European Research Infrastructure project (676541).
