import numpy as np
import pandas as pd
from . import oxygen


def pH_NIOZ(
    absorbance_578nm, absorbance_434nm, absorbance_730nm, temperature=25, salinity=35
):
    """Calculate pH from NIOZ spectrophotometer absorbances.

    Parameters
    ----------
    absorbance_578nm : array_like
        Absorbance at 578 nm.
    absorbance_434nm : array_like
        Absorbance at 434 nm.
    absorbance_730nm : array_like
        Absorbance at 730 nm.
    temperature : array_like, optional
        Temperature in °C, by default 25.
    salinity : array_like, optional
        Practical salinity, by default 35.

    Returns
    -------
    array_like
        pH on the total scale.
    """
    WL1 = absorbance_578nm
    WL2 = absorbance_434nm
    WL3 = absorbance_730nm
    pH_total = (
        np.log10(
            (((WL1 - WL3) / (WL2 - WL3) - 0.00815 * WL1) - 0.00691)
            / (2.222 - ((WL1 - WL3) / (WL2 - WL3) - 0.00815 * WL1) * 0.1331)
        )
        + 1245.69 / (temperature + 273.15)
        + 3.8275
        + 0.00211 * (35 - salinity)
    )
    return pH_total


def pH_DSC07(
    absorbance_578nm,
    absorbance_434nm,
    absorbance_730nm,
    temperature=25,
    salinity=35,
    dye_intercept=0,
    dye_slope=1,
):
    """Calculate pH following SOP 6b, including dye addition correction if known.

    Parameters
    ----------
    absorbance_578nm : array_like
        Absorbance at 578 nm.
    absorbance_434nm : array_like
        Absorbance at 434 nm.
    absorbance_730nm : array_like
        Absorbance at 730 nm.
    temperature : array_like, optional
        Temperature in °C, by default 25.
    salinity : array_like, optional
        Practical salinity, by default 35.
    dye_intercept : array_like, optional
        Intercept of the dye correction (SOP 6b eq. 9), by default 0.
    dye_slope : array_like, optional
        Slope of the dye correction (SOP 6b eq. 9), by default 1.

    Returns
    -------
    array_like
        pH on the total scale.
    """
    WL1 = absorbance_578nm
    WL2 = absorbance_434nm
    WL3 = absorbance_730nm
    ratio_raw = (WL1 - WL3) / (WL2 - WL3)
    ratio = ratio_raw - (dye_intercept + dye_slope * ratio_raw)
    pH_total = (
        np.log10((ratio - 0.00691) / (2.222 - ratio * 0.1331))
        + 1245.69 / (temperature + 273.15)
        + 3.8275
        + 0.00211 * (35 - salinity)
    )
    return pH_total


def read_agilent_pH(filename):
    with open(filename, "rb") as f:
        lines = f.read().decode("utf-16").splitlines()

    # Get positions of data tables
    is_table = False
    table_start = []
    table_end = []
    tables = []
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            table_start.append(i)
            is_table = True
        if is_table and line.strip() == "":
            table_end.append(i)
            is_table = False

    # Import data tables
    pH_renamer = {
        "#": "order",
        "Name": "sample_name",
        "Dilut. Factor": "dilution_factor",
        "Weight(25)": "temperature",
        "Volume(35)": "salinity",
        "pH": "pH_instrument",
        "Abs<578nm>": "abs578",
        "Abs<434nm>": "abs434",
        "Abs<730nm>": "abs730",
    }
    ts = table_start[0]
    te = table_end[0]
    pH_a = (
        pd.read_fwf(
            filename,
            encoding="utf-16",
            engine="python",
            skiprows=[*range(ts), ts + 1],
            skipfooter=len(lines) - te,
            widths=[11, 17, 15, 13, 13, 13, 14],
        )
        .rename(columns=pH_renamer)
        .set_index("order")
    )
    pH_a["sample_name"] = pH_a.sample_name.where(pH_a.sample_name.notnull(), "")
    ts = table_start[1]
    te = table_end[1]
    pH_b = (
        pd.read_fwf(
            filename,
            encoding="utf-16",
            engine="python",
            skiprows=[*range(ts), ts + 1],
            skipfooter=len(lines) - te,
            widths=[11, 17, 15, 14],
        )
        .rename(columns=pH_renamer)
        .set_index("order")
    )
    pH_b["sample_name"] = pH_b.sample_name.where(pH_b.sample_name.notnull(), "")
    for k, v in pH_b.items():
        if k == "sample_name":
            assert (pH_a.sample_name == v).all()
        else:
            pH_a[k] = v

    #  Import comments file to get non-truncated sample_name
    with open(filename.replace(".TXT", "-COMMENTS.TXT"), "rb") as f:
        lines = f.read().decode("utf-16").splitlines()

    # Get positions of data tables
    is_table = False
    table_start = []
    table_end = []
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            table_start.append(i)
            is_table = True
        if is_table and line.strip() == "":
            table_end.append(i)
            is_table = False

    # Import middle table
    ts = table_start[1]
    te = table_end[1]
    pH_c = (
        pd.read_fwf(
            filename.replace(".TXT", "-COMMENTS.TXT"),
            encoding="utf-16",
            engine="python",
            skiprows=[*range(ts), ts + 1],
            skipfooter=len(lines) - te,
            widths=[11, 23],
        )
        .rename(columns=pH_renamer)
        .set_index("order")
    )
    pH_c["sample_name"] = pH_c.sample_name.where(pH_c.sample_name.notnull(), "")

    # Update sample_name and append
    for i, row in pH_a.iterrows():
        assert pH_c.sample_name.loc[i].startswith(row.sample_name)
    pH_a["sample_name"] = pH_c.sample_name
    pH_a["file"] = filename
    return pH_a
