# 09 - Tooling And Quality

How professional Python is tested, debugged, measured, packaged, checked and secured.

| File | Covers |
|---|---|
| [01-Pytest-In-Depth](01-Pytest-In-Depth.ipynb) | Fixtures and scopes, `conftest.py`, parametrize, `tmp_path`/`monkeypatch`/`capsys`, marks, selection flags, test doubles |
| [02-Debugging-With-Pdb](02-Debugging-With-Pdb.ipynb) | Reading tracebacks, `pdb` command transcripts, post-mortem, `breakpoint()`, `faulthandler`, common-bug catalogue |
| [03-Profiling-And-Benchmarking](03-Profiling-And-Benchmarking.ipynb) | `timeit`, `cProfile`/`pstats`, `tracemalloc`, complexity growth, caching, measure-then-optimize workflow |
| [04-Packaging-And-Pyproject](04-Packaging-And-Pyproject.ipynb) | `pyproject.toml`, src layout, building a wheel, offline install into a venv, entry points, `importlib.metadata` |
| [05-Code-Quality](05-Code-Quality.ipynb) | `black`, `flake8`, `mypy`, `isort`, config in `pyproject.toml`, code smells, `pre-commit`, CI outline |
| [06-Documentation-And-Doctest](06-Documentation-And-Doctest.ipynb) | Docstring styles, `doctest` in depth, `pydoc`, README/CHANGELOG practice, a tiny docs generator |
| [07-Security-Basics](07-Security-Basics.ipynb) | Injection (eval, SQL, shell), path traversal, ReDoS, secrets and password storage, supply chain, checklist |
