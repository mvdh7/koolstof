"""Miscellaneous tools for marine carbonate chemistry and other such things."""

import string, textwrap
import numpy as np
from . import crm, infrared, molar, spectro, vindta

__all__ = ["crm", "infrared", "molar", "spectro", "vindta"]

__version__ = "0.0.4"


lcletter = dict(zip(range(1, 27), string.ascii_lowercase))


def sigfig(x, sf):
    """Return `x` to `sf` significant figures."""
    factor = 10.0 ** np.ceil(np.log10(np.abs(x)))
    return factor * np.around(x / factor, decimals=sf)


def say_hello():
    greeting = textwrap.dedent(
        r"""
        k  Miscellaneous tools for
        o  marine carbonate chemistry
        o  and other such things
        l  
        s  Matthew P. Humphreys
        t  https://mvdh.xyz
        o  
        f  Version {}
        """.format(
            __version__
        )
    )
    print(greeting)
