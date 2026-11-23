"""Shared pytest setup for the SQL practice problems.

    pytest 11-Practice                 # check YOUR answers (problems/*/*.sql)
    pytest 11-Practice --solutions     # check the reference answers (solutions/*/*.sql)
    pytest 11-Practice -k store        # one dataset;  -k "store and 07" for one problem

A problem file is a .sql file whose leading `-- Key: value` comment lines describe the task
(Title, Level, Task, Hint, Ordered, Columns). Write your query under the comments.
"""
import pathlib
import sqlite3

import pytest

ROOT = pathlib.Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption("--solutions", action="store_true",
                     help="run the reference answers in solutions/ instead of your files in problems/")


def parse_header(text):
    """Return ({key: value}, query_sql) from a problem file."""
    meta, sql_lines, last = {}, [], None
    for line in text.splitlines():
        if line.startswith("--") and not sql_lines:
            body = line[2:].strip()
            if ":" in body and body.split(":", 1)[0].isalpha():
                last, value = body.split(":", 1)
                last = last.strip().lower()
                meta[last] = value.strip()
            elif last and body:
                meta[last] += " " + body
        else:
            sql_lines.append(line)
    return meta, "\n".join(sql_lines).strip()


def statements(sql):
    out, start = [], 0
    for i, ch in enumerate(sql):
        if ch == ";" and sqlite3.complete_statement(sql[start:i + 1]):
            out.append(sql[start:i + 1].strip())
            start = i + 1
    if sql[start:].strip():
        out.append(sql[start:].strip())
    return out


def run_query(dataset_sql, query):
    """Load the dataset into a fresh in-memory database and return (columns, rows) of the last result set."""
    con = sqlite3.connect(":memory:")
    con.executescript(dataset_sql)
    cols, rows = None, None
    for stmt in statements(query):
        cur = con.execute(stmt)
        if cur.description:
            cols, rows = [d[0] for d in cur.description], cur.fetchall()
    con.close()
    return cols, rows


def normalise(rows):
    def fix(v):
        return round(v, 6) if isinstance(v, float) else v
    return [tuple(fix(v) for v in r) for r in rows]


def problem_ids():
    return sorted(p.relative_to(ROOT / "solutions").as_posix() for p in (ROOT / "solutions").glob("*/*.sql"))


def pytest_generate_tests(metafunc):
    if "problem" in metafunc.fixturenames:
        ids = problem_ids()
        metafunc.parametrize("problem", ids, ids=[i.removesuffix(".sql") for i in ids])


@pytest.fixture
def use_solutions(request):
    return request.config.getoption("--solutions")
