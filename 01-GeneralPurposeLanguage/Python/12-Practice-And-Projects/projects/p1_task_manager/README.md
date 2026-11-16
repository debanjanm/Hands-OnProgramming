# Project 1: Task Manager (`taskman`)

Build a command-line to-do manager. Tasks live in a SQLite file, so they are still there the next time you run it.

## Goal

```
$ python3 -m taskman add "Pay rent" -p high -d 2025-06-01 -t home
added task 1: Pay rent
$ python3 -m taskman list
  1 [ ] high   2025-06-01 Pay rent #home OVERDUE
```

## What you will practise

`argparse` subcommands, `sqlite3`, `datetime`, `dataclasses`, `csv` / `json`, `logging`, exit codes, and testing a CLI by calling `main(argv)`.

## Milestones (tick them off)

- [ ] **1. Dates** (`dates.py`): `parse_due` accepts `YYYY-MM-DD`, `today`, `tomorrow`, `+Nd`; bad input raises `ValueError`. `is_overdue` is true only for open tasks due before today.
- [ ] **2. Storage** (`store.py`): `TaskStore` with `add`, `get`, `mark_done`, `delete`; `TaskNotFound` for unknown ids; validate title and priority; data survives re-opening the file. `resolve_db_path` in `cli.py`.
- [ ] **3. Priorities, tags, search** (`store.list`, `store.search`, `format_task`): sorting, `--tag`, `--overdue`, case-insensitive search.
- [ ] **4. Export** (`export.py`): `to_json`, `to_csv`, and `Task.to_dict`.
- [ ] **5. CLI** (`cli.py`): `build_parser` and one `cmd_*` function per subcommand.
- [ ] **6. Errors and logging** (`cli.main`): clean `error: ...` messages on stderr, exit codes below, `-v` for debug logs.

## Spec

```
taskman [--db PATH] [-v] <command>
  add TITLE [-p low|normal|high] [-d DUE] [-t TAG ...]
  list [--all] [--tag TAG] [--overdue]
  done ID
  delete ID
  search TEXT
  export [--format json|csv] [-o FILE]
```

Database path: `--db`, else the `TASKMAN_DB` environment variable, else `tasks.db`.

| Exit code | Meaning |
|---|---|
| 0 | OK |
| 1 | task id not found |
| 2 | bad input (bad date, empty title, wrong usage) |
| 3 | database or file problem |

Public API the tests use: `taskman.dates.parse_due / is_overdue`, `taskman.store.TaskStore / Task / TaskNotFound`, `taskman.export.to_json / to_csv`, `taskman.cli.main(argv, today=None) -> int`. `main` must **return** the exit code, not call `sys.exit`. The `today` argument lets tests freeze the date.

## Hints

- Open `starter/taskman/` and read each docstring; every stub has a `TODO` for its milestone.
- Use `?` placeholders in SQL, never f-strings.
- `sqlite3.connect(path)` creates the file; `row_factory = sqlite3.Row` lets you read `row["title"]`.
- Store tags as `"a,b"` text and split them on the way out.
- `parser.parse_args()` raises `SystemExit` on bad usage. Catch it in `main` and return its code.
- Do the milestones in order; run the tests after each one.

## Run and test

From `12-Practice-And-Projects/`:

```
python3 -m pytest projects/p1_task_manager -q              # your starter code
python3 -m pytest --solutions projects/p1_task_manager -q  # the reference solution
cd projects/p1_task_manager/reference && python3 -m taskman --db /tmp/demo.db list
```

At first almost everything fails with `NotImplementedError`. That is expected.

## Stretch goals

- `edit ID --title/--due/--priority` command.
- `list --sort due|priority`.
- Recurring tasks (`--repeat weekly`).
- Import from the CSV you exported.
