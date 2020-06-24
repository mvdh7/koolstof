import numpy as np


def pH_NIOZ(
    absorbance_578nm, absorbance_434nm, absorbance_730nm, temperature=25, salinity=35
):
    """Calculate pH from NIOZ spectrophotometer absorbances."""
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
