import koolstof as ks, pandas as pd

# Import files
spreadsheet = "tests/data/test_airica/storage_test_Sept21.xlsx"
dbs_filepath = "tests/data/test_airica/LD_storage_test.dbs"


def test_airica():
    """Does ks.airica.process_airica() return a Pandas DataFrame?"""
    database = ks.airica.process_airica(2009.48,
                                        spreadsheet,
                                        dbs_filepath)
    assert isinstance(database, pd.DataFrame)


df = ks.airica.process_airica(2009.48,
                              spreadsheet,
                              dbs_filepath)

def test_airica_assertions():
    assert isinstance(df, pd.DataFrame)
    assert hasattr(df, "a_3")
    assert hasattr(df, "a_4")
    assert hasattr(df, "b_3")
    assert hasattr(df, "b_4")
    assert hasattr(df, "TCO2_3")
    assert hasattr(df, "TCO2_4")

# test_airica()
# test_airica_assertions()
