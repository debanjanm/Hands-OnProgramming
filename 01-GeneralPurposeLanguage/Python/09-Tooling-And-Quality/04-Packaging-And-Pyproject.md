# Packaging and pyproject.toml — Notes

## What this covers
Turning a script into an installable package: `pyproject.toml`, `src/` layout, building a wheel and sdist, installing offline into a venv, versions, dependency specifiers, and the publishing flow.

## Key points
- **One file, `pyproject.toml`:** `[build-system]` (how to build), `[project]` (metadata, PEP 621), `[tool.xxx]` (settings for one tool).
- `[project]` fields: `name`, `version` (or `dynamic = ["version"]`), `description`, `readme`, `requires-python`, `license`, `dependencies`, `[project.optional-dependencies]` (extras like `pkg[dev]`), `[project.scripts]` (`greet = "greeter.cli:main"` makes a command).
- **Distribution name != import name:** `pip install greeter-demo`, then `import greeter`.
- **src layout** (`src/greeter/...`): the code cannot be imported from the project root until it is installed, so tests use what users get. A flat layout lets the working copy leak in and hides packaging bugs.
- `python -m greeter` runs `__main__.py`; the console script is a launcher pip writes from `[project.scripts]`. Both call the same `main()`.
- **Build:** `python -m build` makes an **sdist** (`.tar.gz`, source) and a **wheel** (`.whl`, a zip installed as-is). Wheel name = `name-version-python-abi-platform`, e.g. `-py3-none-any` for pure Python.
- A wheel is a zip: look inside with `zipfile`. `*.dist-info/` holds `METADATA`, `WHEEL`, `entry_points.txt`, `RECORD` (every file + hash, used for clean uninstall).
- **Offline install:** `python -m pip install --no-index --no-deps --no-build-isolation x.whl` inside a throwaway venv. Then `pip show / list / freeze / uninstall -y`.
- `importlib.metadata`: `version()`, `requires()`, `entry_points()`, `distribution().files` read the installed metadata at runtime.
- **Editable install** `pip install -e .`: source edits take effect with no reinstall. Needs a build backend available (use `--no-build-isolation` offline).
- **Versions:** SemVer `MAJOR.MINOR.PATCH`; PEP 440 adds `rc1`, `.post1`, `.dev1`. Single source of truth: `attr = "pkg.__version__"`, or read it with `importlib.metadata`.
- **Specifiers:** `==` pin, `>=2.28,<3` range, `~=2.28` (>=2.28, <3), `!=`, extras `pkg[extra]`, markers `; python_version < "3.11"`.
- **Libraries** declare loose ranges in `pyproject.toml`; **applications** pin exactly (`requirements.txt` / lock file: `uv.lock`, `poetry.lock`, pip-tools). Commit the lock file.
- `uv` = fast pip/venv/pip-tools/project manager (`uv venv`, `uv pip install`, `uv lock`, `uv sync`, `uv run`). `pipx` (or `uv tool install`) installs command-line apps in their own env.
- **Publish:** `build` -> `twine check` -> upload to TestPyPI -> install from it -> upload to PyPI. Prefer trusted publishing (no stored secret).
- Other backends: hatchling, flit-core, poetry-core, maturin (Rust).
- Public API: re-export in `__init__.py` and set `__all__`; ship an empty `py.typed` file so type checkers trust your hints.

## Gotchas (the part worth revising twice)
- Files that are not `.py` (CSV, templates, `py.typed`) are NOT in the wheel unless listed in `package-data`. Read them with `importlib.resources`, not a relative `open()`.
- `package-data` decides what goes in the **wheel**; `MANIFEST.in` decides the **sdist**. Tests and CHANGELOG were in the sdist but not the wheel.
- Never compare versions as strings: `"1.10" > "1.9"` is `False`. Use `packaging.version.Version`.
- A PyPI version is immutable: you can yank it, never overwrite it. Test on TestPyPI first.
- Changes to `pyproject.toml` (entry points, deps, package-data) are read at install time: reinstall, even for editable installs.
- Always run pip as `python -m pip` so it targets the interpreter you mean. Build/install demos here use `--no-isolation` / `--no-index` only because there is no network; normally build isolation is on.
- `pip freeze` lists everything installed, including dev tools: not a clean dependency list.

## When it matters
When code is shared between projects or machines, needs a command, is deployed, or is published. Namespace packages: `05-Python Advanced/05-Modules-And-Packages.py`.

## One-line recap example
```python
# pyproject.toml:  [project.scripts]  greet = "greeter.cli:main"
# shell:           python -m build && python -m pip install dist/*.whl && greet --name Ada
```
