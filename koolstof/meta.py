import textwrap


__version__ = "1.0.0"
__author__ = "Humphreys, Matthew P."


def hello():
    greeting = textwrap.dedent(
        r"""
        k  Miscellaneous tools for
        o  marine carbonate chemistry
        o  and other such things
        l  
        s  Version {}
        t  doi:10.5281/zenodo.3999292
        o  
        f  https://koolstof.hseao3.group
        """.format(__version__)
    )
    print(greeting)
