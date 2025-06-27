def poison_correction(var, sample_volume, poison_volume):
    """Apply dilution correction to var for added poison."""
    return var * (1 + poison_volume / sample_volume)
