# SQLite With Python — Notes

## What this covers
Driving SQLite from the stdlib `sqlite3` module: connections and cursors, parameters and injection, row factories, transactions, foreign keys and constraints, type adapters, dates, JSON1, indexes and query plans, backup, user-defined functions, threads, migrations, and a repository wrapper. SQL itself: see `../../../02-DomainSpecificLanguage/SQL`.

## Key points
- `sqlite3.connect(":memory:")` is a throwaway database; every `:memory:` connection is its own separate database.
- `execute`, `executemany` (many parameter sets), `executescript` (several statements, no parameters).
- Values go through placeholders: `?` with a tuple or `:name` with a dict. Never f-string user input into SQL.
- `conn.row_factory = sqlite3.Row` gives name access, `keys()`, and `dict(row)`.
- `commit()` / `rollback()` make multi-step changes all-or-nothing. `with conn:` commits on success and rolls back on exception.
- `PRAGMA foreign_keys = ON` is needed **per connection**. Constraints (`NOT NULL`, `UNIQUE`, `CHECK`) raise `sqlite3.IntegrityError`.
- Adapters/converters plus `detect_types=PARSE_DECLTYPES` map Python types (Decimal, date) to storage.
- JSON1: `json_extract`, `->`, `->>`, `json_each`, `json_set`; guard columns with `CHECK (json_valid(...))`.
- `EXPLAIN QUERY PLAN` shows `SCAN` (full table) vs `SEARCH ... USING INDEX`.
- `conn.backup(other)` snapshots a live database; `create_function` / `create_aggregate` / `create_collation` extend SQL with Python.
- `PRAGMA user_version` stores the schema version for a simple migration loop.

## Gotchas (the part worth revising twice)
- Single value params need a trailing comma: `("Asha",)`; `("Asha")` is just a string.
- Placeholders cannot stand in for table/column names; whitelist identifiers instead.
- `with conn:` does **not** close the connection — use `contextlib.closing` or `conn.close()`.
- `PRAGMA foreign_keys = ON` inside an open transaction is silently ignored; commit first.
- `executescript` commits any pending transaction first and takes no parameters.
- A connection works only in its creating thread by default; use one connection per thread and a file database, plus `timeout=` for lock waits.
- SQLite has no real date type; Python 3.12 deprecates the default date/datetime adapters, so register your own (ISO-8601 text).
- `sqlite3.Row` has no `.get()`; a cursor can be read only once.
- Indexes are bypassed when the column is wrapped in a function (`lower(user)`).
- Only one writer at a time; `BEGIN IMMEDIATE` takes the write lock early.

## When it matters
SQLite is the zero-setup database for scripts, tests, caches, desktop/mobile apps and small services. Correct parameters, foreign keys and transactions are what keep that data trustworthy; a repository class keeps SQL in one place and easy to test with `:memory:`.

## One-line recap example
```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (n TEXT)")
with db:
    db.execute("INSERT INTO t VALUES (?)", ("safe",))
print(db.execute("SELECT n FROM t").fetchall())  # [('safe',)]
```
