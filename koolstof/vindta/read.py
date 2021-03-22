import re
import numpy as np, pandas as pd
from matplotlib import dates as mdates
from . import Dbs


def read_logfile(fname, methods="3C standard"):
    """Import a logfile.bak as a DataFrame.

    Arguments:
    fname -- the filename (and path) of the .dbs file

    Keywords arguments:
    methods -- list of VINDTA methods considered as real measurements
    """
    if isinstance(methods, str):
        methods = [methods]
    # Compile regexs for reading logfile
    re_method = re.compile(r"(" + r"|".join(methods) + r")\.mth run started ")
    re_datetime = re.compile(r"started (\d{2})/(\d{2})/(\d{2})  (\d{2}):(\d{2})")
    re_bottle = re.compile(r"(bottle)?\t([^\t]*)\t")
    re_crm = re.compile(r"CRM\t([^\t]*)\t")
    re_increments = re.compile(r"(\d*)\t(\d*)\t(\d*)\t")
    # Import text from logfile
    with open(fname, "r") as f:
        logf = f.read().splitlines()
    # Initialise arrays
    logdf = {
        "line_number": [],
        "analysis_datetime": np.array([], dtype="datetime64"),
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
            if type(lbot) == str:
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
                logdf["analysis_datetime"] = np.append(logdf["analysis_datetime"], ldt)
                # Get coulometer data
                jdict = {"minutes": [0.0], "counts": [0.0], "increments": [0.0]}
                j = 4
                while re_increments.match(logf[i + j].strip()):
                    jinc = re_increments.findall(logf[i + j].strip())[0]
                    jdict["minutes"].append(float(jinc[0]))
                    jdict["counts"].append(float(jinc[1]))
                    jdict["increments"].append(float(jinc[2]))
                    j += 1
                jdict = {k: np.array(v) for k, v in jdict.items()}
                logdf["table"].append(jdict)
                logdf["counts"].append(jdict["counts"][-1])
                logdf["run_time"].append(j - 4.0)
            else:
                print("Logfile line {}: bottle name not found!".format(i + 1))
    # Convert lists to arrays and put logfile into DataFrame
    logdf = pd.DataFrame({k: np.array(v) for k, v in logdf.items()})
    logdf.set_index("line_number", inplace=True)
    return logdf


# More Python-friendly names for the .dbs columns
dbs_mapper = {
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
dbs_drop = [
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


def dbs_datetime(dbs_row):
    """Convert date and time from .dbs file into datetime."""
    try:
        dspl = dbs_row["date"].split("/")
        analysis_datetime = np.datetime64(
            "-".join(("20" + dspl[2], dspl[0], dspl[1])) + "T" + dbs_row["time"]
        )
    except AttributeError:
        analysis_datetime = np.datetime64("NaT")
    return pd.Series(
        {
            "analysis_datetime": analysis_datetime,
        }
    )


def read_dbs(fname, keep_all_cols=False, logfile=None):
    """Import a .dbs file from a VINDTA, rename the columns, and reformat the date/time.

    Arguments:
    fname -- the filename (and path) of the .dbs file

    Keyword arguments:
    keep_all_cols -- keep all original columns from the .dbs?
    logfile -- the DataFrame containing the logfile.bak
    """
    headers = np.genfromtxt(fname, delimiter="\t", dtype=str, max_rows=1)
    dbs = pd.read_table(fname, header=0, names=headers, usecols=headers).rename(
        columns=dbs_mapper
    )
    dbs["dbs_fname"] = fname
    dbs = Dbs(dbs.assign(**dbs.apply(dbs_datetime, axis=1)))
    dbs["analysis_datenum"] = mdates.date2num(dbs.analysis_datetime)
    if not keep_all_cols:
        dbs.drop(columns=dbs_drop, inplace=True)
    if logfile is not None:
        assert isinstance(logfile, pd.DataFrame), "`logfile` must be a DataFrame."
        dbs.logfile = logfile
    return dbs
