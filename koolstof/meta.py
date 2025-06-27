import textwrap


__version__ = "1.0.0-b.3"
__author__ = "Humphreys, Matthew P."


def hello():
    greeting = textwrap.dedent(
        r"""
        k  Dissolved inorganic carbon
        o  measurement processing
        o  
        l  
        s  Version {}
        t  doi:10.5281/zenodo.3999292
        o  
        f  https://koolstof.hseao3.group
        """.format(__version__)
    )
    print(greeting)
