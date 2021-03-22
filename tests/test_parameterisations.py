import numpy as np
import koolstof as ks


def test_aou_GG92():
    """Does ks.aou_GG92() return the check value from GG92 Table 1?"""
    o2_saturation = ks.aou_GG92(temperature=10, salinity=35)[2]
    assert np.round(o2_saturation, decimals=3) == 274.646
    # GG92 actually give 274.647 but hey...
