# Setup & Tooling — Notes

## What this covers
Everything you need before writing real code: which Python is running, how to run it, how to ask it for help, how to keep project packages separate, and how to read the first errors you will hit.

## Key points
- **Which Python?** `sys.version` = version, `sys.executable` = the exact file running. Several Pythons can live on one machine — `sys.executable` is the truth.
- **Four ways to run code**: `python file.py` (script), `python -c "code"` (one-liner), `python -m module` (run a module using *this* interpreter's packages), `python -i file.py` (run, then stay in the REPL with the variables).
- **REPL** = type `python3`, get `>>>`, each expression prints its value. Best tool for "what does this do?" experiments.
- **`if __name__ == "__main__":`** — `__name__` is `"__main__"` when the file is run, and the module's own name when it is imported. The guard keeps demo/start-up code from running on import.
- **Shebang** (`#!/usr/bin/env python3`) on line 1 lets `./script.py` run directly on macOS/Linux after `chmod +x`. To Python itself it is just a comment.
- **Self-discovery**: `type(x)` = what is it, `dir(x)` = what can it do, `x.__doc__` / `help(x)` = what do the docs say. Filter out `_dunder_` names when exploring.
- **`import this`** prints the Zen of Python: "Readability counts", "Explicit is better than implicit", "Errors should never pass silently" — a design philosophy, not rules.
- **Keywords**: `keyword.kwlist` (35 on 3.12) can never be variable names. `softkwlist` (`match`, `case`, `type`, `_`) are special only in certain spots. `print` is *not* a keyword.
- **PEP 8**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_CASE` for constants, 4-space indent, lines ≤ 79 (or 88 with `black`), imports in 3 groups (stdlib / third-party / yours). Style never changes behaviour — only readability.
- **Virtual environment** = a private folder with its own interpreter link and `site-packages`. Create: `python3 -m venv .venv`. Inside one, `sys.prefix != sys.base_prefix`. A fresh venv holds only `pip`.
- **Package tools**: `pip install / uninstall / list / freeze`, `requirements.txt` (pinned snapshot), `uv` (fast all-in-one), `pipx` (install command-line *apps* in isolation), `pyproject.toml` (modern project + tool config).
- **Module search**: `import foo` checks `sys.modules`, then each folder in `sys.path` in order (script folder → `PYTHONPATH` → stdlib → site-packages). First match wins.
- **Reading errors**: read the traceback from the **bottom line** up — it holds the error type and message.
- **Notebooks** (Jupyter, Google Colab) = documents of *cells* (code or Markdown) run by a *kernel* (a live Python process that remembers variables). A `.ipynb` file is plain JSON: `nbformat`, `metadata`, and a `cells` list (`cell_type`, `source`, `outputs`...).
- **Jupyter setup**: in a venv, `python -m pip install jupyterlab`, then `jupyter lab`. To make a venv selectable as a kernel: `python -m ipykernel install --user --name my-venv`.
- **Magics / shell escapes** (`%timeit`, `%run`, `!pip install`) work only inside IPython — in a `.py` they are a `SyntaxError`. Plain-Python equivalents: `timeit`, `runpy.run_path`, `subprocess.run`. Prefer `%pip` over `!pip`.
- **Colab** = hosted notebooks on a temporary VM: `!pip install` again each fresh runtime, mount Drive with `drive.mount('/content/drive')`, pick a GPU under Runtime > Change runtime type.
- **Notebook vs script**: notebooks for exploring/plots/teaching; `.py` for real programs, imports, tests and clean git diffs (why this repo uses `.py`). Convert with `jupyter nbconvert --to script nb.ipynb`.
- **Detect the environment**: `'ipykernel' in sys.modules` is True in a notebook, `'google.colab' in sys.modules` in Colab.

## Gotchas (the part worth revising twice)
- `pip` may belong to a different Python than `python`. Use **`python -m pip install ...`** so the package lands in the interpreter you are actually running.
- Naming your own file `random.py`, `json.py`, `test.py` etc. **shadows** the real module and causes baffling errors. Never reuse stdlib names.
- Never commit `.venv/` to git; commit `requirements.txt` (or `pyproject.toml`) instead.
- `help(len())` calls `len` first and fails — pass the object, not its result: `help(len)`.
- `python` vs `python3`: on many systems `python` is missing or is Python 2/another install. Check `python3 --version`.
- Error types worth knowing: `SyntaxError` (code can't be parsed, nothing runs), `IndentationError` (is a `SyntaxError` subclass), `NameError` (undefined name or typo), `TypeError` (wrong kind of value), `ModuleNotFoundError` (is an `ImportError` subclass — not installed in *this* Python).
- A `SyntaxError` is often on the line *before* the one reported (an unclosed bracket).
- `True`/`False`/`None` are capitalised keywords; `true` is just an unknown name → `NameError`.
- **Hidden state**: cells can run in any order, twice, or be deleted — the kernel keeps old variables, so the page can show results a clean run would not. Use "Restart Kernel and Run All" before trusting or sharing a notebook.
- `!pip` may install into a different Python than the kernel's; use `%pip` or `python -m pip`. `.ipynb` stores outputs inside the JSON, so diffs are noisy and files grow.
- `nbconvert --to script` leaves magics as `get_ipython()` calls — clean them up or the script only runs inside IPython.

## When it matters
Day one of any project (create a venv, pick the interpreter), whenever an import mysteriously fails, and every time you are stuck — `type` / `dir` / `help` and the bottom line of the traceback solve most problems before you search online.

## One-line recap example
```python
# terminal: python3 -m venv .venv && source .venv/bin/activate && python -m pip install requests
import sys
print(sys.executable, sys.prefix != sys.base_prefix)   # which Python? inside a venv? -> (path, True)

if __name__ == "__main__":   # runs on `python file.py`, skipped on `import file`
    print("hello from the main program")
```
