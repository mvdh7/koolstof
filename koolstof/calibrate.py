import numpy as np
import pandas as pd

from .density import get_density


def get_standard_calibrations(dbs):
    """Calculate the calibration factor for each CRM separately and add this
    in-place to dbs as column "k_dic_here".

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs), having
        then passed through `blank_correction`.
    sessions : pd.DataFrame
        A table of analysis sessions including blank correction details,
        produced by `blank_correction`.
    """
    assert "dic_certified" in dbs, (
        "You must provide some dbs.dic_certified values."
    )
    if "density_analysis_dic" not in dbs:
        get_density(dbs)
    dbs["k_dic_here"] = (
        dbs.dic_certified * dbs.density_analysis_dic / dbs.counts_corrected
    )


def _get_session_calibrations(dbs_group):
    """[group.apply] Calculate the session-averaged calibration factors."""
    gk = dbs_group[dbs_group.k_dic_good].k_dic_here
    return pd.Series(
        {
            "k_dic_mean": gk.mean(),
            "k_dic_std": gk.std(),
            "k_dic_count": np.sum(~np.isnan(gk)),
        }
    )


def calibrate_dic(dbs, sessions):
    """Calculate the session-averaged calibration factors and calibrate all DIC
    measurements.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs), having
        then passed through `blank_correction`.
    sessions : pd.DataFrame
        A table of analysis sessions including blank correction details,
        produced by `blank_correction`.
    """
    if "k_dic_here" not in dbs:
        get_standard_calibrations(dbs)
    if "k_dic_good" not in dbs:
        dbs["k_dic_good"] = ~dbs.dic_certified.isnull()
    sc = dbs.groupby(by=sessions.index.name).apply(_get_session_calibrations)
    for k, v in sc.items():
        sessions[k] = v
    dbs["k_dic"] = sessions.loc[dbs[sessions.index.name]].k_dic_mean.values
    dbs["dic"] = dbs.counts_corrected * dbs.k_dic / dbs.density_analysis_dic
    dbs["dic_offset"] = dbs.dic - dbs.dic_certified
