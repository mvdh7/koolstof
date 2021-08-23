import PyCO2SYS as pyco2


def pH_of_analysis(
    alkalinity_sample,
    pCO2_lab=500,
    pk_HCOOH=3.43,
    pk_BPhB=3.86,
    ratio_reagent=827,
    ratio_sample=381,
    stock_BPhB_vol=50,
    stock_HCOOH_vol=50,
    **pyco2_kwargs,
):
    """Calculate the pH of the sample-reagent mixture and the fractional abundance of
    the BPhB^2- ion detected at 590 nm during QuAAtro alkalinity analysis with
    bromophenol blue (BPhB) plus formic acid (HCOOH) reagent.

    Parameters
    ----------
    alkalinity_sample : float
        Total alkalinity of the sample in μmol/kg-sample.
    pCO2_lab : float, optional
        Partial pressure of CO2 in the laboratory in μatm. The default is 500.
    pk_HCOOH : float, optional
        pK* of HCOOH. The default is 3.43 [SMP99].
    pk_BPhB : float, optional
        pK* of BPhB^- (second dissociation constant). The default is 3.86 [SMP99].
    ratio_reagent : float, optional
        Relative amount of reagent in the sample-reagent mixture. The default is 827.
    ratio_sample : float, optional
        Relative amount of sample in the sample-reagent mixture. The default is 381.
    stock_BPhB_vol : float, optional
        Volume of 0.5 g/l BPhB per litre of reagent in ml. The default is 50.
    stock_HCOOH_vol : float, optional
        Volume of 0.1 M HCOOH per litre of reagent in ml. The default is 50.
    **pyco2_kwargs
        Additional keyword arguments to pass to PyCO2SYS.

    Returns
    -------
    pH_free : float
        pH of the sample-reagent mixture on the Free scale.
    percent_detected : float
        Percentage of total BPhB in the 2- form measured at 590 nm.
    """

    # Stock solution composition --- HCOOH
    stock_HCOOH_conc = 0.1  # mol/l

    # Stock solution composition --- BPhB
    stock_BPhB_conc_mg = 500  # mg/l
    rmm_BPhB = 669.96  # g/mol
    stock_BPhB_conc = 1e-3 * stock_BPhB_conc_mg / rmm_BPhB  # mol/l

    # Reagent composition
    reagent_vol = 1000  # ml
    reagent_HCOOH = stock_HCOOH_conc * stock_HCOOH_vol / reagent_vol  # mol/l
    reagent_BPhB = stock_BPhB_conc * stock_BPhB_vol / reagent_vol  # mol/l

    # Alkalinity of reagent
    alkalinity_BPhB = -2  # mol/mol --- like H2SO4
    alkalinity_HCOOH = -1  # mol/mol --- like HF
    alkalinity_vol_reagent = (
        reagent_HCOOH * alkalinity_HCOOH + reagent_BPhB * alkalinity_BPhB
    )  # mol/l

    # Alkalinity of sample
    density_sample = 1.03  # kg/l
    alkalinity_vol_sample = 1e-6 * alkalinity_sample * density_sample  # mol/l

    # Alkalinity of sample-reagent mixture
    alkalinity_vol_mixture = (
        (alkalinity_vol_sample * ratio_sample + alkalinity_vol_reagent * ratio_reagent)
        / (ratio_sample + ratio_reagent)
        * 1e6
    )  # umol/l
    density_mixture = 1.02  # kg/l
    alkalinity_mixture = alkalinity_vol_mixture / density_mixture  # umol/kg

    # HCOOH in sample-reagent mixture
    HCOOH_vol_mixture = (
        1e6 * reagent_HCOOH * ratio_reagent / (ratio_sample + ratio_reagent)
    )  # umol/l
    HCOOH_mixture = HCOOH_vol_mixture / density_mixture  # umol/kg

    # BPhB in sample-reagent mixture
    BPhB_vol_mixture = (
        1e6 * reagent_BPhB * ratio_reagent / (ratio_sample + ratio_reagent)
    )  # umol/l
    BPhB_mixture = BPhB_vol_mixture / density_mixture  # umol/kg

    # Dissociation constants for HCOOH and BPhB
    # pk_HCOOH = 3.745  # Wikipedia
    # pk_BPhB = 3.513  # Nand & Ellwood (2018) doi:10.1002/lom3.10253
    k_HCOOH = 10 ** -pk_HCOOH
    k_BPhB = 10 ** -pk_BPhB

    # Dilute other total concentrations
    results_undiluted = pyco2.sys(
        par1=alkalinity_mixture,
        par2=pCO2_lab,
        par1_type=1,
        par2_type=4,
        total_alpha=HCOOH_mixture,
        k_alpha=k_HCOOH,
        total_beta=BPhB_mixture,
        k_beta=k_BPhB,
        **pyco2_kwargs,
    )
    totals_diluted = {
        t: results_undiluted[t] * ratio_sample / (ratio_sample + ratio_reagent)
        for t in [
            "total_sulfate",
            "total_fluoride",
            "total_borate",
            "total_silicate",
            "total_phosphate",
            "total_ammonia",
            "total_sulfide",
        ]
    }
    pyco2_kwargs = {k: v for k, v in pyco2_kwargs.items() if k not in totals_diluted}

    # Solve the sample-reagent mixture
    res = pyco2.sys(
        par1=alkalinity_mixture,
        par2=400,  # assume CO2 degassing to equilibrium with lab air
        par1_type=1,
        par2_type=4,
        total_alpha=HCOOH_mixture,
        k_alpha=k_HCOOH,
        total_beta=BPhB_mixture,
        k_beta=k_BPhB,
        **pyco2_kwargs,
        **totals_diluted,
    )

    # Return results
    pH_free = res["pH_free"]
    percent_detected = 100 * res["beta"] / res["total_beta"]
    return pH_free, percent_detected
