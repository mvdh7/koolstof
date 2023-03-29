"""
koolstof.vindta
===============

Import, process and calibrate the DIC data files produced by the Marianda VINDTA 3C.

Documentation is available online at https://koolstof.readthedocs.io/en/latest/vindta/

Code examples assume that the import convention has been followed:

  >>> import koolstof.vindta as ksv

The following subfunctions are then available.

Import data
-----------

    read_dbs
    read_logfile

Process and calibrate
---------------------

    blank_correction
    calibrate_dic
    poison_correction

Data visualisation
------------------

    plot_increments
    plot_blanks
    plot_session_blanks
    plot_dic_offset
    plot_k_dic
"""

from .read import read_dbs, read_logfile
from .get import blank_correction, calibrate_dic
from .plot import (
    plot_blanks,
    plot_dic_offset,
    plot_increments,
    plot_k_dic,
    plot_session_blanks,
)
from .process import poison_correction
from . import plot, process
