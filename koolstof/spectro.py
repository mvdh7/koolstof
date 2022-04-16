import numpy as np


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
