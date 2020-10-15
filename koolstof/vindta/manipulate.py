import pandas as pd
from . import Dbs


def concat(objs, logfile=None, **kwargs):
    """Concatenate imported .dbs files, before determining sessions."""
    obj = pd.concat(objs, **kwargs)
    obj.reset_index(drop=True, inplace=True)
    obj = Dbs(obj)
    obj.logfile = logfile
    return obj
