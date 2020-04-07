"""Import and parse the data files produced by the Marianda VINDTA 3C."""

import numpy as np
import pandas as pd

def read_dbs(filepath):
    """Import a .dbs file as a DataFrame."""
    headers = np.genfromtxt(filepath, delimiter='\t', dtype=str, max_rows=1)
    return pd.read_table(filepath, header=0, names=headers, usecols=headers)

def addfunccols(df, func):
    """Add results of `apply()` to a DataFrame as new columns."""
    return pd.concat([df, df.apply(func, axis=1)], axis=1, sort=False)
