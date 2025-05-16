# %%
import numpy as np
import plotly.graph_objects as go  # noqa
from matplotlib import dates as mdates, pyplot as plt

import koolstof as ks


# Import dbs and logfile
dbs_fname = "tests/data/2018_Aug_RWS_CO2.dbs"
logfile_fname = "tests/data/logfile_20200407.bak"
dbs, logfile = ks.read_vindta(
    dbs_fname,
    logfile_fname,
    blank_from=7,
    methods=["3C standard", "3C standardRWS"],
)

# Calculate sample blanks
ks.blank_per_measurement(dbs, logfile)

# Calculate single session blank progression
# dbs["blank_here_std"] = 1
# dbs["blank_here_count"] = 1
dbs_session = dbs[dbs.dic_cell_id == "C_Aug13-18_1008"].copy()
session = ks.session_blank(dbs_session)
dbs_session["datenum_analysis_scaled"] = ks.blank._centre_and_scale(
    dbs_session.datenum_analysis,
    x_factor=session.datenum_analysis_std,
    x_offset=session.datenum_analysis_mean,
)

sessions = ks.blank_per_session(dbs)

# Visualise
fig, ax = plt.subplots(dpi=300)
# Create and draw fitted line
fx = np.linspace(
    dbs_session.datenum_analysis_scaled.min(),
    dbs_session.datenum_analysis_scaled.max(),
    500,
)
fy = ks.blank._blank_progression(session.blank_progression, fx)
fx = mdates.num2date(
    ks.blank._de_centre_and_scale(
        fx, session.datenum_analysis_std, session.datenum_analysis_mean
    )
)
ax.plot(fx, fy)
# Blanks
ax.errorbar(
    dbs_session.datetime_analysis,
    dbs_session.blank_here,
    [
        dbs_session.blank_here - dbs_session.blank_here_min,
        dbs_session.blank_here_max - dbs_session.blank_here,
    ],
    linestyle="none",
    marker="o",
    markersize=5,
)
ax.xaxis.set_major_locator(mdates.HourLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
ax.set_xlabel("Time of day of analysis")

# # Scatter blanks
# scatter = go.Scatter(
#     x=dbs_session.datetime_analysis,
#     y=dbs_session.blank_here,
#     mode="markers",
# )

# # Create and draw fitted line
# fx = np.linspace(
#     dbs_session.datenum_analysis_scaled.min(),
#     dbs_session.datenum_analysis_scaled.max(),
#     500,
# )
# fy = ks.blank._blank_progression(session.blank_progression, fx)
# fx = mdates.num2date(
#     ks.blank._de_centre_and_scale(
#         fx, session.datenum_analysis_std, session.datenum_analysis_mean
#     )
# )
# line = go.Scatter(
#     x=fx,
#     y=fy,
#     mode="lines",
#     name="Fitted blank",
# )

# fig = go.Figure(
#     [
#         line,
#         scatter,
#     ]
# )
# fig.show()
