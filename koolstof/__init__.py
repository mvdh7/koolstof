"""Miscellaneous tools for marine carbonate chemistry and other such things."""

import string, textwrap
import numpy as np
from . import (
    airica,
    crm,
    infrared,
    maps,
    meta,
    molar,
    optode,
    parameterisations,
    plot,
    quaatro,
    spectro,
    vindta,
)
from .vindta import (
    Dbs,
    read_dbs,
    read_logfile,
    get_logfile_index,
    get_sample_blanks,
    get_session_blanks,
    get_counts_corrected,
    get_density,
    get_standard_calibrations,
    get_session_calibrations,
    calibrate_dic,
    plot_session_blanks,
    plot_blanks,
    plot_k_dic,
    plot_dic_offset,
    concat,
    poison_correction,
)
from .optode import pH_optode
from .plot import get_cluster_profile, cluster_profile
from .parameterisations import aou_GG92, pH_tris_DD98
from .meta import __author__, __version__


lcletter = dict(zip(range(1, 27), string.ascii_lowercase))


def sigfig(x, sf):
    """Return `x` to `sf` significant figures."""
    factor = 10.0 ** np.ceil(np.log10(np.abs(x)))
    return factor * np.around(x / factor, decimals=sf)


def hello():
    greeting = textwrap.dedent(
        r"""
        k  Miscellaneous tools for
        o  marine carbonate chemistry
        o  and other such things
        l  
        s  Version {}
        t  doi:10.5281/zenodo.3999292
        o  
        f  https://seaco2.group
        """.format(
            __version__
        )
    )
    print(greeting)


# Alias for back-compat
say_hello = hello
