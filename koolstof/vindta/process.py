import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from . import io


def get_sample_blanks(dbs_row, logfile, use_from=6):
    lft = logfile.loc[dbs_row.logfile_index].table
    use_minutes = lft["minutes"] >= use_from
    blank_here = np.mean(lft["increments"][use_minutes])
    return blank_here


# def get_sample_blanks(dbs, logfile, use_from=6):
#     """Calculate sample-by-sample blank values."""
#     assert "logfile_index" in dbs, "You must first run logfile2dbs()."
#     assert use_from > 0, "`use_from` must be positive."

#     def sample_blanks(x, logfile, use_from):
#         lft = logfile.loc[x.logfile_index].table
#         L = lft["minutes"] >= use_from
#         blank = np.mean(lft["increments"][L])
#         return pd.Series({"blank_here": blank})

#     return io.add_func_cols(dbs, sample_blanks, logfile, use_from)


def centre_and_scale(x, x_factor=None, x_offset=None):
    if x_factor is None:
        x_factor = np.std(x)
    if x_offset is None:
        x_offset = np.mean(x)
    return (x - x_offset) / x_factor


def de_centre_and_scale(x, x_factor, x_offset):
    return x * x_factor + x_offset


def blank_progression(x0, datenum_scaled):
    """Estimate the changing coulometer blank during an analysis session."""
    return (
        x0[0]
        + x0[1] * datenum_scaled
        + x0[2] * np.exp(-(datenum_scaled - x0[3]) / x0[4])
    )


def fit_blank_progression(x0, datenum_scaled, blank_here):
    """Fit the changing coulometer blank during an analysis session."""
    return blank_progression(x0, datenum_scaled) - blank_here


def get_session_blanks(x):
    """Calculate blanks per analysis session."""
    blank_here = x[x.blank_good].blank_here
    datenum_here = x[x.blank_good].analysis_datenum
    datenum_mean = np.mean(datenum_here)
    datenum_std = np.std(datenum_here)
    datenum_scaled = centre_and_scale(
        datenum_here, x_factor=datenum_std, x_offset=datenum_mean
    )
    # blank_polyfit = np.polyfit(datenum_scaled, blank_here, 2)
    blank_prog = least_squares(
        fit_blank_progression, [0, 1, 1, 1, 1], args=[datenum_scaled, blank_here]
    )
    return pd.Series(
        data={
            "blank_mean": blank_here.mean(),
            "blank_median": blank_here.median(),
            "analysis_datenum_mean": datenum_mean,
            "analysis_datenum_std": datenum_std,
            # "blank_polyfit": blank_polyfit,
            "blank_progression": blank_prog["x"],
        }
    )


def blank_correction(
    dbs, blank_col="blank", counts_col="counts", runtime_col="run time"
):
    """Apply the blank correction to the coulometer counts."""
    return dbs[counts_col] - dbs[runtime_col] * dbs[blank_col]


def apply_session_blanks(dbs, dic_sessions):
    """Estimate sample blanks from session fits and apply the blank correction."""
    dbs["analysis_datenum_scaled"] = np.nan
    dbs["blank"] = np.nan
    for session in dic_sessions.index:
        S = dbs["cell ID"] == session
        dbs.loc[S, "analysis_datenum_scaled"] = centre_and_scale(
            dbs.loc[S].analysis_datenum,
            x_factor=dic_sessions.loc[session].analysis_datenum_std,
            x_offset=dic_sessions.loc[session].analysis_datenum_mean,
        )
        dbs.loc[S, "blank"] = blank_progression(
            dic_sessions.loc[session].blank_progression,
            dbs.loc[S].analysis_datenum_scaled,
        )
    dbs["counts_corrected"] = blank_correction(dbs)
    return dbs
