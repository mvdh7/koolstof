# %% Tests where the logfile has an incomplete sample at the end
import pandas as pd

import koolstof as ks


def test_logfilex():
    dbs, logfile = ks.read_vindta(
        "tests/data/2026_05_DIC_ILC/2026_05_DIC-ILC.dbs",
        "tests/data/2026_05_DIC_ILC/logfilex.bak",
        methods=[
            "3C standardRWS",
            "3C standardRWS - NUTS",
            "3C standardRWS DIC ONLY",
        ],
    )
    assert isinstance(dbs, pd.DataFrame)
    assert isinstance(logfile, pd.DataFrame)
    assert dbs.logfile_index.notnull().all()


# test_logfilex()
