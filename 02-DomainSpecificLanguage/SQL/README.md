# SQL

Dialect: **SQLite** (3.45 here). It needs no server, so every notebook is self-contained
and runs for real. Each topic is a Jupyter notebook: a plain-English cheat sheet at the
top, then numbered sections with the SQL and its printed result next to it.

```bash
pip install jupyterlab
jupyter lab 01-Basics/01-Fundamentals.ipynb
```

Every notebook builds its own tables and seed data and uses its own in-memory
database. SQL cells start with `%%sql` (a tiny helper defined in the first code
cell); each statement that returns rows prints a table. Cells marked
`expect_error` show the error instead of stopping, so mistakes can be demonstrated.

```bash
python3 tools/run_notebooks.py                # run every notebook, report failures
python3 tools/run_notebooks.py --save         # ...and save the outputs into the files
python3 tools/run_notebooks.py --only Joins   # one topic
```

## Topics

| Notebook | Covers |
|---|---|
| [01-Basics/01-Fundamentals](01-Basics/01-Fundamentals.ipynb) | `CREATE TABLE`, SQLite type affinity and `STRICT`, `INSERT` variants, `SELECT`, `ORDER BY`, `LIMIT`/`OFFSET` and keyset paging, `DISTINCT`, execution order |
| [01-Basics/02-Filtering-And-Operators](01-Basics/02-Filtering-And-Operators.ipynb) | three-valued logic, `NULL` traps, `LIKE`/`GLOB`, `IN`/`NOT IN`, `BETWEEN`, `CASE`, `COALESCE`/`NULLIF`/`IIF`, precedence, mixed-type comparison |
| [02-Querying/01-Joins](02-Querying/01-Joins.ipynb) | all join types, `ON` vs `WHERE`, anti/semi joins, self and many-to-many joins, join fan-out, `CROSS JOIN` |
| [02-Querying/02-Aggregation-And-Grouping](02-Querying/02-Aggregation-And-Grouping.ipynb) | `COUNT` variants, `GROUP BY`/`HAVING`, `FILTER`, conditional aggregation, `GROUP_CONCAT`, subtotals, fan-out traps |
| [02-Querying/03-Subqueries-And-CTEs](02-Querying/03-Subqueries-And-CTEs.ipynb) | scalar/correlated subqueries, `EXISTS` vs `IN`, CTE chains, `MATERIALIZED`, recursive CTEs (series, trees, graphs) |
| [02-Querying/04-Set-Operations](02-Querying/04-Set-Operations.ipynb) | `UNION`/`INTERSECT`/`EXCEPT`, duplicates, precedence, table diffs, emulating `FULL OUTER JOIN` |
| [03-Window-Functions/01-Window-Functions](03-Window-Functions/01-Window-Functions.ipynb) | ranking, `LAG`/`LEAD`, value functions, frames (`ROWS`/`RANGE`/`GROUPS`), running and moving totals, top-N per group, dedupe |
| [05-DDL-And-Integrity/01-Constraints-And-Keys](05-DDL-And-Integrity/01-Constraints-And-Keys.ipynb) | keys, foreign-key actions, deferred constraints, `UNIQUE`/`CHECK`/`DEFAULT`, generated columns, `STRICT`, `WITHOUT ROWID`, table rebuild |
| [05-DDL-And-Integrity/02-Views-And-Triggers](05-DDL-And-Integrity/02-Views-And-Triggers.ipynb) | views, `INSTEAD OF` triggers, audit and validation triggers, summary tables, trigger gotchas |
| [06-Data-Modification/01-Data-Modification](06-Data-Modification/01-Data-Modification.ipynb) | `UPDATE`/`DELETE`, `UPDATE ... FROM`, upsert, `REPLACE` vs upsert, `RETURNING`, bulk copy, soft deletes |
| [06-Data-Modification/02-Transactions](06-Data-Modification/02-Transactions.ipynb) | ACID, `BEGIN` modes, savepoints, rollback, locking and WAL, lost updates, deferred foreign keys |
| [07-Performance/01-Indexes-And-Query-Plans](07-Performance/01-Indexes-And-Query-Plans.ipynb) | B-tree intuition, `EXPLAIN QUERY PLAN`, covering/composite/partial/expression indexes, when indexes are ignored, `ANALYZE` |
| [09-Design/01-Normalization-And-Design](09-Design/01-Normalization-And-Design.ipynb) | 1NF to BCNF, anomalies, keys, relationship modelling, denormalizing on purpose, money/dates/enums, a worked schema |

## Planned next

`04-Patterns` (top-N, gaps and islands, pivot, cohorts, funnels), more `01-Basics`
(functions, dates, NULL semantics), `08-SQLite-Specials` (JSON, FTS5, `ATTACH`, CLI),
`10-Dialects` (SQLite vs PostgreSQL vs MySQL), `11-Practice` (problems with tests) and
`12-Projects`.
