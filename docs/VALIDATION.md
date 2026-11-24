# Phase 1 validation — 25 November 2026

Only inventory, correctness fixes, and compatibility fixes are applied. Original folder locations and notebook teaching structure are retained. Phase 2 and later are pending. No changes were staged or committed.

## Checked environments

| Component | Current environment | Compatibility environment |
|---|---|---|
| Python | 3.13.1 | 3.10.19 |
| NumPy | 2.5.5 | 1.26.4 |
| Pandas | 3.1.1 | 2.2.3 |
| SQLite | 3.51.2 | 3.50.4 |
| Python reference tests | 619 passed | 619 passed |
| SQL reference tests | 60 passed | 60 passed |
| Python notebooks | 123 passed | 123 passed |
| SQL notebooks | 38 passed | 38 passed |
| Bash notebooks | 21 passed | 21 passed |

Notebook totals combine a complete language run with targeted reruns of the notebooks changed after a failure. All affected notebooks passed their final rerun. Runs used temporary repository copies, fresh kernels, and matching environment-specific Python kernels. Saved outputs for changed notebooks come from the current environment. Untouched notebooks and all 12 pre-existing untracked Bash notebooks were preserved byte-for-byte.

## Corrected behavior

1. Safe writes use unique temporary siblings and clean up after a failed replacement.
2. Inventory requests reject non-finite prices and out-of-range integers; atomic stock updates cannot overflow SQLite integers.
3. Async pipeline workers are cancelled and awaited on errors or caller cancellation.
4. The NumPy promotion demonstration explains and catches the NumPy 2 out-of-range scalar error.
5. The SQLite aggregate demonstration exhausts the earlier cursor before replacing a registered function.
6. The sales-cleaning test states the expected object dtype explicitly across Pandas versions.
7. Newer async syntax is guarded so Python 3.10 can parse and complete the notebook.
8. Log hour buckets use UTC.
9. EventEmitter reports the number of callbacks actually called, even if subscriptions change.
10. Top-k indices work with unsigned arrays and signed integer limits, preserving tie order.
11. Task tags containing the storage separator are rejected before a write.
12. The log CLI counts malformed lines without retaining their text; callers may still request diagnostic lines.

Compatibility checks also exposed unguarded TOML, exception-note, possessive-regex, and SQLite API examples. TOML uses the `tomli` backport on Python 3.10; newer APIs are guarded or demonstrate a compatible equivalent. The async unittest demonstration runs outside Jupyter's host event loop.

## Reproduce

Use Python 3.10+ and install `01-GeneralPurposeLanguage/Python/requirements.txt` in a virtual environment. Install that environment as a Jupyter kernel and ensure the runners select it; otherwise `kernel_name="python3"` may point to a different interpreter.

From the Python language directory:

```bash
python -m pytest 12-Practice-And-Projects --solutions -q
python tools/run_notebooks.py
```

From the SQL language directory:

```bash
python -m pytest 11-Practice --solutions -q
python tools/run_notebooks.py
```

From the Bash language directory:

```bash
python tools/run_notebooks.py
```

Without `--solutions`, unfinished learner assignments are expected to fail.

## Limits

Validated on macOS with Bash 3.2/BSD tools. Windows/Linux and intermediate Python versions were not executed. Optional tool/library sections may skip when their dependency is absent; the runs do not prove every optional integration. FastAPI's TestClient emitted an upstream httpx deprecation warning; all reference tests passed. Dependency vulnerability databases were not checked.
