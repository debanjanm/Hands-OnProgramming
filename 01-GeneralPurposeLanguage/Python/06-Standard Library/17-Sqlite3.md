# Sqlite3 — Notes

## What this covers
The built-in `sqlite3` module: a real SQL database that lives inside your program (one file, or RAM). This file is the Python side only — for the SQL language itself see `02-DomainSpecificLanguage/SQL/`.

## Key points
- **`sqlite3.connect(":memory:")`** = private database in RAM (great for tests). **`connect("app.db")`** = a file, created if missing. Two `:memory:` connections do **not** share data.
- **Connection** = the open database. **Cursor** = what you run SQL through and read results from. `conn.execute(...)` is a shortcut that makes a cursor for you.
- **`execute`** runs one statement, **`executemany`** runs one statement for many parameter tuples, **`executescript`** runs many statements (no parameters).
- **Reading**: `fetchone()` (tuple or `None`), `fetchmany(n)`, `fetchall()`, or just `for row in cursor` (lazy, best for big results). `cursor.description` has the column names.
- **`rowcount`** = rows changed by INSERT/UPDATE/DELETE (use it to detect "nothing matched"). **`lastrowid`** = id of the last inserted row.
- **Parameterized queries**: `?` with a tuple, or `:name` with a dict. Values travel separately from the SQL text, so they can never act as SQL code.
- **`conn.row_factory = sqlite3.Row`** → access columns by name (`row["name"]`), `dict(row)` works. Write a tiny factory function if you want real dicts.
- **Transactions**: changes are only permanent after `commit()`; `rollback()` throws them away. `with conn:` commits on success and rolls back on an exception. `conn.in_transaction` tells you if one is open.
- **`isolation_level`** controls when Python sends `BEGIN`; `None` = you control it manually. Python 3.12 adds the `autocommit` attribute (guarded in the file).
- **Types**: SQLite stores only NULL/INTEGER/REAL/TEXT/BLOB. For `datetime` etc. use `register_adapter` (Python → db) and `register_converter` (db → Python) plus `detect_types=PARSE_DECLTYPES | PARSE_COLNAMES`.
- **Custom SQL**: `create_function` (one value per row) and `create_aggregate` (class with `step`/`finalize`, like SUM).
- **`PRAGMA`**: `table_info(t)` (columns), `journal_mode` (`WAL` for readers + a writer), `foreign_keys`, `user_version`.
- **Migrations**: keep a numbered list of changes and store the applied version in `PRAGMA user_version`.
- **Repository / DAO class**: one class owns all the SQL for one table; the rest of the app never writes SQL.
- **Exceptions**: `sqlite3.Error` → `DatabaseError` → `IntegrityError` (UNIQUE / NOT NULL / FK / CHECK), `OperationalError` (no such table, locked, syntax), `ProgrammingError` (your bug: wrong param count, closed connection).

## Gotchas (the part worth revising twice)
- **Never build SQL with f-strings or `%`.** `password = '' OR '1'='1'` made the unsafe login return every user; the `?` version returned nothing. You cannot parameterize table/column names — whitelist them instead.
- **One parameter still needs a tuple**: `("Asha",)` not `"Asha"` (a string is treated as 4 separate characters → "Incorrect number of bindings").
- **`with conn:` does NOT close the connection** — it only commits/rolls back. Use `contextlib.closing(conn)` to really close it (and nest `with conn:` inside for transactions).
- **Forgetting `commit()`** = changes are lost on close. Uncommitted data is also invisible to other connections.
- **`executescript()` silently COMMITS** any open transaction first, so a later `rollback()` can't undo your earlier insert.
- **`executemany()` does not update `lastrowid`** — it kept the old value in the demo.
- **Foreign keys are OFF by default**: an orphan row was accepted until `PRAGMA foreign_keys = ON` — and that must run on every new connection.
- **Columns are loosely typed**: text went into an `INTEGER` column fine. Use `STRICT` tables (SQLite 3.37+) if you want real enforcement.
- **Python 3.12 deprecated the built-in `datetime` adapters/converters** — register your own (as the file does) to avoid the warning. Registration is process-wide.
- `execute()` refuses two statements in one string (blocks `; DROP TABLE`), but that does not make f-strings safe.

## When it matters
Scripts that need a local database, test suites (`:memory:`), small apps, caches, config/state storage, desktop and mobile apps — anywhere a full database server would be overkill. Not the right tool for many concurrent writers; use PostgreSQL there. `pandas.read_sql(query, conn)` loads results into a DataFrame (see `08-Pandas/09-Input-Output.py`).

## One-line recap example
```python
import sqlite3
from contextlib import closing
with closing(sqlite3.connect(":memory:")) as conn, conn:   # closes at the end, commits on success
    conn.execute("CREATE TABLE t (name TEXT)")
    conn.execute("INSERT INTO t VALUES (?)", ("O'Brien",))   # placeholder = safe, even with quotes
    print(conn.execute("SELECT name FROM t").fetchall())     # [("O'Brien",)]
```
