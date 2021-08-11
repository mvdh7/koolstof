import koolstof as ks, pandas as pd

# Import files
spreadsheet_path = "tests/data/test_optode/spreadsheet.xlsx"
text_files_folder_path = "tests/data/test_optode"


def test_pH_optode():
    """Does ks.pH_optode() return a Pandas DataFrame?"""
    database = ks.pH_optode(spreadsheet_path, text_files_folder_path)
    assert isinstance(database, pd.DataFrame)


df = ks.pH_optode(spreadsheet_path, text_files_folder_path)


def test_optode_assertions():
    assert isinstance(df, pd.DataFrame)
    assert hasattr(df, "pH_NBS")
    assert hasattr(df, "filename")


# test_pH_optode()
# test_optode_assertions()
