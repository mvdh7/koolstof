"""Make figures to assist calibrating and QCing VINDTA datasets."""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


def increments(dbs, logfile, use_from, ax=None, alpha=0.25, c="xkcd:navy", **kwargs):
    """Plot coulometer increments by the minute, focussing on the tails.
    Any additional kwargs are passed to plt.plot().
    """
    if ax is None:
        _, ax = plt.subplots()
    fymax = 1.0
    for i in dbs.logfile_index:
        i_data = logfile.table[i]
        i_blank = i_data["minutes"] >= use_from
        ax.plot(
            i_data["minutes"][i_blank],
            i_data["increments"][i_blank],
            c="xkcd:strawberry",
            alpha=alpha,
        )
        fymax = np.max([fymax, np.max(i_data["increments"][-3:])])
        not_i_blank = i_data["minutes"] <= use_from
        ax.plot(
            i_data["minutes"][not_i_blank],
            i_data["increments"][not_i_blank],
            c="xkcd:navy",
            alpha=alpha,
        )
    ax.set_xlim([0, dbs["run time"].max()])
    ax.set_ylim([0, fymax * 1.2])
    ax.set_xlabel("Run time / minutes")
    ax.set_ylabel("Increments / per minute")
    return ax


def blanks(dbs, ax=None, alpha=0.5, c="xkcd:navy", **kwargs):
    """Plot sample-by-sample blank values.
    Any additional `kwargs` are passed to `plt.scatter()`.
    """
    if ax is None:
        _, ax = plt.subplots()
    dbs[dbs.blank_good].plot.scatter(
        "analysis_datetime", "blank_here", ax=ax, c=c, alpha=alpha, **kwargs
    )
    ax.set_xlim(
        [
            dbs.analysis_datetime.min() - np.timedelta64(30, "m"),
            dbs.analysis_datetime.max() + np.timedelta64(30, "m"),
        ]
    )
    ax.xaxis.set_major_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    ax.set_title(session)
    ax.set_xlabel("Time of day")
    ax.set_ylim([0, np.max(dbs[dbs.blank_good].blank_here) * 1.05])
    ax.set_ylabel("Sample blank / per minute")
    return ax
