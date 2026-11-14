# Views & Query Plans — Notes

## What this covers
Naming a SELECT as a reusable view, and reading EXPLAIN QUERY PLAN to see whether a query scans a full table or uses an index.

## Key points
- `CREATE VIEW name AS SELECT ...` stores a query under a name — it holds no data of its own, every query against it re-runs the underlying SELECT.
- From the caller's side, a view behaves like a read-only table: SELECT, WHERE, ORDER BY, JOIN all work normally against it.
- `DROP VIEW name` removes the view definition only — the underlying tables and data are completely unaffected.
- `EXPLAIN QUERY PLAN` before a query shows how SQLite intends to execute it, without running it.
- A JOIN's ON condition needs an index on the joined column to avoid a full scan of one side for every row of the other.

## Gotchas (the part worth revising twice)
- Views are good for hiding join/aggregation complexity behind a simple name, but they don't cache anything — every hit re-runs the full underlying query, so a slow view is still slow every time.
- "SCAN" in the query plan output means a full row-by-row scan; "SEARCH ... USING INDEX" means it jumped straight to matches — watch for SCAN on a large table, that's your cue to add an index.
- An index only helps once it exists — a JOIN or WHERE on an unindexed column full-scans regardless of table size, and query plans can look very different before vs after `CREATE INDEX`.

## When it matters
Views: whenever a common query shape (a join + filter) gets reused across the app and deserves a stable name. Query plans: whenever a query feels slower than it should — always check EXPLAIN QUERY PLAN before guessing at the fix.

## One-line recap example
```sql
CREATE VIEW high_earners AS
SELECT e.first_name, e.salary FROM employees e WHERE e.salary > 65000;

EXPLAIN QUERY PLAN SELECT * FROM high_earners;
```
