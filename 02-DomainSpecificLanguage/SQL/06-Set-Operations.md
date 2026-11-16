# Set Operations — Notes

## What this covers
Combining the results of two SELECT queries as sets: UNION, UNION ALL, INTERSECT, EXCEPT, and the rules for aligning their columns.

## Key points
- `UNION` combines two result sets and removes duplicate rows — costs extra work (sort/hash) to find those duplicates.
- `UNION ALL` combines them without removing duplicates — cheaper, use it whenever the sets are already disjoint or duplicates are fine.
- `INTERSECT` returns only rows present in both result sets (deduplicated).
- `EXCEPT` returns rows from the first result set that don't appear in the second — order matters, EXCEPT is not symmetric (swapping the two queries gives a different answer).
- Every query combined this way must return the same number of columns; output column names come from the first query only.

## Gotchas (the part worth revising twice)
- `UNION` silently dedups — if you actually want every row including duplicates, `UNION ALL` is what you want, and it's also faster.
- `EXCEPT A minus B` is not the same as `EXCEPT B minus A` — always check which side is "first."
- SQLite doesn't require matching declared column types across combined queries (thanks to dynamic typing), but mismatched meaning per column position is still a design smell even if SQLite lets it run.
- Mismatched column counts raise a hard error ("SELECTs to the left and right of UNION do not have the same number of result columns") — easy to hit when one side gains a column later.

## When it matters
Combining results from different tables that represent the same kind of thing (e.g. employees + contractors), or comparing two sets to find what's shared or missing between them.

## One-line recap example
```sql
SELECT first_name AS name FROM engineering_team
UNION ALL
SELECT full_name FROM contractors;
```
