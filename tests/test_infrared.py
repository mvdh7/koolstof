import numpy as np
import pandas as pd
from scipy import signal, sparse
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


def baseline_als(y, lam, p, niter=10):
    """Baseline correction."""
    # https://stackoverflow.com/questions/29156532/python-baseline-correction-library
    L = len(y)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    D = lam * D.dot(D.transpose())
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for i in range(niter):
        W.setdiag(w)
        Z = W + D
        z = sparse.linalg.spsolve(Z, w * y)
        w = p * (y > z) + (1.0 - p) * (y < z)
    return z


licor["x_CO2_baseline"] = baseline_als(licor.x_CO2, lam=1e9, p=1e-4, niter=10)
licor["x_CO2_corrected"] = licor.x_CO2 - licor.x_CO2_baseline

#%%
licor["x_CO2_diff"] = licor.x_CO2.diff()

ixs = dbs.index[-9:-6]
ix = ixs[1]

l = np.isin(licor.dbs_ix, ixs)
l2 = licor.dbs_ix == ix

fig, ax = plt.subplots(dpi=300)
# ly = np.cumsum(licor[l].x_CO2)
# ax.plot(licor[l].datetime, ly)
licor[l2].plot("datetime", "x_CO2", ax=ax, linewidth=1, c='k')
licor[l2].plot("datetime", "x_CO2_corrected", ax=ax, linewidth=1, linestyle='--',
               c='r')
peaks = signal.find_peaks(
    licor[l2].x_CO2_corrected, distance=60, prominence=20, width=80
)
licor_peaks = licor[l2].iloc[peaks[0]].index
licor.loc[licor_peaks].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="b", zorder=100
)

ax.axhline(0.0, c="k", linewidth=0.8)

# ax.plot(licor[l2].datetime, licor[l2].x_CO2_baseline)
# ax.set_ylim(np.array([-0.5,1 1]) * 10)
