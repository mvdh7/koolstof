"""Miscellaneous tools for marine carbonate chemistry and other delights."""

import string, textwrap
import numpy as np
from . import crm, molar, spectro, vindta

__all__ = ["crm", "molar", "spectro", "vindta"]

__version__ = "0.0.2"


lcletter = dict(zip(range(1, 27), string.ascii_lowercase))


def sigfig(x, sf):
    """Return `x` to `sf` significant figures."""
    factor = 10.0 ** np.ceil(np.log10(np.abs(x)))
    return factor * np.around(x / factor, decimals=sf)


def say_hello():
    greeting = textwrap.dedent(
        r"""
        ┌────────────────────────────┐

           ┬┌─┌─┐┌─┐┬  ┌─┐┌┬┐┌─┐┌─┐
           ├┴┐│ ││ ││  └─┐ │ │ │├┤ 
           ┴ ┴└─┘└─┘┴─┘└─┘ ┴ └─┘└  
        
          Miscellaneous tools for
          marine carbonate chemistry
          and other delights
        
          Matthew P. Humphreys
          https://mvdh.xyz
        
          Version {}


        └────────────────────────────┘
        """.format(
            __version__
        )
    )
    print(greeting)
