import numpy as np
import pandas as pd
from scipy import signal
from matplotlib import pyplot as plt
from koolstof import infrared as ksi

filepath = "data/Humphreys_peakform/"
filepath_dbs = filepath + "Humphreys_peakform.dbs"
filepath_licor = "data/Humphreys_peakform_01.txt"


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


def test_get_licor_samples():
    licor_with_samples = ksi.io.get_licor_samples(licor, dbs)
    assert np.all(np.isin(licor_with_samples.dbs_ix, dbs.index))
    return licor_with_samples


licor = test_get_licor_samples()


#%%
licor["x_CO2_diff"] = licor.x_CO2.diff()

ix = dbs.index[27]
l = licor.dbs_ix == ix
fig, ax = plt.subplots()
ly = np.cumsum(licor[l].x_CO2)
ax.plot(licor[l].datetime, ly)
# licor[l].plot("datetime", "x_CO2_diff", ax=ax)
peaks = signal.find_peaks(licor[l].x_CO2,
                          distance=60,
                          prominence=50)
licor_peaks = licor[l].iloc[peaks[0]].index
licor.loc[licor_peaks].plot.scatter("datetime", "x_CO2_diff", ax=ax)
