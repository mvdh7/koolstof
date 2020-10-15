import pandas as pd


class Dbs(pd.DataFrame):
    logfile = None
    sessions = None

    from .get import (
        get_logfile_index,
        get_sample_blanks,
        get_session_blanks,
        get_blank_corrections,
        get_density,
        get_standard_calibrations,
        get_session_calibrations,
        calibrate_dic,
    )
    from .plot import plot_blanks, plot_session_blanks, plot_k_dic, plot_dic_offset


def concat(objs, logfile=None, **kwargs):
    """Concatenate imported .dbs files."""
    obj = pd.concat(objs, **kwargs)
    obj.reset_index(drop=True, inplace=True)
    obj = Dbs(obj)
    obj.logfile = logfile
    return obj
