import pytest
import pandas as pd

from sqldf import __version__, sqldf

@pytest.fixture(scope="session")
def df():
    return pd.DataFrame([{'a': 1, 'b': 'c'}, {'a': 2, 'b': 'd'}])

def test_version():
    assert __version__ == '0.1.0'

def test_select_all(df):
    result = sqldf.apply_sql(df, "SELECT *")
    assert result.equals(df)

def test_select_constant(df):
    result = sqldf.apply_sql(df, "SELECT 1")
    assert result.equals(pd.DataFrame([{"const0": 1.0}] * len(df)))

def test_select_column(df):
    result = sqldf.apply_sql(df, "SELECT a")
    # FIXME For some reason .get(["a"]) works here but not just a plain ["a"] index
    assert result.equals(df.get(["a"]))

def test_select_multi_column(df):
    result = sqldf.apply_sql(df, "SELECT a, b")
    assert result.equals(df)

def test_select_column_constant(df):
    result = sqldf.apply_sql(df, "SELECT a, 1")
    expected = df.get(["a"]).copy()
    expected["const0"] = 1.0
    assert result.equals(expected)