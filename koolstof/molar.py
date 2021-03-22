import numpy as np

pm1 = np.array([-1, 1])

# Source: https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl
# Value ranges indicate uncertainty
mass_range = {  # standard atomic weights in g/mol
    "H": np.array([1.007_84, 1.008_11]),
    "B": np.array([10.806, 10.821]),
    "C": np.array([12.009_6, 12.011_6]),
    "N": np.array([14.006_43, 14.007_28]),
    "O": np.array([15.999_03, 15.999_77]),
    "Na": 22.989_769_28 + 0.000_000_02 * pm1,
    "Mg": np.array([24.304, 24.307]),
    "Si": np.array([28.084, 28.086]),
    "P": 30.973_761_998 + 0.000_000_005 * pm1,
    "S": np.array([32.059, 32.076]),
    "Cl": np.array([35.446, 35.457]),
    "K": 39.098_3 + 0.000_1 * pm1,
    "Ca": 40.078 + 0.004 * pm1,
}
mass = {k: np.mean(v) for k, v in mass_range.items()}

# Source: mostly Wikipedia...
mass.update(
    {
        "PO4": 94.9714,
        "SO4": 96.06,
        "O2": 31.999,  # https://pubchem.ncbi.nlm.nih.gov/compound/Oxygen
    }
)
