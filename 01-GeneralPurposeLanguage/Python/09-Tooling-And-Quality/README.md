# 09 - Tooling And Quality

How professional Python is tested, debugged, measured, packaged, checked and secured.

| File | Covers |
|---|---|
| [01-Pytest-In-Depth.py](01-Pytest-In-Depth.py) · [notes](01-Pytest-In-Depth.md) | Fixtures and scopes, `conftest.py`, parametrize, `tmp_path`/`monkeypatch`/`capsys`, marks, selection flags, test doubles |
| [02-Debugging-With-Pdb.py](02-Debugging-With-Pdb.py) · [notes](02-Debugging-With-Pdb.md) | Reading tracebacks, `pdb` command transcripts, post-mortem, `breakpoint()`, `faulthandler`, common-bug catalogue |
| [03-Profiling-And-Benchmarking.py](03-Profiling-And-Benchmarking.py) · [notes](03-Profiling-And-Benchmarking.md) | `timeit`, `cProfile`/`pstats`, `tracemalloc`, complexity growth, caching, measure-then-optimize workflow |
| [04-Packaging-And-Pyproject.py](04-Packaging-And-Pyproject.py) · [notes](04-Packaging-And-Pyproject.md) | `pyproject.toml`, src layout, building a wheel, offline install into a venv, entry points, `importlib.metadata` |
| [05-Code-Quality.py](05-Code-Quality.py) · [notes](05-Code-Quality.md) | `black`, `flake8`, `mypy`, `isort`, config in `pyproject.toml`, code smells, `pre-commit`, CI outline |
| [06-Documentation-And-Doctest.py](06-Documentation-And-Doctest.py) · [notes](06-Documentation-And-Doctest.md) | Docstring styles, `doctest` in depth, `pydoc`, README/CHANGELOG practice, a tiny docs generator |
| [07-Security-Basics.py](07-Security-Basics.py) · [notes](07-Security-Basics.md) | Injection (eval, SQL, shell), path traversal, ReDoS, secrets and password storage, supply chain, checklist |
