import koolstof as ks, pandas as pd

# Import files
spreadsheet = 'data/test_optode/spreadsheet.xlsx'
text_files_folder_path = 'data/test_optode'

def test_pH_optode():
    """Does ks.pH_optode() return a Pandas DataFrame?"""
    database = ks.pH_optode(spreadsheet, text_files_folder_path)
    assert isinstance(database, pd.DataFrame)

df = ks.pH_optode(spreadsheet, text_files_folder_path)

def optode_assertions(df):
    assert isinstance(df, pd.DataFrame)
    assert hasattr(df, "pH_s0_mean")
    assert hasattr(df, "filename")
