# SQLAlchemy Core and ORM — Notes

## What this covers
SQLAlchemy 2.0 style on in-memory SQLite: Engine, Core (`text()`, `Table`, `select/insert/update/delete`), ORM models with `DeclarativeBase` / `Mapped` / `mapped_column`, relationships, the Session unit of work, joins, lazy vs eager loading and the N+1 problem, transactions, bulk operations, hybrid properties, pooling, and Alembic notes.

## Key points
- `create_engine("sqlite://")` is lazy and owns a connection pool. 2.0 connections do not autocommit: use `conn.commit()` or `engine.begin()`.
- `text("... :name ...")` with a dict of binds is injection-safe raw SQL; rows are tuple-like with `row.col` and `row._mapping`.
- Core: `MetaData` + `Table`, `metadata.create_all(engine)`, expressions with `==`, `&`, `|`, `.in_()`, `.like()`, `func.sum()`, `.join()`, `.group_by()`.
- ORM: `Mapped[int]`, `Mapped[str | None]` (nullable), `mapped_column(...)`, `relationship(back_populates=...)`, `secondary=` for many-to-many.
- Session = unit of work: `add` (pending) → `flush` (SQL, ids assigned) → `commit`. Loaded objects are dirty-tracked and live in an identity map.
- Query with `session.scalars(select(Model).where(...))`; `session.get(Model, pk)` for primary keys.
- Fix N+1 with `selectinload` (collections) or `joinedload` (many-to-one); `joinedload` on collections needs `.unique()`.
- `session.begin()` commits/rolls back automatically; `begin_nested()` is a savepoint.
- `session.execute(insert(Model), [dicts])` and `update(...).where(...)` are bulk operations.
- `@hybrid_property` works in Python on instances and as SQL on the class.

## Gotchas (the part worth revising twice)
- Use `&` / `|` with parentheses, not `and` / `or`, in `where()`.
- `join()` filters but does not load the related objects; eager loading is a separate option.
- Lazy loading hides N+1: count statements with a `before_cursor_execute` listener to prove it (3 authors cost 4 queries).
- After an exception the Session must `rollback()` before reuse; after commit, objects are expired and reload on access (detached ones raise `DetachedInstanceError`).
- `create_all()` never alters existing tables — you need migrations (Alembic: `revision --autogenerate`, `upgrade head`; always review the draft).
- Bulk statements skip cascades and Python-side events.
- Never share a Session across threads; create one Engine per database per process.
- Legacy `session.query()` and implicit autocommit are 1.x style — avoid in 2.0 code.
- `Numeric` returns `Decimal`; compare/convert deliberately.

## When it matters
Use Core when you think in tables and SQL; use the ORM when your domain is objects with relationships. Either way, SQLAlchemy gives parameterised queries, portability between databases, and pooling, but you must still watch the SQL it emits (N+1, missing indexes).

## One-line recap example
```python
from sqlalchemy import create_engine, text
with create_engine("sqlite://").connect() as c:
    print(c.execute(text("SELECT :x + 1"), {"x": 41}).scalar())  # 42
```
