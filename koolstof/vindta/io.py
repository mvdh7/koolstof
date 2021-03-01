"""Import and parse the data files produced by the Marianda VINDTA 3C."""

import re
import numpy as np, pandas as pd
from matplotlib import dates as mdates


def add_func_cols(df, func, *args, **kwargs):
    """Add results of df.apply(func) to df as new columns."""
    return df.join(df.apply(lambda x: func(x, *args, **kwargs), axis=1))


def dbs_datetime(dbsx):
    """Convert date and time from .dbs file into datetime and datenum."""
    dspl = dbsx["date"].split("/")
    analysis_datetime = np.datetime64(
        "-".join(("20" + dspl[2], dspl[0], dspl[1])) + "T" + dbsx["time"]
    )
    return pd.Series(
        {
            "analysis_datetime": analysis_datetime,
            "analysis_datenum": mdates.date2num(analysis_datetime),
        }
    )


def read_dbs(fname):
    """Import one .dbs file as single DataFrame."""
    headers = np.genfromtxt(fname, delimiter="\t", dtype=str, max_rows=1)
    dbs = pd.read_table(fname, header=0, names=headers, usecols=headers)
    dbs["dbs_fname"] = fname
    dbs = add_func_cols(dbs, dbs_datetime)
    return dbs


def read_logfile(fname, methods="3C standard"):
    """Import a logfile.bak as a DataFrame."""
    if isinstance(methods, str):
        methods = [methods]
    # Compile regexs for reading logfile
    re_method = re.compile(
        r"(" + r"|".join(methods) + r")\.mth run started ".format(methods)
    )
    re_datetime = re.compile(r"started (\d{2})/(\d{2})/(\d{2})  (\d{2}):(\d{2})")
    re_bottle = re.compile(r"(bottle)?\t([^\t]*)\t")
    re_crm = re.compile(r"CRM\t([^\t]*)\t")
    re_increments = re.compile(r"(\d*)\t(\d*)\t(\d*)\t")
    # Import text from logfile
    with open(fname, "r") as f:
        logf = f.read().splitlines()
    # Initialise arrays
    logdf = {
        "logfile_line": [],
        "analysis_datetime": np.array([], dtype="datetime64"),
        "bottle": [],
        "table": [],
        "counts_total": [],
        "runtime": [],
        "method": [],
    }
    # Parse file line by line
    for i, line in enumerate(logf):
        if re_method.match(line):
            logdf["logfile_line"].append(i)
            logdf["method"].append(re_method.findall(line)[0])
            # Get analysis date and time
            ldt = re_datetime.findall(line)[0]
            ldt = np.datetime64(
                "{}-{}-{}T{}:{}".format("20" + ldt[2], ldt[0], ldt[1], ldt[3], ldt[4])
            )
            logdf["analysis_datetime"] = np.append(logdf["analysis_datetime"], ldt)
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
                logdf["counts_total"].append(jdict["counts"][-1])
                logdf["runtime"].append(j - 4.0)
            else:
                print("Logfile line {}: bottle name not found!".format(i + 1))
    # Convert lists to arrays and logfile to DataFrame
    logdf = {k: np.array(v) for k, v in logdf.items()}
    return pd.DataFrame(logdf)


def get_logfile_index(dbs_row, logfile):
    """Get index in logfile corresponding to a given row of the dbs file."""
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


def logfile2dbs(dbs_row, logfile):

    if dbs_row.bottle in logfile.bottle.values:
        xix = np.where(
            (dbs_row.bottle == logfile.bottle)
            & (dbs_row.analysis_datetime == logfile.analysis_datetime)
        )[0]
        assert len(xix) == 1, (
            "{} name/date matches found between dbs and logfile @ dbs loc {}"
        ).format(len(xix), dbs_row.name)
        xix = logfile.index[xix[0]]
    else:
        xix = np.nan
    return pd.Series({"logfile_index": xix})


# def logfile2dbs(dbs, logfile):
#     """Get index in logfile corresponding to each row in dbs."""

#     def _logfile2dbs(x, logfile):
#         if x.bottle in logfile.bottle.values:
#             xix = np.where(
#                 (x.bottle == logfile.bottle)
#                 & (x.analysis_datetime == logfile.analysis_datetime)
#             )[0]
#             assert len(xix) == 1, (
#                 "{} name/date matches found between dbs and logfile @ dbs iloc {}"
#             ).format(len(xix), x.name)
#             xix = logfile.index[xix[0]]
#         else:
#             xix = np.nan
#         return pd.Series({"logfile_index": xix})

#     return add_func_cols(dbs, _logfile2dbs, logfile)
