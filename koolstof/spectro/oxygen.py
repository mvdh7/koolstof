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
    zero = []
    started = False
    for i, line in enumerate(lines):
        if line == "Sample\tF\tMean\tSD\t%RSD\tReadings":
            data_start.append(i)
            started = True
        elif line == "Results Flags Legend":
            # Only add an end line if we have started a new sample since the last end
            # line, because sometimes the "Results Flags Legend" line appears twice
            if started:
                data_end.append(i)
                started = False
        elif line.startswith("Zero") and not line == "Zero Report":
            zero.append(float(line.split()[1]))
    # Sometimes the "Results Flags Legend" line doesn't appear at the very end of the
    # file, so add an extra endpoint manually here if that's the case
    if started:
        data_end.append(len(lines))
    data = []
    if not len(data_start) == len(data_end) == len(zero):
        print(
            "WARNING: there are different numbers of data "
            + "start ({}), end ({}) and zero ({}) points".format(
                len(data_start), len(data_end), len(zero)
            )
        )
        print("for file {}".format(filename))
    for start, end, z in zip(data_start, data_end, zero):
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
        data_["zero"] = z
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
