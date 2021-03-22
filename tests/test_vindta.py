import koolstof as ks, numpy as np, pandas as pd

# Import the VINDTA logfile
fpath = "tests/data/"
logfile = ks.read_logfile(
    fpath + "logfile_20200407.bak",
    methods=["3C standard", "3C standardRWS"],
)

# Import a .dbs file for part of that logfile
dbs = ks.read_dbs(fpath + "2018_Aug_RWS_CO2.dbs", logfile=logfile)

# Add metadata
dbs["dic_certified"] = np.where(dbs.station == 666, 2029.19, np.nan)
dbs["salinity"] = np.where(dbs.station == 666, 33.434, 35)

# Do QC
dbs["blank_good"] = True
dbs.loc[dbs.bottle == "WALCRN2_2018005578", "blank_good"] = False

# Do processing
dbs.calibrate_dic()
sub = dbs.subset(dbs.dic_cell_id == "C_Aug13-18_1008")


def dbs_assertions(dbs):
    assert isinstance(dbs, pd.DataFrame)
    assert isinstance(dbs, ks.Dbs)
    assert hasattr(dbs, "sessions")
    assert isinstance(dbs.sessions, pd.DataFrame)
    assert hasattr(dbs, "logfile")
    assert isinstance(dbs.logfile, pd.DataFrame)


def test_import_and_calibration():
    assert "dic" in dbs
    dbs_assertions(dbs)


# def test_plots():
#     dbs.plot_blanks()
#     dbs.plot_k_dic()
#     dbs.plot_dic_offset()


def test_subset():
    dbs_assertions(sub)
    sub.plot_dic_offset()


# test_import_and_calibration()
# test_plots()
# test_subset()
