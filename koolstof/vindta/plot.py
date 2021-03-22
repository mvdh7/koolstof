"""Make figures to assist calibrating and QCing VINDTA datasets."""
import itertools, copy
import numpy as np
from matplotlib import pyplot as plt, dates as mdates
from . import get, process


markers = itertools.cycle(("o", "^", "s", "v", "D", "<", ">"))
colours = itertools.cycle(
    (
        "xkcd:purple",
        "xkcd:green",
        "xkcd:blue",
        "xkcd:pink",
        "xkcd:brown",
        "xkcd:red",
        "xkcd:teal",
        "xkcd:orange",
    )
)


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


def plot_session_blanks(
    dbs,
    session,
    ax=None,
    c="xkcd:navy",
    marker="o",
    figure_path=None,
    figure_format="png",
    show_fig=True,
):
    """Draw sample blanks and their fit for one analysis session."""
    # Prepare to draw the figure
    s = dbs.sessions.loc[session]
    l = dbs["dic_cell_id"] == session
    if ax is None:
        fig, ax = plt.subplots(dpi=300)
    # Create and draw fitted line
    fx = np.linspace(
        dbs[l].analysis_datenum_scaled.min(), dbs[l].analysis_datenum_scaled.max(), 500
    )
    fy = get.blank_progression(s.blank_progression, fx)
    fx = mdates.num2date(
        get.de_centre_and_scale(fx, s.analysis_datenum_std, s.analysis_datenum_mean)
    )
    ax.plot(fx, fy, c=c, label="Best fit")
    # Draw the rest of the figure
    dbs[l & dbs.blank_good].plot.scatter(
        "analysis_datetime",
        "blank_here",
        ax=ax,
        c=c,
        marker=marker,
        label="Samples used",
    )
    dbs[l & ~dbs.blank_good].plot.scatter(
        "analysis_datetime",
        "blank_here",
        ax=ax,
        c="none",
        edgecolor=c,
        marker=marker,
        label="Ignored",
    )
    y_max = np.max([dbs[l & dbs.blank_good].blank_here.max(), np.max(fy)]) * 1.05
    off_x = dbs[l & (dbs.blank_here > y_max)].analysis_datetime.values
    ax.scatter(
        off_x,
        np.full(np.size(off_x), y_max * 0.99999),
        c="none",
        edgecolor=c,
        marker="^",
        label="Off scale (ignored)",
        clip_on=False,
    )
    ax.set_ylim([0, y_max])
    ax.legend(edgecolor="k")
    ax.xaxis.set_major_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    ax.set_xlabel("Time of day of analysis")
    ax.set_ylabel(r"Coulometer blank / count$\cdot$minute$^{-1}$")
    ax.set_title(session)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    if figure_path is not None:
        plt.savefig("{}/{}.{}".format(figure_path, str(session), figure_format))
    if show_fig:
        plt.show()
    return fig, ax


def plot_blanks(dbs, **kwargs):
    """Draw sample blanks and their fit for all analysis sessions."""
    for session in dbs.sessions.index:
        fig, _ = plot_session_blanks(dbs, session, **kwargs)
        plt.close(fig)


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


def plot_k_dic(
    dbs,
    sessions=None,
    ax=None,
    batch_col="dic_cell_id",
    figure_path=None,
    figure_format="png",
):
    """Plot DIC calibration factors through time."""
    marker = copy.deepcopy(markers)
    colour = copy.deepcopy(colours)
    if ax is None:
        fig, ax = plt.subplots(dpi=300, figsize=(10, 6))
    if sessions is None:
        sessions = dbs.sessions
    else:
        sessions = dbs.sessions.loc[sessions]
    for session, s in sessions.iterrows():
        m = next(marker)
        c = next(colour)
        l = dbs[batch_col] == session
        l_good = l & dbs.k_dic_good
        if l_good.any():
            dbs[l_good].plot.scatter(
                "analysis_datetime",
                "k_dic_here",
                ax=ax,
                c=c,
                marker=m,
                alpha=0.7,
                label=session,
            )
        l_bad = l & ~dbs.k_dic_good & ~np.isnan(dbs.dic_certified)
        if l_bad.any():
            dbs[l_bad].plot.scatter(
                "analysis_datetime",
                "k_dic_here",
                ax=ax,
                c="none",
                edgecolor=c,
                marker=m,
            )
        sl = dbs[batch_col] == session
        sx = np.array(
            [
                dbs.loc[sl, "analysis_datetime"].min(),
                dbs.loc[sl, "analysis_datetime"].max(),
            ]
        )
        sy = np.full_like(sx, s.k_dic_mean)
        ax.plot(sx, sy, c=c)
    ax.legend(edgecolor="k", bbox_to_anchor=(1, 1))
    ax.set_xlabel("Analysis date and time")
    ax.set_ylabel(r"DIC calibration factor / μmol$\cdot$count$^{-1}$")
    # fac_mean = dbs.k_dic.mean()
    # fac_maxdiff = (dbs.k_dic - fac_mean).abs().max()
    # if fac_maxdiff > 0:
    #     ax.set_ylim(np.array([-1, 1]) * fac_maxdiff * 1.1 + fac_mean)
    # ax.set_xlim(
    #     [
    #         dbs.analysis_datetime.min() - np.timedelta64(30, "m"),
    #         dbs.analysis_datetime.max() + np.timedelta64(30, "m"),
    #     ]
    # )
    locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.get_offset_text().set_visible(False)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    if figure_path is not None:
        plt.savefig("{}/k_dic.{}".format(figure_path, figure_format))
    return fig, ax


def plot_dic_offset(
    dbs,
    sessions=None,
    ax=None,
    batch_col="dic_cell_id",
    figure_path=None,
    figure_format="png",
):
    """Plot measured minus certified DIC values through time."""
    marker = copy.deepcopy(markers)
    colour = copy.deepcopy(colours)
    if ax is None:
        fig, ax = plt.subplots(dpi=300, figsize=(10, 6))
    if sessions is None:
        sessions = dbs.sessions.index
    for session in sessions:
        m = next(marker)
        c = next(colour)
        l = dbs[batch_col] == session
        l_good = l & dbs.k_dic_good
        if l_good.any():
            dbs[l_good].plot.scatter(
                "analysis_datetime",
                "dic_offset",
                ax=ax,
                c=c,
                marker=m,
                alpha=0.7,
                label=session,
            )
        l_bad = l & ~dbs.k_dic_good & ~np.isnan(dbs.dic_offset)
        if l_bad.any():
            dbs[l_bad].plot.scatter(
                "analysis_datetime",
                "dic_offset",
                ax=ax,
                c="none",
                edgecolor=c,
                marker=m,
            )
    ax.legend(edgecolor="k", bbox_to_anchor=(1, 1))
    ax.set_xlabel("Analysis date and time")
    ax.set_ylabel(r"DIC (calibrated $-$ certified) / μmol$\cdot$kg$^{-1}$")
    ax.set_ylim(np.array([-1, 1]) * dbs[dbs.k_dic_good].dic_offset.abs().max() * 1.1)
    locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.get_offset_text().set_visible(False)
    ax.grid(alpha=0.2)
    ax.axhline(0, c="k", linewidth=0.8)
    plt.tight_layout()
    if figure_path is not None:
        plt.savefig("{}/dic_offset.{}".format(figure_path, figure_format))
    return fig, ax


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
