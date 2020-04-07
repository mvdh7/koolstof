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
