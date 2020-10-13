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
    )
