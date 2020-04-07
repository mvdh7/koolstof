"""Import and parse the data files produced by the Marianda VINDTA 3C."""

from numpy import genfromtxt
from pandas import read_table

def read_dbs(filepath):
    """Import a .dbs file as a DataFrame."""
    headers = genfromtxt(filepath, delimiter='\t', dtype=str, max_rows=1)
    return read_table(filepath, header=0, names=headers, usecols=headers)
