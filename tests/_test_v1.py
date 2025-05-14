# %%
import koolstof as ks


# Import dbs and logfile
dbs_fname = "tests/data/2018_Aug_RWS_CO2.dbs"
logfile_fname = "tests/data/logfile_20200407.bak"
dbs, logfile = ks.read.read_vindta(
    dbs_fname,
    logfile_fname,
    blank_from=7,
    methods=["3C standard", "3C standardRWS"],
)

# Calculate sample blanks
ks.blank.get_sample_blanks(dbs, logfile)
