import numpy as np
from scipy.stats import norm
from matplotlib import pyplot as plt
from . import profiles
from .profiles import get_cluster_profile, cluster_profile
from ..meta import __version__


def add_credit(ax):
    """Add koolstof credit to figures."""
    ax.text(
        1.005,
        0,
        "koolstof v{}".format(__version__),
        alpha=0.3,
        c="k",
        fontsize=7,
        ha="left",
        va="bottom",
        rotation=-90,
        transform=ax.transAxes,
    )


def plot_duplicates(
    diffs, fmax=None, fstep=None, facecolor="xkcd:azure", linecolor="xkcd:blue"
):
    """Create a histogram of duplicate differences and calculate the corresponding
    1-sigma precision.

    Parameters
    ----------
    diffs : array-like
        The differences between the duplicate values.
    fmax : float, optional
        The maximum value to use for the histogram, by default None, in which case a
        sensible value is estimated.
    fstep : float, optional
        The step size for the histogram, by default None, in which case a sensible
        value is estimated.
    facecolor : str, optional
        The colour of the histogram bars, by default 'xkcd:azure'.
    linecolor : str, optional
        The colour of the distribution line, by default 'xkcd:blue'.

    Returns
    -------
    fig, ax : plt.figure, plt.axes
        The figure and axes created.
    """
    # Prepare variables
    diffs = np.abs(diffs[~np.isnan(diffs)])
    precision = np.mean(diffs) * np.sqrt(np.pi) / 2
    n_diffs = np.size(diffs)
    fmin = 0
    ffactor = 10 / 10 ** np.floor(np.log10(np.max(diffs)))
    if fmax is None:
        fmax = 1.2 * np.ceil(np.max(diffs) * ffactor) / ffactor
    if fstep is None:
        fstep = fmax / 10 ** np.floor(np.log10(n_diffs))
    # Draw figure
    fig, ax = plt.subplots(dpi=300)
    fx = np.linspace(fmin, fmax, num=500)
    fy = 2 * norm.pdf(fx / precision) * fstep * n_diffs / precision
    ax.hist(
        diffs,
        bins=np.arange(start=fmin, stop=fmax, step=fstep),
        facecolor=facecolor,
    )
    ax.plot(fx, fy, c=linecolor, lw=3)
    ax.set_xlabel("Absolute difference")
    ax.set_xlim((fmin, fmax))
    ax.set_ylabel("Frequency")
    ax.text(
        0.98,
        0.97,
        "1$\sigma$ = {:.2e}, $n$ = {}".format(precision, n_diffs),
        ha="right",
        va="top",
        transform=ax.transAxes,
    )
    add_credit(ax)
    fig.tight_layout()
    return fig, ax
