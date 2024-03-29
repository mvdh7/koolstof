"""Import and parse the data files produced by the PyroScience pH optode."""

import pandas as pd
import os
import numpy as np
from scipy import stats


def pH_optode(spreadsheet_path, text_files_folder_path, cutoff=1200, end_secs=120):
    """Import the txt files generated by Pyro Workbench as a pandas dataframe.
    Process data to get mean pH with a slope closest to 0. Generate table
    with results and stats. Optional kwargs include an option to choose a
    cutoff point in seconds to keep the last X seconds of data (default = 1200 sec),
    and an option to compute pH for the last few seconds of measurements (
    default = 120 sec)."""

    # Import spreadsheet with filenames
    db = pd.read_excel(spreadsheet_path, skiprows=[1])

    # Create list of text files
    file_list = [
        file
        for file in os.listdir(text_files_folder_path)
        if file in db.filename.values
    ]

    # Create loop to extract data
    data = {}
    for file in file_list:
        path = text_files_folder_path + "/{}/{}.txt"
        fname = path.format(file, file)
        data[file] = pd.read_table(fname, skiprows=22, encoding="unicode_escape")

    # Clean up datasets
    # Rename headers of df inside dict
    rn = {
        "Date [A Ch.1 Main]": "date",
        "Time [A Ch.1 Main]": "time",
        " dt (s) [A Ch.1 Main]": "sec",
        "pH [A Ch.1 Main]": "pH",
        "Sample Temp. (°C) [A Ch.1 CompT]": "temp",
    }
    for file in file_list:
        data[file].rename(columns=rn, inplace=True)

        # Drop useless (empty) columns
        data[file].drop(
            columns=[
                "Unnamed: 23",
                "Unnamed: 24",
                "Unnamed: 25",
                "Unnamed: 26",
                "Unnamed: 27",
                "Unnamed: 28",
                "Unnamed: 29",
            ],
            inplace=True,
        )

        # Remove last rows including nans
        L = data[file].pH.isnull()
        data[file] = data[file][~L]

        # Only keep the last X min of data
        if data[file].sec.max() > cutoff:
            L = data[file].sec > (data[file].sec.max() - cutoff)
            data[file] = data[file][L]

    # Make a copy of the data
    data_c = data.copy()

    # Create a table to hold the results
    results = pd.DataFrame({"filename": file_list})
    results["date"] = np.nan
    results["time"] = np.nan
    results["pH_NBS_raw"] = np.nan
    results["pH_NBS_raw_median"] = np.nan
    results["pH_end"] = np.nan
    results["pH_end_median"] = np.nan
    results["slope"] = np.nan
    results["lowest_ix"] = np.nan
    results["pH_NBS"] = np.nan
    results["pH_NBS_median"] = np.nan
    results["pH_NBS_stderr"] = np.nan
    results["pH_NBS_std"] = np.nan
    results["pH_NBS_intercept"] = np.nan

    # Compute the mean and median of the last 2min of measurements
    # using all datapoints inside file
    for file in file_list:
        L = data[file].sec > data[file].sec.max() - end_secs
        F = results.filename == file
        results.loc[F, "pH_end"] = data[file][L].pH.mean()
        results.loc[F, "pH_end_median"] = data[file][L].pH.median()

        # Do a linear regression on all data inside sample file
        slope = stats.linregress(data_c[file].sec, data_c[file].pH)[0]

        # Create column to hold slope results
        data[file]["slope_here"] = np.nan

        # Loop through the data to find the slope closest to 0
        for i in data[file].index[:-5]:
            print("processing...")
            slope = stats.linregress(data_c[file].sec, data_c[file].pH)[0]
            data_c[file] = data_c[file].drop(data_c[file].index[0])
            data_c[file].sort_values(by="sec")
            data[file].loc[i, "slope_here"] = np.abs(slope)
            print(file)

        # Find index of lowest absolute slope
        lowest_ix = data[file].slope_here.idxmin()

        # Store time for pH of slope closest to 0 in df
        results.loc[F, "time"] = data[file].time.loc[lowest_ix][:5]

        # Store temperature for pH of slope closest to 0
        results.loc[F, "temperature"] = data[file].temp.loc[lowest_ix]

        # Store the mean(raw pH) in df
        results.loc[F, "pH_NBS_raw"] = data[file].pH.mean()

        # Store the median (raw pH) in df
        results.loc[F, "pH_NBS_raw_median"] = data[file].pH.median()

        # Store the index of the lowest absolute slope in df
        results.loc[F, "lowest_ix"] = lowest_ix

        # Store the slope from lowest_ix in df
        results.loc[F, "slope"] = data[file].slope_here.loc[lowest_ix]

        # Store the mean (pH slope 0) in df
        results.loc[F, "pH_NBS"] = data[file].pH.loc[lowest_ix:].mean()

        # Store the median (pH slope 0) in df
        results.loc[F, "pH_NBS_median"] = data[file].pH.loc[lowest_ix:].median()

        # Store the standard error for pH slope 0 in df
        results.loc[F, "pH_NBS_stderr"] = stats.linregress(
            data[file].sec.loc[lowest_ix:], data[file].pH.loc[lowest_ix:]
        )[4]

        # Store the standard deviation for pH slope 0 in df
        results.loc[F, "pH_NBS_std"] = (data[file].pH.loc[lowest_ix:]).std()

        # Store the intercept for pH slope 0 in df
        results.loc[F, "pH_NBS_intercept"] = stats.linregress(
            data[file].sec.loc[lowest_ix:], data[file].pH.loc[lowest_ix:]
        )[1]

        # Add extra information
        results.loc[F, "date"] = db.date

    return results
