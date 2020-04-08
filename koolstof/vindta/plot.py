"""Make figures to assist calibration and QC of VINDTA datasets."""
from numpy import timedelta64
import matplotlib.dates as mdates

def increments(ax, dbs, logfile, c='xkcd:navy', alpha=0.25, **kwargs):
    """Plot coulometer increments by the minute, focussing on the tails.
    Any additional `kwargs` are passed to `plt.plot()`.
    """
    assert 'logfile_iloc' in dbs.columns, \
        'You must first run `ks.vindta.logfile2dbs()`.'
    fymax = 1.0
    for i in dbs.logfile_iloc.values:
        ax.plot('minutes', 'increments', data=logfile.table[i], c=c,
                alpha=alpha, )
        fymax = max([fymax, max(logfile.table[i]['increments'][-3:])])
    ax.set_xlim([0, dbs['run time'].max()])
    ax.set_ylim([0, fymax*1.25])
    ax.set_xlabel('Run time / minutes')
    ax.set_ylabel('Increments / per minute')
    return ax

def blanks(ax, dbs, c='xkcd:navy', alpha=0.5, **kwargs):
    """Plot sample-by-sample blank values.
    Any additional `kwargs` are passed to `plt.scatter()`.
    """
    assert 'blank_here' in dbs.columns, \
        'You must first run `ks.vindta.get_blanks()`.'
    dbs.plot.scatter('analysisdate', 'blank_here', ax=ax, c=c, alpha=alpha,
                     **kwargs)
    ax.set_xlim([min(dbs.analysisdate) - timedelta64(3, 'h'),
                 max(dbs.analysisdate) + timedelta64(3, 'h')])
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax.set_xlabel('Day of month')
    ax.set_ylim([0, max(dbs.blank_here)*1.05])
    ax.set_ylabel('Sample-by-sample blank')
    return ax
