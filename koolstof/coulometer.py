import pandas as pd


def read_coulometer(filename):
    """Import data from Bob's coulometer.

    Parameters
    ----------
    filename : str
        The name (and path) of the file to import.

    Returns
    -------
    pd.DataFrame
        The imported file with samples identified by "number".
    """
    # Import text file and rename columns
    dic = pd.read_csv(filename).rename(
        columns={
            "Time": "datetime",
            "    Cnts": "counts",
            "    Cell_%T": "transmission",
            " Cell_mA": "current",
            " Cell_Temp": "temperature",
            " Cell_ON": "state",
            " Titrate": "titrate",
        }
    )
    dic["datetime"] = pd.to_datetime(dic.datetime)
    # Identify samples
    dic["number"] = (dic.counts < dic.counts.shift()).cumsum()
    return dic


def _get_samples(group):
    row = {}
    row["datetime_start"] = group.datetime.iloc[0]
    row["datetime_end"] = group.datetime.iloc[-1]
    row["counts"] = group.counts.iloc[-1]
    if row["counts"] != group.counts.max():
        print("WARNING! Final counts is not the greatest for the sample.")
    row["temperature_mean"] = group.temperature.mean()
    return pd.Series(row)


def get_samples(dic):
    """Get table of individual samples from imported coulometer file.

    Parameters
    ----------
    dic : pd.DataFrame
        Coulometer dataset imported with ``get_coulometer``.

    Returns
    -------
    pd.DataFrame
        Table with one row per sample.

    """
    return dic.groupby("number").apply(_get_samples)
