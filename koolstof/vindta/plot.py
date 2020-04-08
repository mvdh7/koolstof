"""Make figures to assist calibration and QC of VINDTA datasets."""
from numpy import timedelta64

def increments(ax, dbs, logfile):
    """Plot coulometer increments by the minute, focussing on the tails."""
    fymax = 1.0
    for i in dbs.logfile_iloc.values:
        ax.plot('minutes', 'increments', data=logfile.table[i], c='xkcd:navy',
                alpha=0.25)
        fymax = max([fymax, max(logfile.table[i]['increments'][-3:])])
    ax.set_xlim([0, dbs['run time'].max()])
    ax.set_ylim([0, fymax*1.25])
    ax.set_xlabel('Run time / minutes')
    ax.set_ylabel('Increments / per minute')
    return ax

def blanks(ax, dbs):
    """Plot sample-by-sample blank values."""
    assert 'blank_here' in dbs.columns, \
        'You must first run `ks.vindta.get_blanks()`.'
    dbs.plot.scatter('analysisdate', 'blank_here', ax=ax)
    ax.set_xlim([min(dbs.analysisdate) - timedelta64(3, 'h'),
                 max(dbs.analysisdate) + timedelta64(3, 'h')])
