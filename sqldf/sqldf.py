import operator
import sys
from io import StringIO

import pandas as pd
from pegen.tokenizer import Tokenizer, tokenize

try:
    from .parser import GeneratedParser as SqlParser
except ImportError:
    from parser import GeneratedParser as SqlParser

OP_MAPPING = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "=": operator.eq,
    "!=": operator.ne,
}

OP_FUNCS = {
    symbol: (lambda df, col, value: op(df[col], value))
    for symbol, op in OP_MAPPING.items()
}

# IN needs to be specialized to use isin
OP_FUNCS["IN"] = lambda df, col, values: df[col].isin(values)
OP_FUNCS["NOT IN"] = lambda df, col, values: ~df[col].isin(values)

# FIXME I have no idea why, but these don't work just from the comprehension
# != and > work because ???
OP_FUNCS["<"] = lambda df, col, value: OP_MAPPING["<"](df[col], value)
OP_FUNCS["<="] = lambda df, col, value: OP_MAPPING["<="](df[col], value)
OP_FUNCS[">="] = lambda df, col, value: OP_MAPPING[">="](df[col], value)
OP_FUNCS["="] = lambda df, col, value: OP_MAPPING["="](df[col], value)


def parse(sql):
    # generate_tokens particularly wants a readline method reference,
    # so we can use StringIO here to get that interface
    statement = StringIO(sql)
    tokengen = tokenize.generate_tokens(statement.readline)
    t = Tokenizer(tokengen)
    p = SqlParser(t)
    return p.start()


def apply_sql(df, sql):
    parsed = parse(sql)
    # TODO Proper logging
    print(parsed)
    columns = [c["column"] for c in parsed[0] if c and "column" in c]
    constants = [c["const"] for c in parsed[0] if c and "const" in c]
    filters = [c["filter"] for c in parsed if c and "filter" in c]
    # If a SELECT * is passed, we just use the original df
    # Note that this may not work exactly if we add alias support and have something like
    # SELECT *, a AS alias, but I don't know if I've ever seen that done in regular SQL
    if "*" in columns:
        reduced = df
    else:
        reduced = df[[c for c in columns if c != "*"]]
    for i, const in enumerate(constants):
        reduced[f"const{i}"] = const

    filter_statement = None
    for f in filters:
        if filter_statement is None:
            # Note that these need to be done on the original dataframe as it's possible
            # to filter on columns that aren't selected
            filter_statement = OP_FUNCS[f["op"]](df, f["column"], f["value"])
        else:
            # TODO OR operations
            filter_statement &= OP_FUNCS[f["op"]](df, f["column"], f["value"])
    # print("Filters", filters)
    # print(filter_statement)
    if filter_statement is not None:
        reduced = reduced[filter_statement]

    return reduced


if __name__ == "__main__":
    iris = pd.read_csv(
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    )
    reduced = apply_sql(iris, sys.argv[1])
    print(reduced)
