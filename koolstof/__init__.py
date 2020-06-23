"""Miscellaneous tools for marine carbonate chemistry."""

import string
import numpy as np
from . import crm, molar, vindta

__all__ = ["crm", "molar", "vindta"]


lcletter = dict(zip(range(1, 27), string.ascii_lowercase))


def sigfig(x, sf):
    """Return `x` to `sf` significant figures."""
    factor = 10.0 ** np.ceil(np.log10(np.abs(x)))
    return factor * np.around(x / factor, decimals=sf)
