"""Import and parse the data files produced by the Marianda VINDTA 3C."""

import textwrap
import pandas as pd
from . import io, plot, process

#  _   _  _  _   _  ___   _____  _____       ___    _
# ( ) ( )(_)( ) ( )(  _`\(_   _)(  _  )    /'___)_ (_ )
# | | | || || `\| || | ) | | |  | (_) |   | (__ (_) | |    __    ___
# | | | || || , ` || | | ) | |  |  _  |   | ,__)| | | |  /'__`\/',__)
# | \_/ || || |`\ || |_) | | |  | | | |   | |   | | | | (  ___/\__, \
# `\___/'(_)(_) (_)(____/' (_)  (_) (_)   (_)   (_)(___)`\____)(____/
#


class Vindta:
    """A combined DIC and alkalinity dataset from a VINDTA."""

    plot_blanks = plot.blanks

    def __init__(
        self,
        fnames_dbs,
        fpath_dbs="",
        fname_logfile="logfile.bak",
        methods="3C standard",
        use_from=6,
    ):
        if isinstance(fnames_dbs, str):
            fnames_dbs = [fnames_dbs]
        assert isinstance(fnames_dbs, list)
        self.logfile = io.read_logfile(fname_logfile, methods=methods)
        self.dbs = pd.concat([io.read_dbs(fpath_dbs + fname) for fname in fnames_dbs])
        self.dbs = io.logfile2dbs(self.dbs, self.logfile)
        self.sessions = self.dbs.groupby(by="cell ID")["cell ID"].agg(count="count")
        self.get_sample_blanks(use_from=use_from)
        print("Next, run Vindta.get_session_blanks().")

    def get_sample_blanks(self, use_from=6):
        """Get sample-by-sample blank values."""
        self.dbs = process.get_sample_blanks(self.dbs, self.logfile, use_from=use_from)

    def get_session_blanks(self, blank_good=None):
        """Get blanks per analysis session."""
        # if blank_good is not None:
        #     self.dbs["blank_good"] = blank_good
        if "blank_good" not in self.dbs:
            self.dbs["blank_good"] = True
        self.sessions = self.sessions.join(
            self.dbs.groupby(by="cell ID").apply(process.get_session_blanks)
        )
