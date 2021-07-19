import numpy as np, pandas as pd
from scipy.optimize import least_squares
from calkulate import density


def _get_logfile_index(dbs_row, logfile):
    """[row.apply] Get index in logfile corresponding to a given row of the dbs file."""
    if dbs_row.bottle in logfile.bottle.values:
        logfile_index = np.where(
            (dbs_row.bottle == logfile.bottle)
            & (dbs_row.analysis_datetime == logfile.analysis_datetime)
        )[0]
        assert np.size(logfile_index) == 1, (
            "{} name/date matches found between dbs and logfile @ dbs loc {}"
        ).format(np.size(logfile_index), dbs_row.name)
        logfile_index = logfile.index[logfile_index[0]]
    else:
        logfile_index = np.nan
    return logfile_index


def get_logfile_index(dbs):
    """Get index in logfile corresponding to all rows of the dbs file."""
    assert dbs.logfile is not None, "You have not assigned a logfile for this dbs!"
    dbs["logfile_index"] = dbs.apply(_get_logfile_index, args=[dbs.logfile], axis=1)
    return dbs


def _get_sample_blanks(dbs_row, logfile, use_from=6):
    """[row.apply] Calculate each sample's DIC blank value."""
    lft = logfile.loc[dbs_row.logfile_index].table
    use_minutes = lft["minutes"] >= use_from
    blank_here = np.mean(lft["increments"][use_minutes])
    return blank_here


def get_sample_blanks(dbs, use_from=6):
    """Calculate each sample's DIC blank value."""
    if "logfile_index" not in dbs:
        dbs.get_logfile_index()
    dbs["blank_here"] = dbs.apply(
        _get_sample_blanks, args=[dbs.logfile], axis=1, use_from=use_from
    )
    return dbs


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
    blank = (
        x0[0]
        + x0[1] * datenum_scaled
        + x0[2] * np.exp(-(datenum_scaled - x0[3]) / x0[4])
    )
    blank = np.where(blank < 0, 0, blank)
    return blank


def fit_blank_progression(x0, datenum_scaled, blank_here):
    """Fit the changing coulometer blank during an analysis session."""
    return blank_progression(x0, datenum_scaled) - blank_here


def _get_session_blanks(dbs_group):
    """[group.apply] Calculate blanks per analysis session."""
    x = dbs_group
    blank_here = x[x.blank_good].blank_here
    datenum_here = x[x.blank_good].analysis_datenum
    datenum_mean = datenum_here.mean()
    datenum_std = datenum_here.std()
    datenum_scaled = centre_and_scale(
        datenum_here, x_factor=datenum_std, x_offset=datenum_mean
    )
    blank_prog = least_squares(
        fit_blank_progression, [0, 1, 1, 1, 1], args=[datenum_scaled, blank_here]
    )
    return pd.Series(
        data={
            "blank_mean": blank_here.mean(),
            "blank_median": blank_here.median(),
            "analysis_datenum_mean": datenum_mean,
            "analysis_datenum_std": datenum_std,
            "blank_progression": blank_prog["x"],
        }
    )


def get_session_blanks(dbs, batch_col="dic_cell_id", **kwargs):
    """Calculate blanks per analysis session."""
    if "blank_here" not in dbs:
        dbs.get_sample_blanks(**kwargs)
    if "blank_good" not in dbs:
        dbs["blank_good"] = True
    dbs.sessions = dbs.groupby(by=batch_col).apply(_get_session_blanks)
    return dbs


def blank_correction(
    dbs, blank_col="blank", counts_col="counts", runtime_col="run_time"
):
    """Apply the blank correction to the coulometer counts."""
    return dbs[counts_col] - dbs[runtime_col] * dbs[blank_col]


def get_blank_corrections(
    dbs, blank_col="blank", counts_col="counts", runtime_col="run_time", **kwargs
):
    """Determine and apply the blank correction."""
    if ~isinstance(dbs.sessions, pd.DataFrame):
        dbs.get_session_blanks(**kwargs)
    dbs["analysis_datenum_scaled"] = np.nan
    dbs["blank"] = np.nan
    for session, s in dbs.sessions.iterrows():
        l = dbs[dbs.sessions.index.name] == session
        dbs.loc[l, "analysis_datenum_scaled"] = centre_and_scale(
            dbs.loc[l].analysis_datenum,
            x_factor=s.analysis_datenum_std,
            x_offset=s.analysis_datenum_mean,
        )
        dbs.loc[l, "blank"] = blank_progression(
            s.blank_progression,
            dbs.loc[l].analysis_datenum_scaled,
        )
    dbs["counts_corrected"] = blank_correction(
        dbs, blank_col=blank_col, counts_col=counts_col, runtime_col=runtime_col
    )
    return dbs


def get_density(dbs):
    """Calculate sample densities in kg/l."""
    if "temperature_analysis_dic" not in dbs:
        dbs["temperature_analysis_dic"] = 25.0
        print("dbs.temperature_analysis_dic not set, so assuming 25 °C.")
    if "salinity" not in dbs:
        dbs["salinity"] = 35.0
        print("dbs.salinity not set, so assuming 35.")
    dbs["density_analysis_dic"] = density.seawater_1atm_MP81(
        temperature=dbs.temperature_analysis_dic, salinity=dbs.salinity
    )
    return dbs


def get_standard_calibrations(dbs, **kwargs):
    """Calculate the separate calibration factor for each CRM."""
    assert "dic_certified" in dbs, "You must provide some dbs.dic_certified values."
    if "counts_corrected" not in dbs:
        dbs.get_blank_corrections(**kwargs)
    if "density_analysis_dic" not in dbs:
        dbs.get_density()
    dbs["k_dic_here"] = (
        dbs.dic_certified * dbs.density_analysis_dic / dbs.counts_corrected
    )
    return dbs


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


def get_session_calibrations(dbs, batch_col="dic_cell_id", **kwargs):
    """Calculate the session-averaged calibration factors."""
    if "k_dic_here" not in dbs:
        dbs.get_standard_calibrations(batch_col=batch_col, **kwargs)
    if "k_dic_good" not in dbs:
        dbs["k_dic_good"] = ~np.isnan(dbs.dic_certified)
    sc = dbs.groupby(by=batch_col).apply(_get_session_calibrations)
    for k, v in sc.iteritems():
        dbs.sessions[k] = v
    dbs["k_dic"] = dbs.sessions.loc[dbs[batch_col]].k_dic_mean.values
    return dbs


def calibrate_dic(dbs, **kwargs):
    """Calibrate all DIC measurements."""
    if "k_dic" not in dbs:
        dbs.get_session_calibrations()
    dbs["dic"] = dbs["counts_corrected"] * dbs["k_dic"] / dbs["density_analysis_dic"]
    dbs["dic_offset"] = dbs.dic - dbs.dic_certified
    return dbs
