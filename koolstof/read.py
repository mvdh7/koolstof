import re
import warnings

import numpy as np
import pandas as pd
from matplotlib import dates as mdates

from .vindta import get_logfile_index


def read_vindta_logfile(
    fname,
    methods="3C standard",
    ignore_lines=None,
):
    """Import a logfile.bak as a DataFrame.

    Parameters
    ----------
    fname : str
        The filename (and path) of the logfile.
    methods : str or list, optional
        VINDTA method name or list of names used for measurements, by default
        "3C standard".
    ignore_lines : list, optional
        Which line numbers of the logfile to ignore, by default None.

    Returns
    -------
    pd.DataFrame
        The logfile as a pandas DataFrame.
    """
    if isinstance(methods, str):
        methods = [methods]
    if ignore_lines is None:
        ignore_lines = []
    # Compile regexs for reading logfile
    re_method = re.compile(r"(" + r"|".join(methods) + r")\.mth run started ")
    re_datetime = re.compile(
        r"started (\d{2})/(\d{2})/(\d{2})  (\d{2}):(\d{2})"
    )
    re_bottle = re.compile(r"(bottle)?\t([^\t]*)\t")
    re_crm = re.compile(r"CRM\t([^\t]*)\t")
    re_increments = re.compile(r"(\d*)\t(\d*)\t(\d*)\t")
    # Import text from logfile
    with open(fname, "r") as f:
        logf = f.read().splitlines()
    # Initialise arrays
    logdf = {
        "line_number": [],
        "datetime_analysis": np.array([], dtype="datetime64"),
        "bottle": [],
        "table": [],
        "counts": [],
        "run_time": [],
        "method": [],
    }
    # Parse file line by line
    for i, line in enumerate(logf):
        if re_method.match(line):
            # Get sample name
            lbot = 0
            if re_bottle.match(logf[i + 1]):
                lbot = re_bottle.findall(logf[i + 1])[0][1]
            elif re_crm.match(logf[i + 1]):
                lbot = re_crm.findall(logf[i + 1])[0]
            elif logf[i + 1] == "other":
                lbot = "other_{}".format(i + 1)
            if isinstance(lbot, str):
                logdf["bottle"].append(lbot)
                logdf["line_number"].append(i)
                logdf["method"].append(re_method.findall(line)[0])
                # Get analysis date and time
                ldt = re_datetime.findall(line)[0]
                ldt = np.datetime64(
                    "{}-{}-{}T{}:{}".format(
                        "20" + ldt[2], ldt[0], ldt[1], ldt[3], ldt[4]
                    )
                )
                logdf["datetime_analysis"] = np.append(
                    logdf["datetime_analysis"], ldt
                )
                # Get coulometer data
                jdict = {
                    "time": [0.0],
                    "counts": [0.0],
                    "increments": [0.0],
                }
                j = 4
                while re_increments.match(logf[i + j].strip()):
                    jinc = re_increments.findall(logf[i + j].strip())[0]
                    jdict["time"].append(float(jinc[0]))
                    jdict["counts"].append(float(jinc[1]))
                    jdict["increments"].append(float(jinc[2]))
                    j += 1
                jdict = {k: np.array(v) for k, v in jdict.items()}
                logdf["table"].append(jdict)
                logdf["counts"].append(jdict["counts"][-1])
                logdf["run_time"].append(j - 4.0)
            else:
                if i + 1 not in ignore_lines:
                    warnings.warn(
                        "Logfile line {}: bottle name not found!".format(i + 1)
                    )
    # Convert lists to arrays and put logfile into DataFrame
    logdf = pd.DataFrame({k: np.array(v) for k, v in logdf.items()})
    logdf.set_index("line_number", inplace=True)
    return logdf


# More Python-friendly names for the .dbs columns
_dbs_mapper = {
    "run type": "run_type",
    "i.s. temperature": "temperature_insitu",
    "run time": "run_time",
    "CT": "dic_raw",
    "factor CT": "factor_dic",
    "blank": "blank_setting",
    "TCT": "total_carbon_titrated",
    "last CRM CT": "last_crm_dic",
    "cert. CRM CT": "dic_cert",
    "last CRM AT": "last_crm_alkalinity",
    "cert. CRM AT": "alkalinity_cert",
    "batch": "batch_setting",
    "AT": "alkalinity_raw",
    "factor AT": "factor_alkalinity",
    "rms": "rms_alkalinity",
    "calc ID": "calc_id",
    "Titrino": "titrino",
    "sample line": "sample_line",
    "pip vol": "pip_vol",
    "Lat.": "latitude",
    "Long.": "longitude",
    "cell ID": "dic_cell_id",
}


# List of columns to drop from the .dbs by default
_dbs_drop = [
    "run_type",
    "temperature_insitu",
    "salinity",
    "dic_raw",
    "factor_dic",
    "blank_setting",
    "total_carbon_titrated",
    "last_crm_dic",
    "dic_cert",
    "last_crm_alkalinity",
    "alkalinity_cert",
    "batch_setting",
    "alkalinity_raw",
    "factor_alkalinity",
    "rms_alkalinity",
    "calc_id",
    "titrino",
    "sample_line",
    "pip_vol",
    "comment",
    "latitude",
    "longitude",
    "date",
    "time",
]


def _dbs_datetime(dbs_row):
    """[row.apply] Convert date and time from dbs file into a datetime."""
    try:
        dspl = dbs_row["date"].split("/")
        datetime_analysis = np.datetime64(
            "-".join(("20" + dspl[2], dspl[0], dspl[1]))
            + "T"
            + dbs_row["time"]
        )
    except AttributeError:
        datetime_analysis = np.datetime64("NaT")
    return pd.Series(
        {
            "datetime_analysis": datetime_analysis,
        }
    )


def read_vindta_dbs(fname, drop_cols=True):
    """Import a dbs file from a VINDTA, rename the columns, and reformat the
    date/time.

    Parameters
    ----------
    fname : str
        The filename (and path) of the dbs file.
    drop_cols : bool, optional
        Whether to drop superfluous columns (True) or not (False), by default
        True.

    Returns
    -------
    pd.DataFrame
        The dbs file as a pandas DataFrame.
    """
    # Import the dbs file and rename columns
    headers = np.genfromtxt(fname, delimiter="\t", dtype=str, max_rows=1)
    dbs = pd.read_table(fname, header=0, names=headers, usecols=headers)
    dbs = dbs.rename(columns=_dbs_mapper)
    dbs["dbs_fname"] = fname
    # Reformat the date and time
    dbs = dbs.assign(**dbs.apply(_dbs_datetime, axis=1))
    dbs["datenum_analysis"] = mdates.date2num(dbs.datetime_analysis)
    # Drop superfluous columns, if requested (by default, do this)
    if drop_cols:
        dbs.drop(columns=_dbs_drop, inplace=True)
    return dbs


def read_vindta(
    fname_dbs,
    fname_logfile,
    blank_from=6,
    drop_cols=True,
    methods="3C standard",
    ignore_lines=None,
):
    """Import a VINDTA dbs file and logfile.bak as pandas `DataFrame`s.

    Parameters
    ----------
    fname_dbs : str
        The filename (and path) of the dbs file.
    fname_logfile : str
        The filename (and path) of the logfile.
    blank_from : float, optional
        Which minute of each titration to start counting as the blank, by
        default `6`.
    drop_cols : bool, optional
        Whether to drop superfluous columns from `dbs`, by default `True`.
    methods : str or list, optional
        VINDTA method name or list of names used for measurements, by default
        `"3C standard"`.
    ignore_lines : list, optional
        Which line numbers of the logfile to ignore, by default `None`.

    Returns
    -------
    dbs : pd.DataFrame
        The dbs file as a pandas `DataFrame`.
    logfile : pd.DataFrame
        The logfile as a pandas `DataFrame`.
    """
    dbs = read_vindta_dbs(fname_dbs, drop_cols=drop_cols)
    dbs["blank_from"] = blank_from
    logfile = read_vindta_logfile(
        fname_logfile,
        methods=methods,
        ignore_lines=ignore_lines,
    )
    get_logfile_index(dbs, logfile)
    return dbs, logfile


def read_uic(fname, blank_from=10, to_datetime_kwargs=None):
    dbs = pd.read_csv(fname).rename(columns={"Time": "run_time"})
    if to_datetime_kwargs is None:
        to_datetime_kwargs = {}
    dbs["datetime_analysis"] = pd.to_datetime(dbs.Date, **to_datetime_kwargs)
    dbs["datenum_analysis"] = mdates.date2num(
        dbs.datetime_analysis
    ) + dbs.run_time.cumsum() / (60 * 24)
    dbs["datetime_analysis"] = mdates.num2date(dbs.datenum_analysis)
    dbs["blank_from"] = blank_from
    # Generate `logfile`
    dbs["logfile_index"] = dbs.index.values
    rcols = [c for c in dbs.columns if c.startswith("Read")]
    table = {i: {} for i in dbs.index}
    for i, row in dbs.iterrows():
        counts = row[rcols].values.astype(float)
        L = ~np.isnan(counts)
        table[i]["time"] = np.arange(0, L.sum())
        table[i]["counts"] = counts[L]
        table[i]["increments"] = np.append([0], np.diff(counts[L]))
    logfile = pd.DataFrame({"table": table})
    return dbs, logfile
