import warnings

import numpy as np


def _get_logfile_index(dbs_row, logfile):
    """[row.apply] Get index in logfile corresponding to a given row of the dbs
    file.
    """
    if dbs_row.bottle in logfile.bottle.values:
        logfile_index = np.where(
            (dbs_row.bottle == logfile.bottle)
            & (dbs_row.datetime_analysis == logfile.datetime_analysis)
        )[0]
        if np.size(logfile_index) == 1:
            logfile_index = logfile.index[logfile_index[0]]
        else:
            warnings.warn(
                (
                    f"{np.size(logfile_index)} name/date matches found "
                    + f"between dbs and logfile @ dbs loc {dbs_row.name}"
                )
            )
            logfile_index = np.nan
    else:
        logfile_index = np.nan
    return logfile_index


def get_logfile_index(dbs, logfile):
    """Find the index in the logfile corresponding to each row of the dbs file
    and add this in-place to the dbs as "logfile_index".

    Parameters
    ----------
    dbs : pd.DataFrame
        The dbs file as a pandas DataFrame (imported with read_dbs).
    logfile : pd.DataFrame
        The logfile as a pandas DataFrame (imported with read_logfile).
    """
    dbs["logfile_index"] = dbs.apply(
        _get_logfile_index, args=[logfile], axis=1
    )
