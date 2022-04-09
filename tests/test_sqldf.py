import operator

import pytest
import pandas as pd

from sqldf import __version__, sqldf


@pytest.fixture(scope="session")
def df():
    return pd.DataFrame([{"a": 1.0, "b": "c"}, {"a": 2.0, "b": "d"}])


@pytest.mark.parametrize("kw", ["SELECT", "select"])
def test_select_all(df, kw):
    result = sqldf.query_df(df, f"{kw} *")
    assert result.equals(df)


@pytest.mark.parametrize("kw", ["SELECT", "select"])
def test_select_constant(df, kw):
    result = sqldf.query_df(df, f"{kw} 1")
    assert result.equals(pd.DataFrame([{"const0": 1.0}] * len(df)))


@pytest.mark.parametrize("kw", ["SELECT", "select"])
def test_select_column(df, kw):
    result = sqldf.query_df(df, f"{kw} a")
    # FIXME For some reason .get(["a"]) works here but not just a plain ["a"] index
    assert result.equals(df.get(["a"]))


@pytest.mark.parametrize("kw", ["SELECT", "select"])
def test_select_multi_column(df, kw):
    result = sqldf.query_df(df, f"{kw} a, b")
    assert result.equals(df)


@pytest.mark.parametrize("kw", ["SELECT", "select"])
def test_select_column_constant(df, kw):
    result = sqldf.query_df(df, f"{kw} a, 1")
    expected = df.get(["a"]).copy()
    expected["const0"] = 1.0
    assert result.equals(expected)


@pytest.mark.parametrize("select_kw", ["SELECT", "select"])
@pytest.mark.parametrize("where_kw", ["WHERE", "where"])
@pytest.mark.parametrize(
    "sql_op,df_op",
    [
        ("=", operator.eq),
        ("!=", operator.ne),
        ("<", operator.lt),
        ("<=", operator.le),
        (">", operator.gt),
        (">=", operator.ge),
    ],
)
def test_where_equals(df, sql_op, df_op, select_kw, where_kw):
    result = sqldf.query_df(df, f"{select_kw} * {where_kw} a {sql_op} 1")
    expected = df[df_op(df.a, 1)]
    assert result.equals(expected)


@pytest.mark.parametrize("select_kw", ["SELECT", "select"])
@pytest.mark.parametrize("where_kw", ["WHERE", "where"])
def test_where_in(df, select_kw, where_kw):
    result = sqldf.query_df(df, f"{select_kw} * {where_kw} b IN ('c', 'd')")
    assert result.equals(df)


@pytest.mark.parametrize("select_kw", ["SELECT", "select"])
@pytest.mark.parametrize("where_kw", ["WHERE", "where"])
def test_where_not_in(df, select_kw, where_kw):
    result = sqldf.query_df(df, f"{select_kw} * {where_kw} a NOT IN (1)")
    expected = df[~df.a.isin([1.0])]
    assert result.equals(expected)
