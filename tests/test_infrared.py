import pandas as pd
from koolstof import infrared as ksi

filepath_dbs = "data/Humphreys_peakform.dbs"
filepath_licor = "data/Humphreys_peakform_00.txt"


def test_read_dbs():
    dbs = ksi.io.read_dbs(filepath_dbs)
    assert isinstance(dbs, pd.DataFrame)
    return dbs


def test_read_licor():
    licor = ksi.io.read_LI7000(filepath_licor)
    assert isinstance(licor, pd.DataFrame)
    return licor


dbs = test_read_dbs()
licor = test_read_licor()
