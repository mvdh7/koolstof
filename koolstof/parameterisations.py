import numpy as np


def aou_GG92(oxygen=None, temperature=25, salinity=35):
    """AOU and saturated O2 from temperature and salinity in umol/kg-sw.
    Based on Garcia & Gordon (1992), 'combined-fit' constants.
    """
    A0 = 5.80818
    A1 = 3.20684
    A2 = 4.11890
    A3 = 4.93845
    A4 = 1.01567
    A5 = 1.41575
    B0 = -0.00701211
    B1 = -0.00725958
    B2 = -0.00793334
    B3 = -0.00554491
    C0 = -0.000000132412
    # Scaled temperature
    ts = np.log((298.15 - temperature) / (273.15 + temperature))
    # Calculate saturated oxygen <o2s>
    o2_saturation = np.exp(
        A0
        + A1 * ts
        + A2 * ts ** 2
        + A3 * ts ** 3
        + A4 * ts ** 4
        + A5 * ts ** 5
        + salinity * (B0 + B1 * ts + B2 * ts ** 2 + B3 * ts ** 3)
        + C0 * salinity ** 2
    )
    # Calculate AOU
    if oxygen is not None:
        aou = o2_saturation - oxygen
        aou_percent = 100 * aou / o2_saturation
    else:
        aou = aou_percent = np.nan
    return aou, aou_percent, o2_saturation
