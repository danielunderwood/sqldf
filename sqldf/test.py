from io import StringIO

import pandas as pd
from pegen.tokenizer import Tokenizer, tokenize

from parser import GeneratedParser as SqlParser


def parse(sql):
    # generate_tokens particularly wants a readline method reference,
    # so we can use StringIO here to get that interface
    statement = StringIO(sql)
    tokengen = tokenize.generate_tokens(statement.readline)
    t = Tokenizer(tokengen)
    p = SqlParser(t)
    return p.start()


if __name__ == "__main__":
    iris = pd.read_csv(
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    )
    parsed = parse("SELECT sepal_length, species, 1")
    reduced = iris.get([c["column"] for c in parsed if "column" in c])
    for i, const in enumerate([c["const"] for c in parsed if "const" in c]):
        reduced[f"const{i}"] = const
    print(reduced)
