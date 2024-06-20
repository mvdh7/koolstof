import pandas as pd
import numpy as np


def read_cary_oxygen(filename, us_date_format=False):
    """Import oxygen data from Agilent Cary spectrophotometer report.

    Parameters
    ----------
    filename : str
        The file name (and path) for the .csv report.
    us_date_format : bool, optional
        Whether the dates in the file are in US format (month first), by default False.

    Returns
    -------
    pd.DataFrame
        The data from the file parsed into a pandas DataFrame.
    """
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    data_start = []
    data_end = []
    for i, line in enumerate(lines):
        if line == "Sample\tF\tMean\tSD\t%RSD\tReadings":
            data_start.append(i)
        elif line == "Results Flags Legend":
            data_end.append(i)
    data = []
    for start, end in zip(data_start, data_end):
        data_ = pd.read_csv(
            filename,
            skiprows=start,
            skipfooter=len(lines) - end,
            sep="\t",
            engine="python",
        )
        if us_date_format:
            mm, dd, yyyy = lines[start - 1].split()[2].split("/")
        else:
            dd, mm, yyyy = lines[start - 1].split()[2].split("/")
        HH, MM, SS = lines[start - 1].split()[3].split(":")
        try:
            if lines[start - 1].split()[4] == "PM" and HH != "12":
                HH = int(HH) + 12
        except IndexError:
            pass
        data_["datetime"] = np.datetime64(
            "{:04.0f}-{:02.0f}-{:02.0f}T{:02.0f}:{:02.0f}:{:02.0f}".format(
                int(yyyy), int(mm), int(dd), int(HH), int(MM), int(SS)
            )
        )
        data.append(data_)
    data = (
        pd.concat(data)
        .rename(
            columns={
                "Sample": "sample_name",
                "F": "flag",
                "Mean": "absorbance_mean",
                "SD": "absorbance_std",
                "%RSD": "absorbance_rsd_pct",
                "Readings": "absorbance_raw",
            }
        )
        .replace(" ", None)
        .reset_index(drop=True)
    )
    data["sample_name"] = data.sample_name.ffill()
    return data
