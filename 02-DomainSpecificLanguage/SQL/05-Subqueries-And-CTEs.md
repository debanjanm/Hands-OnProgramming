# Subqueries & CTEs — Notes

## What this covers
Nesting queries inside queries: scalar subqueries, subqueries in WHERE/IN, correlated subqueries, and naming subqueries with WITH (including recursive CTEs).

## Key points
- A scalar subquery returns exactly one row, one column — usable anywhere a single value is expected.
- `WHERE col IN (subquery)` keeps outer rows whose value appears anywhere in the subquery's results — reads naturally for "matches any of these."
- A correlated subquery references a column from the outer query, so it re-runs once per outer row (unlike a plain scalar subquery, which runs once and gets reused).
- `WITH name AS (...)` (a CTE) names a subquery so it can be referenced like a table in the main query — more readable than deeply nested subqueries, and can be referenced more than once.
- `WITH RECURSIVE name(cols) AS (anchor UNION ALL recursive_term)` — the anchor runs once, then the recursive term keeps re-running against previously produced rows until it produces nothing new.
- Recursive CTEs are the standard way to generate a sequence (no real table needed) or walk a self-referencing hierarchy like an org chart.

## Gotchas (the part worth revising twice)
- Correlated subqueries can be O(n×m) without an index on the correlated column — `EXPLAIN QUERY PLAN` will show a scalar subquery re-executed per row if unindexed.
- Don't confuse a scalar subquery (runs once, reused for every outer row) with a correlated subquery (runs once per outer row) — they look similar but perform very differently.
- A recursive CTE needs a real termination condition in the recursive term (e.g. `WHERE n < 10`) — forget it and it never stops producing rows.

## When it matters
Reach for a CTE when a query would otherwise need deeply nested subqueries; reach for a recursive CTE specifically for hierarchies (org charts, category trees) or generated sequences.

## One-line recap example
```sql
WITH RECURSIVE org_chart(emp_id, depth) AS (
    SELECT emp_id, 0 FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id, oc.depth + 1
    FROM employees e JOIN org_chart oc ON e.manager_id = oc.emp_id
)
SELECT * FROM org_chart;
```
