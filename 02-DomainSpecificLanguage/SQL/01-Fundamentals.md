# SQL Fundamentals — Notes

## What this covers
The absolute basics of SQLite: creating a table, inserting rows, and the four core query pieces (SELECT, WHERE, ORDER BY, LIMIT/OFFSET, DISTINCT).

## Key points
- SQLite has 5 storage classes: `NULL`, `INTEGER`, `REAL`, `TEXT`, `BLOB`.
- A column's declared type is just a hint ("type affinity"), not a strict rule — SQLite is dynamically typed at the column level.
- `INSERT INTO table (cols) VALUES (...), (...), (...)` — one multi-row statement is cheaper than many single-row inserts.
- Columns left out of an INSERT get their `DEFAULT`, or `NULL` if none is set.
- `SELECT col1, col2 FROM table` — prefer explicit columns over `*` in real code.
- `WHERE` filters rows based on raw column values.
- `ORDER BY col DESC` sorts; multiple columns break ties left to right (default is ASC).
- `LIMIT n OFFSET m` caps and skips rows — always pair with `ORDER BY` or the picked rows aren't guaranteed stable.
- `DISTINCT` removes duplicate rows, comparing the whole selected column list, not just one column.

## Gotchas (the part worth revising twice)
- SQLite's dynamic typing means you can insert a TEXT value into a REAL-affinity column and it just stores it as TEXT if it can't convert losslessly — legal in SQLite, would be a hard error in Postgres.
- Because of that, a `WHERE salary > 80000` filter can silently include a row where salary is stored as TEXT (`'not-a-number'`) — SQLite's sort rule ranks all TEXT values as greater than any NUMERIC value, regardless of content.
- `INTEGER PRIMARY KEY` is special — it's an alias for the hidden `rowid` column (more in file 08), so it auto-increments and is the fastest possible lookup.
- Without `ORDER BY`, row order is not guaranteed, so `LIMIT`/`OFFSET` pagination can silently return inconsistent pages.

## When it matters
Every query you write starts here — this is the vocabulary the rest of the SQL files build on.

## One-line recap example
```sql
SELECT first_name, salary FROM employees
WHERE salary > 70000
ORDER BY salary DESC
LIMIT 2 OFFSET 1;
```
