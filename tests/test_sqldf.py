import operator

import pytest
import pandas as pd

from sqldf import __version__, sqldf


@pytest.fixture(scope="session")
def df():
    return pd.DataFrame([{"a": 1.0, "b": "c"}, {"a": 2.0, "b": "d"}])


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

@pytest.mark.parametrize("sql_op,df_op", [
    ("=", operator.eq),
    ("!=", operator.ne),
    ("<", operator.lt),
    ("<=", operator.le),
    (">", operator.gt),
    (">=", operator.ge),
])
def test_where_equals(df, sql_op, df_op):
    result = sqldf.apply_sql(df, f"SELECT * WHERE a {sql_op} 1")
    expected = df[df_op(df.a, 1)]
    assert result.equals(expected)

def test_where_in(df):
    result = sqldf.apply_sql(df, f"SELECT * WHERE b IN ('c', 'd')")
    assert result.equals(df)

def test_where_not_in(df):
    result = sqldf.apply_sql(df, "SELECT * WHERE a NOT IN (1)")
    expected = df[~df.a.isin([1.0])]
    assert result.equals(expected)
