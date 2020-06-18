"""Make figures to assist calibrating and QCing VINDTA datasets."""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from . import process


def increments(dbs, logfile, use_from, ax=None, alpha=0.25, **kwargs):
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


def blanks(dbs, dic_sessions, ax=None, title=None, alpha=0.5, **kwargs):
    """Plot sample-by-sample blank values.
    Additional kwargs are passed to plt.scatter.
    """
    if ax is None:
        _, ax = plt.subplots()
    if "blank_good" not in dbs:
        dbs["blank_good"] = True
    dbs[~dbs.blank_good].plot.scatter(
        "analysis_datetime",
        "blank_here",
        ax=ax,
        c="xkcd:strawberry",
        alpha=alpha,
        **kwargs
    )
    dbs[dbs.blank_good].plot.scatter(
        "analysis_datetime", "blank_here", ax=ax, c="xkcd:navy", alpha=alpha, **kwargs
    )
    sessions_here = dbs["cell ID"].unique()
    for session in sessions_here:
        sl = dbs["cell ID"] == session
        sx_sc = process.centre_and_scale(
            np.linspace(
                np.min(dbs[sl]["analysis_datenum"]),
                np.max(dbs[sl]["analysis_datenum"]),
                num=100,
            ),
            x_factor=dic_sessions.loc[session].analysis_datenum_std,
            x_offset=dic_sessions.loc[session].analysis_datenum_mean,
        )
        sx = mdates.num2date(
            process.de_centre_and_scale(
                sx_sc,
                dic_sessions.loc[session].analysis_datenum_std,
                dic_sessions.loc[session].analysis_datenum_mean,
            )
        )
        ax.plot(
            sx,
            process.blank_progression(
                dic_sessions.loc[session].blank_progression, sx_sc
            ),
            c="xkcd:navy",
        )
    ax.set_xlim(
        [
            dbs.analysis_datetime.min() - np.timedelta64(30, "m"),
            dbs.analysis_datetime.max() + np.timedelta64(30, "m"),
        ]
    )
    ax.xaxis.set_major_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    ax.set_title(title)
    ax.set_xlabel("Time of day")
    ax.set_ylim([0, np.max(dbs[dbs.blank_good].blank_here) * 1.05])
    ax.set_ylabel("Sample blank / count per minute")
    return ax


def dic_calibration_factors(dbs, dic_sessions, ax=None, save_as=None, **kwargs):
    """Plot changing DIC calibration factors through time."""
    if ax is None:
        _, ax = plt.subplots()
    if dbs.dic_calibration_good.any():
        dbs[dbs.dic_calibration_good].plot.scatter(
            "analysis_datetime",
            "dic_calibration_factor",
            ax=ax,
            c="xkcd:navy",
            alpha=0.5,
            **kwargs
        )
    if (~dbs.dic_calibration_good & dbs.crm).any():
        dbs[~dbs.dic_calibration_good].plot.scatter(
            "analysis_datetime",
            "dic_calibration_factor",
            ax=ax,
            c="xkcd:strawberry",
            alpha=0.5,
            **kwargs
        )
    for session in dic_sessions.index:
        if session in dbs["cell ID"].values:
            sl = dbs["cell ID"] == session
            sx = np.array(
                [
                    dbs.loc[sl, "analysis_datetime"].min(),
                    dbs.loc[sl, "analysis_datetime"].max(),
                ]
            )
            sy = np.full_like(sx, dic_sessions.loc[session].dic_calibration_mean)
            ax.plot(sx, sy, c="xkcd:strawberry", zorder=100, alpha=1)
    ax.set_ylabel("DIC calibration factor / μmol/count")
    fac_mean = dbs.dic_calibration_factor.mean()
    fac_maxdiff = (dbs.dic_calibration_factor - fac_mean).abs().max()
    if fac_maxdiff > 0:
        ax.set_ylim(np.array([-1, 1]) * fac_maxdiff * 1.1 + fac_mean)
    ax.set_xlim(
        [
            dbs.analysis_datetime.min() - np.timedelta64(30, "m"),
            dbs.analysis_datetime.max() + np.timedelta64(30, "m"),
        ]
    )
    ax.grid(alpha=0.4)
    return ax
