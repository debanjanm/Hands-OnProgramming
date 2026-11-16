# 12 - Practice And Projects

Hands-on work to check that the topics in folders 01-11 actually stuck.
Everything runs locally with `pytest`; nothing touches the internet.

## How it works

Every exercise set has three files:

- `exercises/exNN_name.py` - **your file**: function stubs with the task, examples, a level (easy / medium / hard) and a hint. Each stub raises `NotImplementedError` until you write it.
- `solutions/exNN_name.py` - a reference answer. Try first, peek after.
- `tests/test_exNN_name.py` - the tests that decide if your answer is right.

```bash
pytest 12-Practice-And-Projects/tests/test_ex01_fundamentals_and_control_flow.py   # your work (fails until you solve it)
pytest 12-Practice-And-Projects --solutions                                        # reference answers: everything passes
```

Run `pytest` from the `Python/` folder (`pip install -r requirements.txt` first). Add `-x` to stop at the first failure and `-k name` to run one problem.

## Exercise sets (12 problems each, easy to hard)

| Set | Files |
|---|---|
| `ex01_fundamentals_and_control_flow` | [stubs](exercises/ex01_fundamentals_and_control_flow.py) · [solutions](solutions/ex01_fundamentals_and_control_flow.py) · [tests](tests/test_ex01_fundamentals_and_control_flow.py) |
| `ex02_strings` | [stubs](exercises/ex02_strings.py) · [solutions](solutions/ex02_strings.py) · [tests](tests/test_ex02_strings.py) |
| `ex03_collections` | [stubs](exercises/ex03_collections.py) · [solutions](solutions/ex03_collections.py) · [tests](tests/test_ex03_collections.py) |
| `ex04_functions_and_functional` | [stubs](exercises/ex04_functions_and_functional.py) · [solutions](solutions/ex04_functions_and_functional.py) · [tests](tests/test_ex04_functions_and_functional.py) |
| `ex05_oop` | [stubs](exercises/ex05_oop.py) · [solutions](solutions/ex05_oop.py) · [tests](tests/test_ex05_oop.py) |
| `ex06_errors_and_files` | [stubs](exercises/ex06_errors_and_files.py) · [solutions](solutions/ex06_errors_and_files.py) · [tests](tests/test_ex06_errors_and_files.py) |
| `ex07_iterators_generators_decorators` | [stubs](exercises/ex07_iterators_generators_decorators.py) · [solutions](solutions/ex07_iterators_generators_decorators.py) · [tests](tests/test_ex07_iterators_generators_decorators.py) |
| `ex08_stdlib_toolbox` | [stubs](exercises/ex08_stdlib_toolbox.py) · [solutions](solutions/ex08_stdlib_toolbox.py) · [tests](tests/test_ex08_stdlib_toolbox.py) |
| `ex09_concurrency_and_async` | [stubs](exercises/ex09_concurrency_and_async.py) · [solutions](solutions/ex09_concurrency_and_async.py) · [tests](tests/test_ex09_concurrency_and_async.py) |
| `ex10_numpy` | [stubs](exercises/ex10_numpy.py) · [solutions](solutions/ex10_numpy.py) · [tests](tests/test_ex10_numpy.py) |
| `ex11_pandas` | [stubs](exercises/ex11_pandas.py) · [solutions](solutions/ex11_pandas.py) · [tests](tests/test_ex11_pandas.py) |
| `ex12_sql_and_data_access` | [stubs](exercises/ex12_sql_and_data_access.py) · [solutions](solutions/ex12_sql_and_data_access.py) · [tests](tests/test_ex12_sql_and_data_access.py) |

## Capstone projects

Each project has a `README.md` (goal, milestones, spec, hints), a `starter/` skeleton to fill in, a `reference/` solution, and `tests/`.

| Project | What you build | Practises |
|---|---|---|
| [p1_task_manager](projects/p1_task_manager/README.md) | Task manager CLI | `argparse`, sqlite3, dates, export, exit codes, logging |
| [p2_log_analyzer](projects/p2_log_analyzer/README.md) | Access-log analyzer | regex parsing, generators, `Counter`, percentiles, anomaly detection, CLI |
| [p3_inventory_api](projects/p3_inventory_api/README.md) | Inventory REST API | FastAPI, pydantic, repository + sqlite, auth dependency, `TestClient` |
| [p4_sales_analysis](projects/p4_sales_analysis/README.md) | Sales analysis pipeline | pandas cleaning and KPIs, cohort table, matplotlib charts, report writer |

```bash
pytest 12-Practice-And-Projects/projects/p1_task_manager              # tests against your starter/
pytest 12-Practice-And-Projects/projects/p1_task_manager --solutions   # tests against reference/
```

## Notes

- The starter files were generated from `reference/`; if you edit a reference solution, update its starter by hand.
- No notebooks here: stubs fail on purpose, so they are plain `.py` files.
