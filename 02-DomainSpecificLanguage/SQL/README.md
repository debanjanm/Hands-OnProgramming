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

A few notebooks use SQLite features that depend on how your SQLite was built (math
functions, FTS5, R-Tree, `dbstat`) or on a recent version (`group_concat(... ORDER BY)` needs
3.44+, `->>` needs 3.38+). Check yours with `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`.

## Topics (38 notebooks)

| Notebook | Covers |
|---|---|
| [01-Basics/01-Fundamentals](01-Basics/01-Fundamentals.ipynb) | Creating tables, SQLite's flexible type system, inserting rows, basic SELECT, filtering, sorting, paging, DISTINCT, and the order in which SQL really runs. |
| [01-Basics/02-Filtering-And-Operators](01-Basics/02-Filtering-And-Operators.ipynb) | Comparison and logic operators, NULL and three-valued logic, LIKE/GLOB, IN, BETWEEN, CASE, COALESCE/NULLIF/IIF, operator precedence, and the number/text quirks of SQLite. |
| [01-Basics/03-String-And-Text-Functions](01-Basics/03-String-And-Text-Functions.ipynb) | Measuring, slicing and searching text: `length`, `substr`, `instr`, `replace`, `trim` and friends. |
| [01-Basics/04-Math-And-Numbers](01-Basics/04-Math-And-Numbers.ipynb) | Integer vs real arithmetic, the `/` and `%` operators, and what `CAST` really does. |
| [01-Basics/05-Dates-And-Times](01-Basics/05-Dates-And-Times.ipynb) | How SQLite stores dates (it has **no date type**): ISO-8601 TEXT, Julian day REAL, or Unix time INTEGER. |
| [02-Querying/01-Joins](02-Querying/01-Joins.ipynb) | Combining rows from two or more tables: INNER, LEFT, RIGHT, FULL OUTER, CROSS and self-joins. |
| [02-Querying/02-Aggregation-And-Grouping](02-Querying/02-Aggregation-And-Grouping.ipynb) | Aggregate functions (COUNT, SUM, AVG, MIN, MAX, TOTAL, GROUP_CONCAT) that collapse many rows into one value. |
| [02-Querying/03-Subqueries-And-CTEs](02-Querying/03-Subqueries-And-CTEs.ipynb) | Subqueries: a SELECT inside another statement (scalar, row, table; in WHERE, FROM, SELECT). |
| [02-Querying/04-Set-Operations](02-Querying/04-Set-Operations.ipynb) | `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT` and how they treat duplicates and NULLs. |
| [03-Window-Functions/01-Window-Functions](03-Window-Functions/01-Window-Functions.ipynb) | Window functions vs `GROUP BY`, `OVER (PARTITION BY ... ORDER BY ...)`. |
| [04-Patterns/01-Top-N-And-Ranking-Patterns](04-Patterns/01-Top-N-And-Ranking-Patterns.ipynb) | Top-N overall and top-N per group with `ROW_NUMBER`, `RANK`, `DENSE_RANK`. |
| [04-Patterns/02-Gaps-Islands-And-Sessions](04-Patterns/02-Gaps-Islands-And-Sessions.ipynb) | Islands (unbroken runs) and gaps (the holes between runs) in numbers, dates and statuses. |
| [04-Patterns/03-Pivot-Unpivot-And-Crosstabs](04-Patterns/03-Pivot-Unpivot-And-Crosstabs.ipynb) | Turning rows into columns (pivot) and columns into rows (unpivot) in SQLite, which has no `PIVOT` keyword. |
| [04-Patterns/04-Time-Series-Patterns](04-Patterns/04-Time-Series-Patterns.ipynb) | Calendar (date spine) tables built with a recursive CTE, so days with no data show up as zero. |
| [04-Patterns/05-Cohorts-Retention-And-Funnels](04-Patterns/05-Cohorts-Retention-And-Funnels.ipynb) | Signup cohorts, the retention matrix (month 0, 1, 2, ...), churn, rolling retention, new vs returning vs resurrected users. |
| [04-Patterns/06-Hierarchies-And-Graphs](04-Patterns/06-Hierarchies-And-Graphs.ipynb) | Trees stored as an adjacency list (`id`, `parent_id`) and queried with recursive CTEs: descendants, ancestors, depth, paths, leaves, subtree totals, level by level. |
| [04-Patterns/07-Data-Cleaning-And-Quality-In-SQL](04-Patterns/07-Data-Cleaning-And-Quality-In-SQL.ipynb) | Profiling a table: row counts, NULLs, distinct values, min/max, lengths and shapes. |
| [04-Patterns/08-Analytics-Recipes](04-Patterns/08-Analytics-Recipes.ipynb) | Customer analytics: RFM segmentation (`NTILE`), customer lifetime value, basket size and AOV. |
| [05-DDL-And-Integrity/01-Constraints-And-Keys](05-DDL-And-Integrity/01-Constraints-And-Keys.ipynb) | How a table protects its own data: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, NOT NULL, DEFAULT. |
| [05-DDL-And-Integrity/02-Views-And-Triggers](05-DDL-And-Integrity/02-Views-And-Triggers.ipynb) | Views: saved SELECTs you can query like tables, and how to make them writable. |
| [05-DDL-And-Integrity/03-Schema-Evolution-And-Migrations](05-DDL-And-Integrity/03-Schema-Evolution-And-Migrations.ipynb) | Changing a table after it has data: `ALTER TABLE` ADD / RENAME / DROP COLUMN, and what SQLite refuses to do. |
| [06-Data-Modification/01-Data-Modification](06-Data-Modification/01-Data-Modification.ipynb) | Changing data: INSERT (all the variants), UPDATE, DELETE, UPSERT, RETURNING, copying data between tables, and changing a table's shape with ALTER TABLE. |
| [06-Data-Modification/02-Transactions](06-Data-Modification/02-Transactions.ipynb) | How to group several statements into one all-or-nothing unit (a transaction), how SQLite handles locks and concurrency, and the classic mistakes (lost updates, half-finished work). |
| [06-Data-Modification/03-Bulk-Loading-And-Export](06-Data-Modification/03-Bulk-Loading-And-Export.ipynb) | Getting lots of rows IN: CSV, JSON, `INSERT ... SELECT`, `executemany`, staging tables, upserts, deduplication and handling bad rows. |
| [06-Data-Modification/04-History-Audit-And-Temporal-Data](06-Data-Modification/04-History-Audit-And-Temporal-Data.ipynb) | Keeping the past instead of overwriting it: soft delete, audit-log triggers, history tables, and "valid from / valid to" rows (SCD type 2). |
| [07-Performance/01-Indexes-And-Query-Plans](07-Performance/01-Indexes-And-Query-Plans.ipynb) | What an index is, how SQLite uses it, and how to see that with `EXPLAIN QUERY PLAN`. |
| [07-Performance/02-Query-Optimization-Patterns](07-Performance/02-Query-Optimization-Patterns.ipynb) | A catalogue of common slow-query patterns ("anti-patterns"), each with a rewrite that does less work. |
| [07-Performance/03-Pragmas-Storage-And-Maintenance](07-Performance/03-Pragmas-Storage-And-Maintenance.ipynb) | How SQLite stores a database in one file: fixed-size **pages**, **B-trees** for tables and indexes, and a **freelist** of unused pages. |
| [08-SQLite-Specials/01-JSON-In-SQLite](08-SQLite-Specials/01-JSON-In-SQLite.ipynb) | SQLite's built-in JSON functions: reading (`json_extract`, `->`, `->>`), writing (`json_set`, `json_insert`, `json_replace`, `json_remove`, `json_patch`), building (`json_object`, `json_array`, `json_group_array`,... |
| [08-SQLite-Specials/02-Full-Text-Search-FTS5](08-SQLite-Specials/02-Full-Text-Search-FTS5.ipynb) | Creating FTS5 virtual tables, loading them, and searching with `MATCH`. |
| [08-SQLite-Specials/03-Attach-Backup-And-The-CLI](08-SQLite-Specials/03-Attach-Backup-And-The-CLI.ipynb) | `ATTACH DATABASE` to work with several database files (or in-memory databases) on one connection, schema-qualified names (`main.`, `temp.` and the name you give in `ATTACH`), and cross-database joins and copies. |
| [08-SQLite-Specials/04-SQLite-With-Python](08-SQLite-Specials/04-SQLite-With-Python.ipynb) | Using Python's built-in `sqlite3` module as a SQL playground: parameters, cursors, row factories, type adapters. |
| [08-SQLite-Specials/05-RTree-Virtual-Tables-And-Extensions](08-SQLite-Specials/05-RTree-Virtual-Tables-And-Extensions.ipynb) | Virtual tables: tables that look normal in SQL but are backed by code (R-Tree, FTS5, DBSTAT, GEOPOLY, `json_each`, `pragma_*`). |
| [09-Design/01-Normalization-And-Design](09-Design/01-Normalization-And-Design.ipynb) | How to decide which tables and columns you need: normal forms (1NF, 2NF, 3NF, BCNF), the problems bad design causes (anomalies), keys, relationships, and practical column-type choices (money, dates, enums, JSON).... |
| [09-Design/02-Dimensional-Modeling-And-Star-Schemas](09-Design/02-Dimensional-Modeling-And-Star-Schemas.ipynb) | How to shape data for reporting (OLAP) instead of for day-to-day writes (OLTP): facts, dimensions, grain, star vs snowflake. |
| [09-Design/03-Schema-Design-Case-Studies](09-Design/03-Schema-Design-Case-Studies.ipynb) | Three complete designs, each walked through the same way: plain-English requirements, entities, a text ER sketch, `CREATE TABLE` with constraints and indexes, seed data, the queries the app really needs, and... |
| [10-Dialects/01-SQLite-vs-PostgreSQL-vs-MySQL](10-Dialects/01-SQLite-vs-PostgreSQL-vs-MySQL.ipynb) | A side-by-side cheat sheet of the places where SQLite, PostgreSQL and MySQL differ in daily work. |
| [10-Dialects/02-Writing-Portable-SQL](10-Dialects/02-Writing-Portable-SQL.ipynb) | What the portable core of SQL is, what to avoid, and how to adapt a query for another database. |

The `10-Dialects` notebooks compare SQLite with PostgreSQL and MySQL. Only the SQLite cells
(and SQLAlchemy's compiled SQL text) can run here, so the PostgreSQL 16 and MySQL 8.x
statements come from their documentation, not from a server: check them against your version.

## Practice

[`11-Practice`](11-Practice/README.md) has graded problems you solve in plain `.sql` files,
checked by `pytest` against a seeded dataset. Start with the `store` shop dataset (30 problems,
easy to hard):

```bash
pytest 11-Practice                 # check your answers
pytest 11-Practice --solutions     # check the reference answers
```

## Planned next

More practice datasets (`hr`, `streaming`, `bank`) and three capstone projects in `12-Projects`.
