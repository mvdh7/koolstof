import numpy as np
import pandas as pd
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


def get_session_blanks(x):
    """Calculate blanks per analysis session."""
    blank_here = x[x.blank_good].blank_here
    datenums_conditioned = x[x.blank_good].analysis_datenum
    datenum_mean = np.mean(datenums_conditioned)
    datenum_std = np.std(datenums_conditioned)
    datenums_conditioned = (datenums_conditioned - datenum_mean) / datenum_std
    blank_fit = np.polyfit(datenums_conditioned, blank_here, 2)
    return pd.Series(
        data={
            "blank_mean": blank_here.mean(),
            "blank_median": blank_here.median(),
            "analysis_datenum_mean": datenum_mean,
            "analysis_datenum_std": datenum_std,
            "blank_fit": blank_fit,
        }
    )
