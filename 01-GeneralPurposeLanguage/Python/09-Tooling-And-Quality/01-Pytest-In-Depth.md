# Pytest In Depth — Notes

## What this covers
How to write and run tests with pytest: plain asserts, fixtures, parametrization, built-in helpers, marks, selection flags, mocking, and how to keep tests reliable. The `.py` builds small projects in a temp folder and runs real pytest on them.

## Key points
- **Why pytest over unittest**: plain `assert x == y` (no `self.assertEqual`), failure messages that show both sides plus a diff, fixtures instead of `setUp`/`tearDown`, and it also runs old `unittest.TestCase` tests unchanged.
- **Discovery**: files `test_*.py` or `*_test.py`, functions `test_*`, classes `Test*` with **no `__init__`**. A test passes if it finishes without raising.
- **Exit codes**: `0` all passed, `1` failures, `2` interrupted, `4` usage error, `5` nothing collected.
- **`pytest.raises(Err, match="regex")`** checks an error is raised; `as excinfo` gives `.type` / `.value` (read it after the `with` block).
- **`pytest.approx`** compares floats within a tolerance (`0.1 + 0.2 == approx(0.3)`).
- **Fixtures**: `@pytest.fixture`, ask for one by naming it as a parameter. `return` = setup only; `yield` = setup, then teardown after (runs even if the test fails). Scopes: `function` (default), `class`, `module`, `session`. Fixtures can use other fixtures; `autouse=True` applies to all tests.
- **`conftest.py`**: shared fixtures visible to that folder and everything below. Never import from it.
- **Parametrize**: `@pytest.mark.parametrize("a, b, expected", [...], ids=[...])` makes one test per row. Stacked decorators multiply (2 x 2 = 4). `pytest.param(..., marks=..., id=...)` tweaks one case.
- **Built-in fixtures**: `tmp_path` (fresh folder), `monkeypatch` (`setattr`, `setenv`, `delenv`, `delattr`, `setitem`, `chdir`; all undone after the test), `capsys` / `capfd` (captured output), `caplog` (captured logging).
- **Marks**: `skip`, `skipif`, `xfail` (`strict=True` makes an unexpected pass a failure), custom marks selected with `-m "slow or db"`. Register them in `pytest.ini` / `pyproject.toml` and use `--strict-markers`.
- **Selection / reporting**: `-k "expr"`, `file.py::Class::test`, `-x`, `--maxfail=N`, `--lf`, `-q`/`-v`, `--tb=short|line|no`, `-rA`, `--collect-only`, `--setup-show`.
- **Mocking**: `unittest.mock.patch` or `monkeypatch.setattr`. `mocker` is only from the `pytest-mock` plugin.
- **Make hidden inputs explicit** so tests control them: pass `argv` to `main()`, pass a path (use `tmp_path`), inject the clock, pass a seeded `random.Random`.
- **Test doubles**: dummy (fills a slot), stub (canned answer), fake (simple working version), spy (records calls), mock (verifies calls). Prefer real > fake > stub > mock.
- **AAA**: Arrange, Act, Assert, one behavior per test, named like a sentence.
- **Run it from code**: `pytest.main([...])` in a subprocess, with `plugins=[obj]` to collect results.

## Gotchas (the part worth revising twice)
- Patch a name **where it is used**, not where it is defined. After `from app import fetch_price`, patching `"app.fetch_price"` does not change the copy inside `report.py`; the real function still runs.
- Two test files with the same name in different folders (and no `__init__.py`) cause an "import file mismatch" collection error.
- A `Test*` class with `__init__` is skipped with only a warning, and a helper named `check_x` is not collected. Always glance at the collected count.
- Order dependence is the classic flaky test: it passes in a full run and fails alone with `-k`. Other causes: real time, unseeded randomness, network, leaked global state.
- `--lf` needs the cache plugin; if you disable `cacheprovider` it will not work.
- Code after the raising line inside `with pytest.raises(...)` never runs. `pytest.raises(Exception)` is too broad.
- `approx(0)` has no relative tolerance: use `abs=`. Do not use `approx` for money (use `Decimal`).
- A fixture that crashes during setup shows as `ERROR`, not `FAILED`.
- Coverage % shows what ran, not whether the tests are good.

## When it matters
Any project you will keep for more than a week. Tests let you change code without fear, and pytest makes writing them cheap. Use `python -m pytest` so the current folder is on `sys.path`.

## One-line recap example
```python
import pytest

@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (0, 0, 0)], ids=["pos", "zero"])
def test_add(a, b, expected):
    assert a + b == expected

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="division"):
        1 / 0
```
