"""
koolstof
========

Import, blank-correct and calibrate DIC data.

Documentation is available online at https://koolstof.hseao3.group

Code examples assume that the import convention has been followed:

  >>> import koolstof as ks

The following subfunctions are then available:

Import data (from VINDTA)
-------------------------
    read_vindta_dbs
    read_vindta_logfile

Process and calibrate
---------------------
    get_counts_at
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

from .blank import blank_correction, get_counts_at
from .calibrate import calibrate_dic
from .meta import __version__, hello
from .plot import (
    plot_blanks,
    plot_dic_offset,
    plot_increments,
    plot_k_dic,
    plot_session_blanks,
)
from .process import poison_correction
from .read import read_vindta_dbs, read_vindta_logfile


__all__ = [
    "read_vindta_dbs",
    "read_vindta_logfile",
    "get_counts_at",
    "blank_correction",
    "calibrate_dic",
    "poison_correction",
    "plot_increments",
    "plot_blanks",
    "plot_session_blanks",
    "plot_dic_offset",
    "plot_k_dic",
    "hello",
    "__version__",
]
