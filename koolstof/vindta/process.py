import numpy as np


def get_data_index(dbs_row, data):
    """Get index of data in dbs to transfer metadata across for processing."""
    if dbs_row.bottle in data.station_bottleid.values:
        data_iloc = np.where(dbs_row.bottle == data.station_bottleid.values)[0]
        assert (
            len(data_iloc) == 1
        ), "Found more than one bottle ID match for {}!".format(dbs_row.bottle)
        data_index = data.index[data_iloc[0]]
    else:
        data_index = np.nan
    return data_index


def dbs2data(dbs, data, fields):
    """Transfer results from dbs into data, taking means for duplicates."""
    if isinstance(fields, str):
        fields = [fields]
    for field in fields:
        data[field] = np.nan
        data[field + "_std"] = np.nan
        data[field + "_count"] = 0
    for row in data.index:
        dr = data.loc[row]
        if dr.station_bottleid in dbs.bottle.values:
            for field in fields:
                dbs_iloc = np.where(
                    (dr.station_bottleid == dbs.bottle.values) & dbs[field + "_good"]
                )[0]
                if np.size(dbs_iloc) > 0:
                    fdata = dbs.iloc[dbs_iloc][field]
                    data.loc[row, field] = np.mean(fdata)
                    if np.size(dbs_iloc) > 1:
                        data.loc[row, field + "_std"] = np.std(fdata)
                    data.loc[row, field + "_count"] = np.size(dbs_iloc)
    return data


def poison_correction(var, sample_volume, poison_volume):
    """Apply dilution correction to var for added poison."""
    return var * (1 + poison_volume / sample_volume)
