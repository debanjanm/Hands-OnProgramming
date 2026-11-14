# Documentation And Doctest — Notes

## What this covers
Docstrings as the first documentation, `doctest` (examples in docstrings that run as tests), the other docs a project needs, and a tiny docs generator built on `inspect`.

## Key points
- A **docstring** is the first string in a module/class/function, stored in `__doc__`. `help()`, editors, `pydoc` and Sphinx all read it.
- **Three styles, same facts**: Google (`Args:` / `Returns:` / `Raises:`, easiest in plain text), NumPy (underlined sections), reST (`:param x:`). Pick one per project; Google is a good default.
- **Good docstring**: imperative one-line summary, then units/ranges/meaning of args, what is returned (including special values), what is raised, one example. **Not**: a restatement of the code, or types already in the hints.
- `inspect.getdoc()` cleans indentation and inherits a parent method's docstring; raw `__doc__` keeps the source indentation. `pydoc.render_doc(obj)` gives the terminal page; `python -m pydoc -w mod` writes HTML.
- **doctest**: lines starting `>>>` are run, the lines below are the expected output. Run with `doctest.testmod()`, `python -m doctest -v file.py`, `doctest.testfile("guide.txt")`, or `pytest --doctest-modules`. Exit code is 1 on failure.
- **Expected exceptions**: write `Traceback (most recent call last):`, then `...`, then the exact exception line.
- **Option flags**: `ELLIPSIS` (`...` matches anything, e.g. object addresses), `NORMALIZE_WHITESPACE`, `IGNORE_EXCEPTION_DETAIL`, `SKIP`. Enable per example with `# doctest: +ELLIPSIS`.
- **Project docs**: README (what/install/quick start/dev/license), `CHANGELOG.md` (Keep a Changelog: Added/Changed/Fixed…, newest first, `Unreleased` on top), CONTRIBUTING, LICENSE, ADRs (short "why we decided X" files).
- **Generators**: Sphinx (`sphinx-quickstart`, autodoc + napoleon), MkDocs + mkdocstrings, pdoc, built-in pydoc. Build docs in CI so they cannot rot.
- **Good error messages** say what went wrong, with which value, and what to do. `--help` needs a description, per-argument help and examples.
- **Docs generator idea**: honour `__all__`, skip `_private` names, only document objects defined in the module, print `inspect.signature` + `inspect.getdoc` as Markdown.

## Gotchas (the part worth revising twice)
- doctest compares **text exactly**: `0.1 + 0.2` prints `0.30000000000000004`, not `0.3` (use `round()`).
- **Trailing whitespace** in output is invisible in the failure report and editors strip it; show `repr(...)` instead.
- A **blank line** ends expected output; write `<BLANKLINE>`.
- **Set order** of strings changes between runs (hash randomization); use `sorted()`. Dict order is stable since 3.7.
- **Object addresses** (`<object at 0x...>`) need `ELLIPSIS`.
- **Backslashes**: in a normal docstring `\n` becomes a real newline before doctest sees it and the example breaks (doctest raises `ValueError`). Use a raw docstring `r"""..."""`.
- An undocumented exception fails the example and shows a traceback.
- Flags make tests blind; prefer deterministic output.
- doctest = a few teaching examples; **pytest** = fixtures, parametrized edge cases, mocks, I/O. Use both. No randomness, secrets or network in doctests.
- Comments explain **why**, docstrings state the contract; delete commented-out code and use `# TODO(owner): ...` so TODOs are searchable.

## When it matters
Any code other people (or future you) will call. Docstrings plus a runnable example are the cheapest docs that stay correct; the README quick start should itself be tested.

## One-line recap example
```python
def add(a, b):
    """Return a + b.

    >>> add(2, 3)
    5
    """
    return a + b
# python -m doctest -v this_file.py   -> "1 passed and 0 failed"
```
