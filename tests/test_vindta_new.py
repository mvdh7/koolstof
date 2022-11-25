import pandas as pd
from koolstof import vindta as ksv

logfile_fname = "tests/data/logfile_20200407.bak"
dbs_fname = "tests/data/2018_Aug_RWS_CO2.dbs"
logfile = ksv.read_logfile(logfile_fname)
dbs = ksv.read_dbs(dbs_fname)


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
    ksv.get_logfile_index(dbs, logfile)
    assert "logfile_index" in dbs


def test_get_sample_blanks():
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get_sample_blanks(dbs, logfile)
    assert "blank_here" in dbs


def test_get_session_blanks():
    dbs = ksv.read_dbs(dbs_fname)
    sessions = ksv.get_session_blanks(dbs, logfile)
    assert isinstance(sessions, pd.DataFrame)
    assert "blank_here" in dbs


def test_get_counts_corrected():
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get_counts_corrected(dbs, logfile)
    assert "counts_corrected" in dbs
    dbs = ksv.read_dbs(dbs_fname)
    ksv.get_sample_blanks(dbs, logfile)
    ksv.get_counts_corrected(dbs)
    assert "counts_corrected" in dbs


def test_get_blanks():
    dbs = ksv.read_dbs(dbs_fname)
    dbs, sessions = ksv.get_blanks(dbs, logfile)
    assert "counts_corrected" in dbs
    dbs, sessions = ksv.get_blanks(dbs_fname, logfile_fname)
    assert "counts_corrected" in dbs


# test_read_dbs()
# test_get_logfile_index()
# test_get_sample_blanks()
# test_get_session_blanks()
# test_get_counts_corrected()
# test_get_blanks()
