# Aggregation & Grouping — Notes

## What this covers
Collapsing many rows into summary values: aggregate functions, GROUP BY (single and multi-column), HAVING vs WHERE, and SQLite's GROUP_CONCAT.

## Key points
- Aggregate functions collapse many rows into one value: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
- `COUNT(*)` counts rows; `COUNT(col)` counts only non-NULL values in that column — they can differ.
- `GROUP BY col` buckets rows by that column, then runs aggregates per bucket instead of over the whole table.
- `GROUP BY col1, col2` buckets by the combination — one group per distinct pair.
- `WHERE` filters rows before grouping; `HAVING` filters groups after aggregation (and can reference aggregate functions like `COUNT()`/`SUM()`, unlike WHERE).
- `GROUP_CONCAT(col, sep)` is SQLite-specific — concatenates a group's values into one string (comma-separated by default).

## Gotchas (the part worth revising twice)
- Every non-aggregated column in the SELECT list should appear in GROUP BY. SQLite is lenient and often won't error if you skip this, but relying on that is a portability trap — Postgres/MySQL (strict mode) will reject it.
- "Departments with more than 1 employee" needs `HAVING COUNT(*) > 1`, not `WHERE` — WHERE runs before aggregation and never sees the group's row count.
- WHERE and HAVING can be combined in one query: WHERE filters rows first, then GROUP BY buckets what's left, then HAVING filters the resulting groups.

## When it matters
Any "totals per category" question — headcount per department, revenue per region, anything summarized rather than listed row-by-row.

## One-line recap example
```sql
SELECT dept, COUNT(*) AS headcount
FROM employees
GROUP BY dept
HAVING COUNT(*) >= 2;
```
