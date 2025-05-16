"""
koolstof
========

Import, blank-correct and calibrate DIC data.

Documentation is available online at https://koolstof.hseao3.group

Code examples assume that the import convention has been followed:

  >>> import koolstof as ks

The following subfunctions are then available:

Import data
-----------
    read_uic
    read_vindta
    read_vindta_dbs
    read_vindta_logfile

Process and calibrate
---------------------
    counts_at
    blank_per_measurement
    blank_per_session
    blank_correction
    session_blank
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

from .blank import (
    blank_correction,
    blank_per_measurement,
    blank_per_session,
    counts_at,
    session_blank,
)
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
from .read import read_uic, read_vindta, read_vindta_dbs, read_vindta_logfile


__all__ = [
    "read_uic",
    "read_vindta",
    "read_vindta_dbs",
    "read_vindta_logfile",
    "counts_at",
    "blank_per_measurement",
    "blank_per_session",
    "blank_correction",
    "session_blank",
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
