import numpy as np
from koolstof import quaatro as ksq


def test_pH_of_analysis():
    """Does the pH_of_analysis function return the correct types of results?
    Values are not checked.
    """
    # Scalar arg
    pH, pct = ksq.pH_of_analysis(2300)
    assert isinstance(pH, float)
    assert isinstance(pct, float)
    # Array arg
    pH_arr, pct_arr = ksq.pH_of_analysis(np.array([2000, 2500, 3000]))
    assert isinstance(pH_arr, np.ndarray)
    assert isinstance(pct_arr, np.ndarray)
    assert pH > np.min(pH_arr)
    assert pH < np.max(pH_arr)
    assert pct > np.min(pct_arr)
    assert pct < np.max(pct_arr)
    # Scalar arg with kwargs
    pH_kws, pct_kws = ksq.pH_of_analysis(
        2300,
        pk_HCOOH=3.43,
        pk_BPhB=3.86,
        ratio_reagent=827,
        ratio_sample=381,
        stock_BPhB_vol=50,
        stock_HCOOH_vol=50,
        temperature=20,
        salinity=30,
        total_phosphate=10,
        total_silicate=50,
    )
    assert isinstance(pH_kws, float)
    assert isinstance(pct_kws, float)


# test_pH_of_analysis()
