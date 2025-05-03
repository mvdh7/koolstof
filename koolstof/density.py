import warnings

import numpy as np


def seawater_1atm_MP81(temperature=25, salinity=35):
    """Seawater density at 1 atm in kg/l following MP81.

    Validity:
      *  0 < temperature < 40 °C
      *  0.5 < salinity < 43
    """
    if np.any(temperature < 0) or np.any(temperature > 40):
        warnings.warn(
            "Warning: some temperature values fall outside the valid range"
            + "of the MP81 density equation (0-40 °C)."
        )
    if np.any(salinity < 0.5) or np.any(salinity > 43):
        warnings.warn(
            "Warning: some salinity values fall outside the valid range"
            + "of the MP81 density equation (0.5-43)."
        )
    return (
        999.842594
        + 6.793952e-2 * temperature
        - 9.095290e-3 * temperature**2
        + 1.001685e-4 * temperature**3
        - 1.120083e-6 * temperature**4
        + 6.536336e-9 * temperature**5
        + (
            0.824493
            - 4.0899e-3 * temperature
            + 7.6438e-5 * temperature**2
            - 8.2467e-7 * temperature**3
            + 5.3875e-9 * temperature**4
        )
        * salinity
        + (-5.72466e-3 + 1.0227e-4 * temperature - 1.6546e-6 * temperature**2)
        * salinity**1.5
        + 4.8314e-4 * salinity**2
    ) * 1e-3
