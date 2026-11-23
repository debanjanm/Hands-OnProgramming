import pathlib
from collections import Counter

import pytest

from conftest import ROOT, normalise, parse_header, run_query

DATASETS = ROOT / "datasets"


def load(problem, folder):
    path = ROOT / folder / problem
    return parse_header(path.read_text()) if path.exists() else ({}, "")


def test_your_answer_matches_the_solution(problem, use_solutions):
    dataset = problem.split("/")[0]
    dataset_sql = (DATASETS / f"{dataset}.sql").read_text()
    sol_meta, sol_query = load(problem, "solutions")
    ans_meta, ans_query = load(problem, "solutions" if use_solutions else "problems")
    meta = ans_meta or sol_meta

    if not ans_query.strip():
        pytest.fail(f"no query written yet.\nTask: {meta.get('task', '')}\nHint: {meta.get('hint', '')}")

    expected_cols, expected = run_query(dataset_sql, sol_query)
    got_cols, got = run_query(dataset_sql, ans_query)

    assert got is not None, "your query did not return any rows/columns (is it a SELECT?)"
    assert len(got_cols) == len(expected_cols), (
        f"expected {len(expected_cols)} columns {expected_cols}, you returned {len(got_cols)} {got_cols}")
    expected, got = normalise(expected), normalise(got)
    if sol_meta.get("ordered", "no").lower().startswith("y"):
        assert got == expected, f"rows (order matters here).\nexpected: {expected[:8]}\n     got: {got[:8]}"
    else:
        assert Counter(got) == Counter(expected), (
            f"same rows expected (any order).\nexpected: {sorted(expected, key=repr)[:8]}\n     got: {sorted(got, key=repr)[:8]}")


def test_solution_is_meaningful_and_stable(problem):
    """Guards the problem set itself: a solution must return rows, deterministically, and carry its metadata."""
    dataset = problem.split("/")[0]
    dataset_sql = (DATASETS / f"{dataset}.sql").read_text()
    meta, query = load(problem, "solutions")
    for key in ("title", "level", "task"):
        assert meta.get(key), f"{problem}: missing '-- {key.title()}:' header"
    assert meta["level"].lower() in {"easy", "medium", "hard"}
    cols, rows = run_query(dataset_sql, query)
    assert rows, f"{problem}: the solution returns no rows"
    assert normalise(rows) == normalise(run_query(dataset_sql, query)[1]) or meta.get("ordered", "no").lower().startswith("n")
    stub_meta, stub_query = load(problem, "problems")
    assert (ROOT / "problems" / problem).exists(), f"{problem}: missing starter file in problems/"
    assert stub_meta.get("title") == meta["title"], f"{problem}: starter header differs from the solution"
