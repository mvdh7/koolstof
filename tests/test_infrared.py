import numpy as np, pandas as pd
from scipy import signal, integrate
from matplotlib import pyplot as plt, dates as mdates
from koolstof import infrared as ksi

filepath = "data/Humphreys_peakform/"
filepath_dbs = filepath + "Humphreys_peakform.dbs"
filepath_licor = "data/Humphreys_peakform_03.txt"
filepath_support = "data/Humphreys_peakform.xlsx"


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

# Get supporting metadata (flow rates)
support = pd.read_excel(filepath_support)
dbs["flow_rate"] = np.nan
dbs["sample_volume"] = np.nan
for supp_ix in support.index:
    dbs_ix = dbs[dbs.bottle == support.loc[supp_ix].bottle].index
    dbs.loc[dbs_ix, "flow_rate_mlmin"] = support.loc[supp_ix].flow_rate  # in ml/min
    dbs.loc[dbs_ix, "sample_volume"] = support.loc[supp_ix].sample_volume  # in μl
dbs["flow_rate"] = dbs.flow_rate_mlmin * 1e-5 / 60  # in m3/s


def test_get_licor_samples():
    licor_with_samples = ksi.io.get_licor_samples(licor, dbs)
    assert np.all(np.isin(licor_with_samples.dbs_ix, dbs.index))
    return licor_with_samples


licor = test_get_licor_samples()


licor["x_CO2_baseline"] = ksi.baseline.als(licor.x_CO2, lam=1e9, p=1e-4, niter=10)
licor["x_CO2_corrected"] = licor.x_CO2 - licor.x_CO2_baseline
licor["flow_CO2"] = (  # in mol/m**3
    licor.x_CO2_corrected
    * licor.pressure
    * 1e-3
    / ((licor.temperature + 273.15) * 8.314_462_618)
)
peaks = {}
peaks["licor_iloc"], peaks_info = signal.find_peaks(
    licor.x_CO2_corrected, distance=60, prominence=20, width=80, threshold=0
)
peaks = pd.DataFrame(peaks)
peaks["licor_ix"] = licor.iloc[peaks.licor_iloc].index
peaks["dbs_ix"] = licor.loc[peaks.licor_ix].dbs_ix.values
peaks["prominence"] = peaks_info["prominences"]
peaks["start_ix"] = np.nan
peaks["end_ix"] = np.nan
peaks["integral"] = np.nan
for peak_ix in peaks.index:
    peak = peaks.loc[peak_ix]
    i50 = licor.x_CO2_corrected <= 0.5 * peak.prominence
    i50_left = i50 & (licor.datenum < licor.loc[peak.licor_ix].datenum)
    i50_right = i50 & (licor.datenum > licor.loc[peak.licor_ix].datenum)
    # Offsets (60 and 200) assume LI-COR file is 2 Hz & standard AIRICA settings
    start_ix = licor[i50_left].index[-1] - 60
    end_ix = licor[i50_right].index[0] + 200
    peaks.loc[peak_ix, "start_ix"] = start_ix
    peaks.loc[peak_ix, "end_ix"] = end_ix
    # Integral dx assumes LI-COR file is 2 Hz
    peaks.loc[peak_ix, "flow_integral"] = integrate.trapz(
        licor.loc[start_ix:end_ix].flow_CO2.values, dx=0.5
    )  # in mol*s/m**3
peaks["start_datetime"] = licor.loc[peaks.start_ix].datetime.values
peaks["end_datetime"] = licor.loc[peaks.end_ix].datetime.values
# Duration rounding assumes LI-COR file is 2 Hz
peaks["duration"] = (
    np.round(
        (
            (
                mdates.date2num(peaks.end_datetime)
                - mdates.date2num(peaks.start_datetime)
            )
            * (60 * 60 * 24)
        )
        * 2
    )
    / 2
)
for var in ["flow_rate", "sample_volume"]:
    peaks[var] = dbs.loc[peaks.dbs_ix, var].values
peaks["total_CO2"] = peaks.flow_integral * peaks.flow_rate  # in mol
peaks["dic"] = 1e12 * peaks.total_CO2 / peaks.sample_volume

#%%
ixs = dbs.index[-10:-7]
ix = ixs[1]

l = np.isin(licor.dbs_ix, ixs)
l2 = licor.dbs_ix == ix

fig, ax = plt.subplots(dpi=300)
licor.plot("datetime", "x_CO2", ax=ax, linewidth=1, c="k")
licor.plot("datetime", "x_CO2_corrected", ax=ax, linewidth=1, linestyle="--", c="r")

licor.loc[peaks.licor_ix].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="c", zorder=100, marker="^"
)
licor.loc[peaks.start_ix].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="b", zorder=100
)
licor.loc[peaks.end_ix].plot.scatter(
    "datetime", "x_CO2_corrected", ax=ax, c="lime", zorder=101, marker="+"
)
ax.axhline(0.0, c="k", linewidth=0.8)
# ax.set_xlim([np.min(licor[l2].datenum), np.max(licor[l2].datenum)])
# ax.set_ylim([-5, 10])
for i in range(len(peaks.licor_ix)):
    peaks_here = [peaks.start_ix[i], peaks.licor_ix[i], peaks.end_ix[i]]
    ax.plot(
        licor.loc[peaks_here].datetime, licor.loc[peaks_here].x_CO2_corrected, c="k"
    )
