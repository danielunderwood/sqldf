# sqldf

[![Tests](https://github.com/danielunderwood/sqldf/actions/workflows/test.yml/badge.svg)](https://github.com/danielunderwood/sqldf/actions/workflows/test.yml)

Ever wish you could query pandas DataFrames with SQL like this?

```python
df = pd.DataFrame(...)
sqldf.query_df(df, """
SELECT *, sum(b)
WHERE a > 5
GROUP BY b
""")
```

Well now you can with sqldf!

## Currently Supported

- `SELECT`
- `WHERE`
  - `=`, `!=`, `>`, `>=`, `<`, `<=`, `IN`, `NOT IN`

## Not (Yet) Supported

- `SELECT ... AS`
- `FROM`
- `GROUP BY`
- `JOIN`
- `WHERE ... LIKE`
- `ORDER BY`

## How it Works

A PEG grammar is defined in [`sqldf/sql.gram`](./sqldf/sql.gram) that is passed through [pegen](https://github.com/we-like-parsers/pegen) to generate the parser in [`sqldf/parser.py`](./sqldf/parser.py) that parses the SQL and generates objects (currently dictionaries). The generated objects are then processed to build up the relevant pandas calls to return the processed DataFrame.
