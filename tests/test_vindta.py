import pandas as pd, numpy as np
from koolstof import vindta as ksv

logfile_fname = "tests/data/logfile_20200407.bak"
dbs_fname = "tests/data/2018_Aug_RWS_CO2.dbs"
logfile = ksv.read_logfile(logfile_fname, methods=["3C standard", "3C standardRWS"])
dbs = ksv.read_dbs(dbs_fname)
sessions = ksv.blank_correction(dbs, logfile)
dbs["dic_certified"] = np.where(dbs.bottle.str.startswith("CRM"), 2029.19, np.nan)
ksv.calibrate_dic(dbs, sessions)


def test_read_dbs():
    """Is the dbs correctly imported and are columns dropped (or not)?"""
    dbs = ksv.read_dbs(dbs_fname)
    assert isinstance(dbs, pd.DataFrame)
    assert "dic_cell_id" in dbs
    assert "run_type" not in dbs
    dbs = ksv.read_dbs(dbs_fname, drop_cols=False)
    assert isinstance(dbs, pd.DataFrame)
    assert "dic_cell_id" in dbs
    assert "run_type" in dbs


def test_get_logfile_index():
    dbs = ksv.read_dbs(dbs_fname)
    assert "logfile_index" not in dbs
    ksv.get.get_logfile_index(dbs, logfile)
    assert "logfile_index" in dbs


def test_get_sample_blanks():
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get.get_sample_blanks(dbs, logfile)
    assert "blank_here" in dbs


def test_get_session_blanks():
    dbs = ksv.read_dbs(dbs_fname)
    sessions = ksv.get.get_session_blanks(dbs, logfile)
    assert isinstance(sessions, pd.DataFrame)
    assert "blank_here" in dbs


def test_get_counts_corrected():
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get.get_counts_corrected(dbs, logfile)
    assert "counts_corrected" in dbs
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get.get_sample_blanks(dbs, logfile)
    ksv.get.get_counts_corrected(dbs)
    assert "counts_corrected" in dbs


def test_blank_correction():
    dbs = ksv.read_dbs(dbs_fname)
    sessions = ksv.blank_correction(dbs, logfile)
    assert isinstance(sessions, pd.DataFrame)
    assert "counts_corrected" in dbs


def test_get_standard_calibrations():
    dbs = ksv.read_dbs(dbs_fname)
    ksv.blank_correction(dbs, logfile)
    dbs["dic_certified"] = np.nan
    dbs.loc[dbs.bottle.str.startswith("CRM"), "dic_certified"] = 2029.19
    ksv.get.get_standard_calibrations(dbs)
    assert "k_dic_here" in dbs


def test_calibrate_dic():
    dbs = ksv.read_dbs(dbs_fname)
    sessions = ksv.blank_correction(dbs, logfile)
    dbs["dic_certified"] = np.nan
    dbs.loc[dbs.bottle.str.startswith("CRM"), "dic_certified"] = 2029.19
    ksv.calibrate_dic(dbs, sessions)
    assert "k_dic_mean" in sessions
    assert "k_dic" in dbs
    assert "dic" in dbs
    assert ~dbs.dic.isnull().any()


def test_plots():
    ksv.plot_increments(dbs, logfile)
    ksv.plot_session_blanks(dbs, sessions, sessions.index[0])
    ksv.plot_blanks(dbs, sessions)
    ksv.plot_k_dic(dbs, sessions)
    ksv.plot_dic_offset(dbs, sessions)
    dbs.loc[
        (dbs.dic_cell_id == "C_Aug14-18_0708")
        & ((dbs.bottle == "CRM#171") | (dbs.bottle == "CRM#171B")),
        "k_dic_good",
    ] = False
    ksv.calibrate_dic(dbs, sessions)
    ksv.plot_k_dic(dbs, sessions, show_ignored=False)
    ksv.plot_dic_offset(dbs, sessions)


# test_read_dbs()
# test_get_logfile_index()
# test_get_sample_blanks()
# test_get_session_blanks()
# test_get_counts_corrected()
# test_blank_correction()
# test_get_standard_calibrations()
# test_calibrate_dic()
# test_plots()
