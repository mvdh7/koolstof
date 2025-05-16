# %%
import koolstof as ks


dbs, logfile = ks.read_uic("tests/data/UIC-01302401.CSV", blank_from=9)
ks.plot_increments(dbs, logfile)
ks.blank_per_measurement(dbs, logfile)
sessions = ks.blank_per_session(dbs)
ks.blank.counts_corrected(dbs, logfile=logfile, sessions=sessions)
ks.plot_blanks(dbs, sessions)
