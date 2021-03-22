"""Import and parse the data files produced by the Marianda AIRICA."""

import pandas as pd
import numpy as np
from matplotlib import dates as mdates
from scipy import stats
import seaborn as sns
from calkulate.density import seawater_1atm_MP81
import matplotlib.pyplot as plt


# extract data from dbs
mapper_dbs = {
    "run type": "run_type",
    "i.s. temp.": "temperature_insitu",
    "sample mass": "mass_sample",
    "rep#": "rep",
    "CT": "dic",
    "factor CT": "dic_factor",
    "CV (µmol)": "cv_micromol",
    "CV (%)": "cv_percent",
    "last CRM CT": "lastcrm_dic_measured",
    "cert. CRM CT": "lastcrm_dic_certified",
    "CRM batch": "lastcrm_batch",
    "calc. mode": "mode_calculation",
    "integ. mode": "mode_integration",
    "Lat.": "latitude",
    "Long.": "longitude",
    "area#1": "area_1",
    "area#2": "area_2",
    "area#3": "area_3",
    "area#4": "area_4",
}


def read_dbs(filepath_or_buffer, encoding="unicode_escape", na_values="none", **kwargs):
    """Import the dbs file generated by a Marianda AIRICA as a pandas DataFrame.
    All kwargs are passed to pandas.read_table.
    """
    dbs = pd.read_table(
        filepath_or_buffer, encoding=encoding, na_values=na_values, **kwargs
    )
    dbs.rename(mapper=mapper_dbs, axis=1, inplace=True)
    dbs.drop(columns="Unnamed: 32", inplace=True)
    dbs["datetime"] = pd.to_datetime(
        dbs.apply(lambda x: " ".join((x.date, x.time)), axis=1)
    )
    dbs["datenum"] = mdates.date2num(dbs.datetime)
    return dbs


def process_airica(crm_val, db, dbs_filepath, results_file_path_and_name):
    """Process AIRICA raw data by extracting data from .dbs file and
    adding it to .xlsx file, calculating conversion factor from CRMs and
    computing TCO2 values.
    """

    # import ".dbs" file
    data = read_dbs(dbs_filepath)

    # add ".dbs" data to ".xlsx"
    db = pd.merge(left=db, right=data, how="left", left_on="name", right_on="bottle")

    # check that ".dbs" bottle = ".xlsx" name and drop "bottle" column
    if db["name"].equals(db["bottle"]):
        print("SUCCESSFUL DBS IMPORT")
        db = db.drop(columns=["bottle"])
    else:
        KeyError
        print("ERROR: mismatch between dbs and xlsx files")

    # recalculate density
    db["density_analysis"] = np.nan
    db["density_analysis"] = seawater_1atm_MP81(db.temperature, db.salinity_rws)

    # average areas with all areas and only last 3 areas
    db["area_av_4"] = (db.area_1 + db.area_2 + db.area_3 + db.area_4) / 4
    db["area_av_3"] = (db.area_2 + db.area_3 + db.area_4) / 3

    # calculate DIC * density * sample_v
    db["CT_d_sample_v"] = crm_val * db.density_analysis * db.sample_v

    # create columns to hold conversion factor (CF) values
    db["a_3"] = np.nan
    db["a_4"] = np.nan
    db["b_3"] = np.nan
    db["b_4"] = np.nan

    # calc CRM coeff factor
    def get_CF(db):
        """Calculate conversion factor CF for each analysis batch."""
        L = db.location == "CRM"
        b_3, a_3 = stats.linregress(db.area_av_3[L], db.CT_d_sample_v[L])[:2]
        b_4, a_4 = stats.linregress(db.area_av_3[L], db.CT_d_sample_v[L])[:2]
        return pd.Series({"a_3": a_3, "a_4": a_4, "b_3": b_3, "b_4": b_4})

    db_cf = db.groupby(by=["analysis_batch"]).apply(get_CF)

    # assign CRM a and b to samples based on analysis batch
    db["a_3"] = db_cf.loc[db.analysis_batch.values, "a_3"].values
    db["a_4"] = db_cf.loc[db.analysis_batch.values, "a_4"].values
    db["b_3"] = db_cf.loc[db.analysis_batch.values, "b_3"].values
    db["b_4"] = db_cf.loc[db.analysis_batch.values, "b_4"].values

    # calculate TCO2 values
    db["TCO2_3"] = np.nan
    db["TCO2_4"] = np.nan

    db["TCO2_3"] = ((db.b_3 * db.area_av_3) + db.a_3) / (
        db.density_analysis * db.sample_v
    )
    db["TCO2_4"] = ((db.b_4 * db.area_av_4) + db.a_4) / (
        db.density_analysis * db.sample_v
    )

    # plot regression
    f, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    sns.set_style("darkgrid")
    sns.set_context("paper", font_scale=2)
    sns.set(font="Verdana", font_scale=1)
    sns.despine(f, left=True, bottom=True)

    L = db.location == "CRM"
    sns.regplot(
        x=db.area_av_3[L], y=db.CT_d_sample_v[L], ci=False, color="xkcd:primary blue"
    )

    # add R2 to graph
    r2 = stats.linregress(db.area_av_3[L], db.CT_d_sample_v[L])[2]
    r2s = str(round(r2, 2))
    text = "$R^2$ = " + r2s
    ax.text(
        30000,
        4500000,
        text,
        horizontalalignment="left",
        verticalalignment="center",
        fontsize=15,
    )

    plt.tight_layout()

    # save results as text file
    db.to_csv(results_file_path_and_name, index=None)

    return db
