"""Import and parse the data files produced by the Marianda VINDTA 3C."""

import re
import numpy as np
import pandas as pd

def read_dbs(filepath):
    """Import a .dbs file as a DataFrame."""
    headers = np.genfromtxt(filepath, delimiter='\t', dtype=str, max_rows=1)
    return pd.read_table(filepath, header=0, names=headers, usecols=headers)

def addfunccols(df, func):
    """Add results of `apply()` to a DataFrame as new columns."""
    return pd.concat([df, df.apply(func, axis=1)], axis=1, sort=False)

def read_logfile(filepath, methods='(3C standard|3C standardRWS)'):
    """Import a logfile.bak as a DataFrame."""
    # Compile regexs for reading logfile
    re_method = re.compile(r'{}\.mth run started '.format(methods))
    re_datetime = re.compile('started (\d{2})/(\d{2})/(\d{2})  (\d{2}):(\d{2})')
    re_bottle = re.compile(r'(bottle)?\t([^\t]*)\t')
    re_crm = re.compile(r'CRM\t([^\t]*)\t')
    re_increments = re.compile(r'(\d*)\t(\d*)\t(\d*)\t')
    # Import text from logfile
    with open(filepath, 'r') as f:
        logf = f.read().splitlines()
    # Initialise arrays
    logdf = {
        'logfileline': [],
        'analysisdate': np.array([], dtype='datetime64'),
        'bottle': [],
        'table': [],
        'totalcounts': [],
        'runtime': [],
    }
    # Parse file line by line
    for i, line in enumerate(logf):
        if re_method.match(line):
            logdf['logfileline'].append(i)
            # Get analysis date and time
            ldt = re_datetime.findall(line)[0]
            ldt = np.datetime64('{}-{}-{}T{}:{}'.format(
                '20'+ldt[2], ldt[0], ldt[1], ldt[3], ldt[4]))
            logdf['analysisdate'] = np.append(logdf['analysisdate'], ldt)
            # Get sample name
            lbot = 0
            if re_bottle.match(logf[i+1]):
                lbot = re_bottle.findall(logf[i+1])[0][1]
            elif re_crm.match(logf[i+1]):
                lbot = re_crm.findall(logf[i+1])[0]
            elif logf[i+1] == 'other':
                lbot = 'other_{}'.format(i+1)
            assert(type(lbot) == str), \
                'Logfile line {}: bottle name not found!'.format(i+1)
            logdf['bottle'].append(lbot)
            # Get coulometer data
            jdict = {'minutes': [0.0], 'counts': [0.0], 'increments': [0.0]}
            j = 4
            while re_increments.match(logf[i+j].strip()):
                jinc = re_increments.findall(logf[i+j].strip())[0]
                jdict['minutes'].append(float(jinc[0]))
                jdict['counts'].append(float(jinc[1]))
                jdict['increments'].append(float(jinc[2]))
                j += 1
            jdict = {k: np.array(v) for k, v in jdict.items()}
            logdf['table'].append(jdict)
            logdf['totalcounts'].append(jdict['counts'][-1])
            logdf['runtime'].append(j - 4.0)
    # Convert lists to arrays and put logfile into DataFrame
    logdf = {k: np.array(v) for k, v in logdf.items()}
    return pd.DataFrame(logdf)
