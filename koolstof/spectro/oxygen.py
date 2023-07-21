import pandas as pd
import numpy as np


def read_cary_oxygen(filename):
    """Import oxygen data from Agilent Cary spectrophotometer report.

    Parameters
    ----------
    filename : str
        The file name (and path) for the .csv report.

    Returns
    -------
    pd.DataFrame
        The data from the file parsed into a pandas DataFrame.
    """

    with open(filename, "r") as f:
        lines = f.read().splitlines()

    data_line = False
    oxy = {"name": [], "repeat": []}
    reps = ["r{}".format(r) for r in range(1, 6)]
    oxy.update({rep: [] for rep in reps})
    repeat = (
        0  # increments to 1 for any repeated measurements at end of first run through
    )
    for line in lines:
        # Parse date and time of analysis
        if line.startswith("Collection time"):
            mm, dd, yyyy = line.split()[2].split("/")
            HH, MM, SS = line.split()[3].split(":")
            if line.split()[4] == "PM" and HH != "12":
                HH = int(HH) + 12
            datetime_analysis = np.datetime64(
                "{:04.0f}-{:02.0f}-{:02.0f}T{:02.0f}:{:02.0f}:{:02.0f}".format(
                    int(yyyy), int(mm), int(dd), int(HH), int(MM), int(SS)
                )
            )

        # Get zero value
        if line.startswith("Zero") and not line == "Zero Report":
            zero = float(line.split()[1])

        # If this line is seen, we've reached the end of the data section:
        if line == "Results Flags Legend":
            data_line = False

        # Parse the data section here
        if data_line:
            line_split = line.split()
            # The "+ repeat" in this section deals with the fact that there is an extra
            # column containing "R" in the tables for repeated measurements
            assert len(line_split) in np.array([1, 2, 4]) + repeat
            if len(line_split) == 2 + repeat:  # first measurement for a new sample
                oxy["name"].append(line_split[0])
                oxy["repeat"].append(repeat > 0)
                oxy["r1"].append(float(line_split[1 + repeat]))
                r = 2
            elif len(line_split) == 1 + repeat:  # intermediate measurements
                oxy["r{}".format(r)].append(float(line_split[0 + repeat]))
                r += 1
            elif len(line_split) == 4 + repeat:  # final measurement and statistics
                oxy["r{}".format(r)].append(float(line_split[3 + repeat]))

        # If this line is seen, we're about to start the data section:
        if line == "Sample	F	Mean	SD	%RSD	Readings":
            data_line = True

        if line.startswith("R = Repeat reading"):
            repeat = 1

    # Convert to DataFrame and calculate statistics and other things
    oxy = pd.DataFrame(oxy)
    oxy["absorbance_raw"] = oxy[reps].mean(axis=1)
    oxy["absorbance_std"] = oxy[reps].std(axis=1)
    oxy["mq"] = oxy.name.str.startswith("MQ")
    oxy["zero"] = zero

    return oxy
