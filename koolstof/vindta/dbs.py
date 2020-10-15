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

    def subset(self, condition, batch_col="dic_cell_id"):
        """Create a subset of this dbs based on the logical condition."""
        lf = self.logfile
        ss = self.sessions
        dbs_subset = Dbs(self[condition])
        dbs_subset.logfile = lf
        dbs_subset.sessions = ss.loc[self[batch_col].unique()]
        return dbs_subset
