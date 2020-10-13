import koolstof as ks, numpy as np

# Import the VINDTA logfile
fpath = "../rws-monitoring/data/VINDTA#15 Data/"
logfile = ks.read_logfile(
    fpath + "logfile_20200407.bak", methods=["3C standard", "3C standardRWS"],
)

# Import a .dbs file for part of that logfile and add metadata
dbs = ks.read_dbs(fpath + "2018/2018_Aug_RWS_CO2.dbs", logfile=logfile)
dbs["dic_cert"] = np.where(dbs.station == 666, 2029.19, np.nan)
dbs["salinity"] = np.where(dbs.station == 666, 33.434, 35)

# Do all the processing
dbs.get_session_calibrations()
