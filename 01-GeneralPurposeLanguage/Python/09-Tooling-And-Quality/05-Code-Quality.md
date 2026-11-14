# Code Quality — Notes

## What this covers
How formatters, linters and type checkers each catch a different kind of problem, how to configure them, and how teams automate them (pre-commit, CI) so humans can review design instead of commas.

## Key points
- **Four tools, four questions**: formatter (`black`) = is the layout consistent? linter (`flake8`, `ruff`) = any suspicious patterns? type checker (`mypy`) = do values fit together? tests (`pytest`) = is the behaviour right?
- **Run tools as `python -m <tool>`** so they use the same Python/venv as your code. Exit code `0` = clean; CI and pre-commit only read the exit code.
- **`black --check --diff`** previews changes, `black` applies them. It only moves whitespace/quotes — it never fixes unused imports, `== None` or bare `except`. Running it twice changes nothing (idempotent).
- **flake8 codes**: `F401` unused import, `F841` unused variable, `E711` `== None`, `E722` bare `except`, `E501` line too long, `C901` too complex (needs `--max-complexity`).
- **pyflakes** = only real mistakes, almost no false alarms. **isort** sorts imports (`--profile black` to match black).
- **mypy** only checks annotated code unless you add `--disallow-untyped-defs` / `--strict`. It catches wrong-type calls (`[arg-type]`) and bad assignments (`[assignment]`) without running anything.
- **`# type: ignore[code]  # reason`** is a last resort; `--warn-unused-ignores` flags stale ones.
- **`pyproject.toml`** holds `[tool.black]`, `[tool.mypy]`, `[tool.ruff]`, `[tool.pytest.ini_options]`. Per-module relaxations go in `[[tool.mypy.overrides]]`.
- **pre-commit** installs a git hook that runs your checks and blocks the commit if one fails (`pre-commit install`, `pre-commit run --all-files`). **CI** repeats the same checks on a clean machine: lint → types → tests → build.
- **Code smells with fixes**: deep nesting → guard clauses; boolean flag args → two named functions; magic numbers → constants; strings → `Enum`; tuples → `dataclass`; manual loop → comprehension/`any()`; one huge function → small named ones.
- **Refactor safely**: keep tests green, one small step at a time, assert old and new code agree on many inputs before swapping.
- **Quality ladder**: format → lint → types → tests → human review. Automate the first four.

## Gotchas (the part worth revising twice)
- **No stock tool flags `def f(x, cache=[])`** (mutable default). The default list is created once, so calls share it (`add_item('a')` then `add_item('b')` returned `['a', 'b']`). Needs flake8-bugbear (`B006`) or ruff. Same blind spot for shadowing builtins like `list` (`A002`).
- **flake8 does not read `pyproject.toml`.** Use `.flake8`/`setup.cfg`, ruff, or a plugin.
- **black vs flake8 line length**: black wraps at 88, flake8 warns at 79. Set `max-line-length = 88` and ignore `E203`, `W503`.
- **A bare `# noqa` hides every warning on the line.** Always name the code (`# noqa: E501`).
- **Shadowing a builtin** (`list = [...]`) compiles fine and fails later (`'list' object is not callable`).
- **Pin tool versions** (pre-commit `rev`, dev requirements) or CI turns red when a new release adds rules.
- **Passing all tools ≠ correct code.** Tests and review still decide that.
- `ruff` and `coverage` were not installed here; the file prints their commands as reference.

## When it matters
Any project with more than one person or more than a few weeks of life: tooling ends style arguments and catches a class of bugs before runtime. Adopt on old code gradually (format once in a single commit, then add lint rules and mypy per module).

## One-line recap example
```python
# python -m black --check . && python -m flake8 . && python -m mypy src && python -m pytest
def average(numbers: list[int]) -> float:
    return sum(numbers) / len(numbers)

average("abc")   # mypy: Argument 1 has incompatible type "str"; expected "list[int]"  [arg-type]
```
