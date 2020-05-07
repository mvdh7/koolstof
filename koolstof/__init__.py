"""Miscellaneous tools for marine carbonate chemistry."""
__all__ = ["vindta"]
from . import vindta


def sigfig(x, sf):
    """Return `x` to `sf` significant figures."""
    factor = 10.0 ** np.ceil(np.log10(np.abs(x)))
    return factor * np.around(x / factor, decimals=sf)
