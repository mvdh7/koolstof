# koolstof

[![PyPI version](https://badge.fury.io/py/koolstof.svg)](https://badge.fury.io/py/koolstof)

Miscellaneous tools for marine carbonate chemistry.

**Install:**

    pip install koolstof

**Import:**

```python
import koolstof as ks
```

## ks.vindta

Import and parse the data files produced by the [Marianda VINDTA 3C](http://www.marianda.com/index.php?site=products&subsite=vindta3c).

**This module is totally unofficial and in no way endorsed by Marianda!**

### vindta.read_dbs

Import a VINDTA .dbs file as a [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).

```python
dbs = ks.vindta.read_dbs(filepath)
```

### vindta.addfunccols

Append new columns to a [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) `df` containing the results of `df.apply(func)`.

```python
df = ks.vindta.addfunccols(df, func)
```

### vindta.read_logfile

Import a VINDTA logfile.bak as a [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).

```python
logfile = ks.vindta.read_logfile(filepath, methods=['3C standard'])
```

Optional input `methods` allows you to specify your own set of method file names that should be treated as DIC samples, as a list of strings excluding the .mth extension.
