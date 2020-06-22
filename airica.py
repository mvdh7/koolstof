import pandas as pd

data = pd.read_table("data/Humphreys_peakform_00.txt", header=1)
data.plot("Time", "CO2B um/m")
