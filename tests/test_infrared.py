import numpy as np
import pandas as pd
from scipy import signal
from matplotlib import pyplot as plt
from koolstof import infrared as ksi

filepath = "data/Humphreys_peakform/"
filepath_dbs = filepath + "Humphreys_peakform.dbs"
filepath_licor = "data/Humphreys_peakform_03.txt"


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


licor["x_CO2_baseline"] = ksi.baseline.als(licor.x_CO2, lam=1e9, p=1e-4, niter=10)
licor["x_CO2_corrected"] = licor.x_CO2 - licor.x_CO2_baseline
peaks_iloc, peaks_info = signal.find_peaks(
    licor.x_CO2_corrected, distance=60, prominence=20, width=80)
peaks_loc = licor.iloc[peaks_iloc].index
peaks_left = licor.iloc[peaks_info["left_bases"]].index
peaks_right = licor.iloc[peaks_info["right_bases"]].index

#%%
# for peak in peaks_loc:
    

#%%


ixs = dbs.index[-10:-7]
ix = ixs[1]

l = np.isin(licor.dbs_ix, ixs)
l2 = licor.dbs_ix == ix

fig, ax = plt.subplots(dpi=300)
licor[l2].plot("datetime", "x_CO2", ax=ax, linewidth=1, c="k")
licor[l2].plot("datetime", "x_CO2_corrected", ax=ax, linewidth=1, linestyle="--", c="r")

licor.loc[peaks_loc].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="c", zorder=100, marker='^'
)
licor.loc[peaks_left].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="b", zorder=100
)
licor.loc[peaks_right].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="lime", zorder=101, marker='+'
)
ax.axhline(0.0, c="k", linewidth=0.8)
ax.set_xlim([np.min(licor[l2].datenum), np.max(licor[l2].datenum)])
# ax.set_ylim([-5, 5])
for i in range(len(peaks_loc)):
    peaks_here = [peaks_left[i], peaks_loc[i], peaks_right[i]]
    ax.plot(licor.loc[peaks_here].datetime,
            licor.loc[peaks_here].x_CO2_corrected,
            c="k")

