"""Certified reference material (CRM) data."""

import numpy as np


class ReferenceMaterial:
    """A generic reference material."""

    def __init__(self, **kwargs):
        assert all(
            [
                key
                in [
                    "batch",
                    "salinity",
                    "dissolved_inorganic_carbon",
                    "dissolved_inorganic_carbon_std",
                    "total_alkalinity",
                    "total_alkalinity_std",
                    "phosphate",
                    "silicate",
                    "nitrite",
                    "nitrate",
                ]
                for key in kwargs
            ]
        )
        self.__dict__.update((k, v) for k, v in kwargs.items())


dickson_certified_values = {
    171: ReferenceMaterial(
        batch=171,
        salinity=33.434,
        dissolved_inorganic_carbon=2029.19,
        dissolved_inorganic_carbon_std=0.87,
        total_alkalinity=2217.40,
        total_alkalinity_std=0.63,
        phosphate=0.43,
        silicate=2.3,
        nitrite=0.00,
        nitrate=3.1,
    ),
    186: ReferenceMaterial(
        batch=186,
        salinity=33.525,
        dissolved_inorganic_carbon=2012.59,
        dissolved_inorganic_carbon_std=0.80,
        total_alkalinity=2212.00,
        total_alkalinity_std=0.53,
        phosphate=0.42,
        silicate=3.3,
        nitrite=0.01,
        nitrate=2.8,
    ),
}


def dickson(crm_batches, fields):
    """Dickson seawater certified reference material."""
    if isinstance(fields, str):
        if fields == "all":
            fields = [
                "batch",
                "salinity",
                "dissolved_inorganic_carbon",
                "dissolved_inorganic_carbon_std",
                "total_alkalinity",
                "total_alkalinity_std",
                "phosphate",
                "silicate",
                "nitrite",
                "nitrate",
            ]
        else:
            fields = [fields]
    return {
        field: np.array(
            [
                dickson_certified_values[crm_batch].__dict__[field]
                if crm_batch in dickson_certified_values
                else np.nan
                for crm_batch in crm_batches
            ]
        )
        for field in fields
    }


def dic_calibration_factor(
    data=None,
    dic_certified="dic_certified",
    density_analysis="density_analysis",
    counts_corrected="counts_corrected",
):
    """Calculate volume-cancelling DIC calibration factor."""
    if data is not None:
        dic_certified = data[dic_certified]
        density_analysis = data[density_analysis]
        counts_corrected = data[counts_corrected]
    return dic_certified * density_analysis / counts_corrected


def calibrate_dic(
    data=None,
    calibration_factor="dic_calibration_factor",
    counts_corrected="counts_corrected",
    density_analysis="density_analysis",
):
    """Apply volume-cancelling DIC calibration factor."""
    if data is not None:
        calibration_factor = data[calibration_factor]
        counts_corrected = data[counts_corrected]
        density_analysis = data[density_analysis]
    return calibration_factor * counts_corrected / density_analysis
