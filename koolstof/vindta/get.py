import numpy as np, pandas as pd
from scipy.optimize import least_squares
from calkulate.density import seawater_1atm_MP81
from .read import read_dbs, read_logfile


def _get_logfile_index(dbs_row, logfile):
    """[row.apply] Get index in logfile corresponding to a given row of the dbs file."""
    if dbs_row.bottle in logfile.bottle.values:
        logfile_index = np.where(
            (dbs_row.bottle == logfile.bottle)
            & (dbs_row.analysis_datetime == logfile.analysis_datetime)
        )[0]
        if np.size(logfile_index) == 1:
            logfile_index = logfile.index[logfile_index[0]]
        else:
            print(
                (
                    "{} name/date matches found between dbs and logfile @ dbs loc {}"
                ).format(np.size(logfile_index), dbs_row.name)
            )
            logfile_index = np.nan
    else:
        logfile_index = np.nan
    return logfile_index


def get_logfile_index(dbs, logfile):
    """Find the index in the logfile corresponding to each row of the dbs file and add
    this in-place to the dbs as "logfile_index".

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame
        The logfile as a pandas DataFrame (imported with read_logfile).
    """
    dbs["logfile_index"] = dbs.apply(_get_logfile_index, args=[logfile], axis=1)


def _get_sample_blanks(dbs_row, logfile, use_from=6):
    """[row.apply] Calculate each sample's DIC blank value."""
    try:
        lft = logfile.loc[dbs_row.logfile_index].table
        use_minutes = lft["minutes"] >= use_from
        blank_here = lft["increments"][use_minutes].mean()
        blank_here_min = lft["increments"][use_minutes].min()
        blank_here_max = lft["increments"][use_minutes].max()
        blank_here_std = lft["increments"][use_minutes].std()
        blank_here_count = use_minutes.sum()
    except (ValueError, KeyError):
        blank_here = np.nan
        blank_here_min = np.nan
        blank_here_max = np.nan
        blank_here_std = np.nan
        blank_here_count = 0
    return pd.Series(
        {
            "blank_here": blank_here,
            "blank_here_min": blank_here_min,
            "blank_here_max": blank_here_max,
            "blank_here_std": blank_here_std,
            "blank_here_count": blank_here_count,
        }
    )


def get_sample_blanks(dbs, logfile, use_from=6):
    """Calculate each sample's DIC blank value and add this in-place to the dbs plus
    some relevant statistics.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame
        The logfile as a pandas DataFrame (imported with read_logfile).
    use_from : int, optional
        Which minute of the titration to begin counting as a blank measurement, by
        default 6.
    """
    if "logfile_index" not in dbs:
        get_logfile_index(dbs, logfile)
    dbs_blanks = dbs.apply(
        _get_sample_blanks, args=[logfile], axis=1, use_from=use_from
    )
    for blank in dbs_blanks.columns:
        dbs[blank] = dbs_blanks[blank]


def _centre_and_scale(x, x_factor=None, x_offset=None):
    if x_factor is None:
        x_factor = np.std(x)
    if x_offset is None:
        x_offset = np.mean(x)
    return (x - x_offset) / x_factor


def _de_centre_and_scale(x, x_factor, x_offset):
    return x * x_factor + x_offset


def _blank_progression(x0, datenum_scaled):
    """Estimate the changing coulometer blank during an analysis session."""
    blank = (
        x0[0]
        + x0[1] * datenum_scaled
        + x0[2] * np.exp(-(datenum_scaled - x0[3]) / x0[4])
    )
    blank = np.where(blank < 0, 0, blank)
    return blank


def _lsqfun_blank_progression(x0, datenum_scaled, blank_here):
    """Fit the changing coulometer blank during an analysis session."""
    return _blank_progression(x0, datenum_scaled) - blank_here


def _get_session_blanks(dbs_group):
    """[group.apply] Calculate blanks per analysis session."""
    x = dbs_group
    if x.blank_here.isnull().all():
        print(
            "No good blank_here values available for session '{}'".format(
                dbs_group.name
            )
        )
        blank_cols = pd.Series(
            data={
                "blank_mean": np.nan,
                "blank_median": np.nan,
                "analysis_datenum_mean": np.nan,
                "analysis_datenum_std": np.nan,
                "blank_progression": [np.nan] * 5,
                "blank_fit_std": np.nan,
                "blank_fit_rmse": np.nan,
            }
        )
    else:
        blank_here = x[x.blank_good].blank_here
        datenum_here = x[x.blank_good].analysis_datenum
        datenum_mean = datenum_here.mean()
        datenum_std = datenum_here.std()
        datenum_scaled = _centre_and_scale(
            datenum_here, x_factor=datenum_std, x_offset=datenum_mean
        )
        blank_prog = least_squares(
            _lsqfun_blank_progression,
            [30, 1, 0, 1, 1],
            args=[datenum_scaled, blank_here],
        )
        blank_cols = pd.Series(
            data={
                "blank_mean": blank_here.mean(),
                "blank_median": blank_here.median(),
                "analysis_datenum_mean": datenum_mean,
                "analysis_datenum_std": datenum_std,
                "blank_progression": blank_prog["x"],
                "blank_fit_std": np.std(blank_prog["fun"]),
                "blank_fit_rmse": np.sqrt(np.mean(blank_prog["fun"] ** 2)),
            }
        )
    return blank_cols


def get_session_blanks(dbs, logfile=None, session_col="dic_cell_id", use_from=6):
    """Calculate blanks per analysis session.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame, optional
        The logfile as a pandas DataFrame (imported with read_logfile), only necessary
        if you have not run get_sample_blanks on the dbs, by default None.
    session_col : str, optional
        The column name in the dbs that identifies analysis sessions, by default
        'dic_cell_id'.
    use_from : int, optional
        Which minute of the titration to begin counting as a blank measurement, by
        default 6.  Passed to get_sample_blanks if this has not already been run.

    Returns
    -------
    sessions : pd.DataFrame
        A table with blank fit data for each analysis session.
    """
    if "blank_here" not in dbs:
        assert (
            logfile is not None
        ), "You must either provide a logfile or run get_sample_blanks on the dbs."
        get_sample_blanks(dbs, logfile, use_from=use_from)
    if "blank_good" not in dbs:
        dbs["blank_good"] = ~dbs.blank_here.isnull()
    sessions = dbs.groupby(by=session_col).apply(_get_session_blanks)
    sessions.sort_values("analysis_datenum_mean", inplace=True)
    return sessions


def _get_counts_corrected(
    dbs,
    blank_col="blank",
    counts_col="counts",
    runtime_col="run_time",
):
    """Calculate the corrected counts."""
    return dbs[counts_col] - dbs[runtime_col] * dbs[blank_col]


def get_counts_corrected(
    dbs,
    logfile=None,
    sessions=None,
    blank_col="blank",
    counts_col="counts",
    runtime_col="run_time",
    session_col="dic_cell_id",
    use_from=6,
):
    """Determine and apply the blank corrections to get corrected counts, which are
    added to dbs in place as column 'counts_corrected'.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame, optional
        The logfile as a pandas DataFrame (imported with read_logfile), only necessary
        if you have not run get_sample_blanks on the dbs, by default None.
    sessions : pd.DataFrame, optional
        The table of analysis sessions generated by get_session_blanks, will be
        generated here if not provided, by default None.
    blank_col : str, optional
        The column name for blank values to use for corrections, by default 'blank'.
    counts_col : str, optional
        The column name for uncorrected counts, by default 'counts'.
    runtime_col : str, optional
        The column name for run time, by default 'run_time'.
    session_col : str, optional
        The column name in the dbs that identifies analysis sessions, by default
        'dic_cell_id'.
    use_from : int, optional
        Which minute of the titration to begin counting as a blank measurement, by
        default 6.  Passed to get_sample_blanks if this has not already been run.
    """
    if sessions is None:
        sessions = get_session_blanks(
            dbs, logfile=logfile, session_col=session_col, use_from=use_from
        )
    dbs["analysis_datenum_scaled"] = np.nan
    dbs["blank"] = np.nan
    for session, s in sessions.iterrows():
        l = dbs[sessions.index.name] == session
        dbs.loc[l, "analysis_datenum_scaled"] = _centre_and_scale(
            dbs.loc[l].analysis_datenum,
            x_factor=s.analysis_datenum_std,
            x_offset=s.analysis_datenum_mean,
        )
        dbs.loc[l, "blank"] = _blank_progression(
            s.blank_progression,
            dbs.loc[l].analysis_datenum_scaled,
        )
    dbs["counts_corrected"] = _get_counts_corrected(
        dbs, blank_col=blank_col, counts_col=counts_col, runtime_col=runtime_col
    )


def blank_correction(
    dbs,
    logfile,
    blank_col="blank",
    counts_col="counts",
    runtime_col="run_time",
    session_col="dic_cell_id",
    use_from=6,
):
    """Convenience wrapper for get_counts_corrected.  Returns the dbs with the blanks
    having been determined for each analysis session and counts thus corrected.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame
        The logfile as a pandas DataFrame (imported with read_logfile).
    blank_col : str, optional
        The column name for blank values to use for corrections, by default 'blank'.
    counts_col : str, optional
        The column name for uncorrected counts, by default 'counts'.
    runtime_col : str, optional
        The column name for run time, by default 'run_time'.
    session_col : str, optional
        The column name in the dbs that identifies analysis sessions, by default
        'dic_cell_id'.
    use_from : int, optional
        Which minute of the titration to begin counting as a blank measurement, by
        default 6.

    Returns
    -------
    sessions : pd.DataFrame
        A table of analysis sessions including blank correction details.
    """
    sessions = get_session_blanks(dbs, logfile=logfile, use_from=use_from)
    get_counts_corrected(dbs, sessions=sessions)
    return sessions


def get_density(dbs, temperature_analysis_dic=25.0, salinity=35.0):
    """Calculate sample densities in kg/l.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file.
    temperature_analysis_dic : float, optional
        Temperature of DIC analysis in degC, by default 25.0
    salinity : float, optional
        Practical salinity, by default 35.0

    Returns
    -------
    pd.DataFrame
        The dbs DataFrame with an extra column 'density_analysis_dic' containing the
        density during analysis in kg/l.
    """
    if "temperature_analysis_dic" not in dbs:
        dbs["temperature_analysis_dic"] = temperature_analysis_dic
        print(
            "dbs.temperature_analysis_dic not set; assuming {} °C.".format(
                temperature_analysis_dic
            )
        )
    if "salinity" not in dbs:
        dbs["salinity"] = salinity
        print("dbs.salinity not set; assuming {}.".format(salinity))
    dbs["density_analysis_dic"] = seawater_1atm_MP81(
        temperature=dbs.temperature_analysis_dic, salinity=dbs.salinity
    )
    return dbs


def get_standard_calibrations(dbs):
    """Calculate the calibration factor for each CRM separately and add this in-place
    to dbs as column 'k_dic_here'.

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs), having then passed
        throught blank_correction().
    sessions : pd.DataFrame
        A table of analysis sessions including blank correction details, produced by
        blank_correction().
    """
    assert "dic_certified" in dbs, "You must provide some dbs.dic_certified values."
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
        The dbs file as a pandas DataFrame (imported with read_dbs), having then passed
        throught blank_correction().
    sessions : pd.DataFrame
        A table of analysis sessions including blank correction details, produced by
        blank_correction().
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
