# 01. Connect, Cursor, Execute
# 02. executemany and executescript
# 03. Fetching: fetchone / fetchall / iteration
# 04. Parameterised Queries (Placeholders)
# 05. SQL Injection: Bad vs Good
# 06. row_factory and sqlite3.Row
# 07. Transactions: commit and rollback
# 08. Connection as a Context Manager (and its trap)
# 09. Isolation Levels and autocommit
# 10. PRAGMA foreign_keys and Foreign Keys
# 11. Constraints: NOT NULL, UNIQUE, CHECK
# 12. Adapters, Converters and detect_types
# 13. Dates and Times
# 14. JSON1 Functions
# 15. Indexes and EXPLAIN QUERY PLAN
# 16. Backup API
# 17. User-Defined Functions and Aggregates
# 18. Connection Per Thread
# 19. Migrations with PRAGMA user_version
# 20. Repository Class Wrapper
#
# SQL itself is covered in ../../../02-DomainSpecificLanguage/SQL - this file
# is about driving SQLite FROM Python. Everything runs in memory or in a
# temp directory that is removed at the end.

import datetime
import json
import os
import sqlite3
import tempfile
import threading

print("sqlite3 module works; library supports JSON1:", sqlite3.connect(":memory:").execute("SELECT json_valid('{}')").fetchone()[0] == 1)

# 01. Connect, Cursor, Execute
# ----------------------------
# - sqlite3 is in the standard library; SQLite itself is a single-file
#   database engine with no server.
# - connect(":memory:") makes a throwaway database in RAM. A file path
#   makes (or opens) a file.
# - conn.execute(...) is a shortcut that creates a cursor for you.
# - Each :memory: connection is its OWN separate database.

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE person (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
cur.execute("INSERT INTO person (name, age) VALUES ('Asha', 30)")
print("lastrowid:", cur.lastrowid, "| rowcount:", cur.rowcount)
other = sqlite3.connect(":memory:")
try:
    other.execute("SELECT * FROM person")
except sqlite3.OperationalError as exc:
    print("second :memory: connection is a different db ->", exc)
other.close()

# 02. executemany and executescript
# ----------------------------
# - executemany(sql, iterable_of_params) runs one statement many times:
#   faster and tidier than a Python loop of execute().
# - executescript(text) runs several statements separated by ; - but it
#   takes NO parameters and commits any pending transaction first.

conn.executemany("INSERT INTO person (name, age) VALUES (?, ?)", [("Ben", 25), ("Chitra", 41), ("Dev", 19)])
print("rows after executemany:", conn.execute("SELECT COUNT(*) FROM person").fetchone()[0])
conn.executescript("""
    CREATE TABLE city (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
    INSERT INTO city (name) VALUES ('Pune'), ('Kolkata');
""")
print("cities:", conn.execute("SELECT name FROM city ORDER BY name").fetchall())
print("# Gotcha: executescript cannot take ? parameters - never build its text from user input.")

# 03. Fetching: fetchone / fetchall / iteration
# ----------------------------
# - fetchone() -> one row or None; fetchall() -> list; fetchmany(n).
# - A cursor is iterable: "for row in cur" streams rows without loading
#   everything - good for big result sets.
# - A cursor can be consumed only ONCE; re-run execute() to re-read.

cur = conn.execute("SELECT name, age FROM person ORDER BY age")
print("fetchone:", cur.fetchone())
print("fetchmany(2):", cur.fetchmany(2))
print("rest via iteration:", [row for row in cur])
print("exhausted fetchone ->", cur.fetchone())
print("description (column names):", [d[0] for d in conn.execute("SELECT name, age FROM person").description])

# 04. Parameterised Queries (Placeholders)
# ----------------------------
# - Put ? (positional) or :name (named) in the SQL and pass the values
#   separately. The driver sends them as DATA, never as SQL text.
# - Params for positional style must be a sequence (tuple), even for ONE
#   value: ("Asha",) - not ("Asha").
# - Placeholders work only for VALUES - not for table or column names.

print("positional:", conn.execute("SELECT name FROM person WHERE age > ?", (26,)).fetchall())
print("named:", conn.execute("SELECT name FROM person WHERE age BETWEEN :lo AND :hi", {"lo": 20, "hi": 35}).fetchall())
try:
    conn.execute("SELECT name FROM person WHERE name = ?", ("Asha"))
except sqlite3.ProgrammingError as exc:
    print('("Asha") is a string, not a tuple ->', type(exc).__name__)
print("# Gotcha: you cannot do 'SELECT * FROM ?'. Whitelist identifiers in Python instead.")

# 05. SQL Injection: Bad vs Good
# ----------------------------
# - Building SQL with f-strings/% lets user text become SQL code.
# - The classic trick ' OR '1'='1 turns a login check into "always true".
# - Demo is on a tiny in-memory table with fake data only.

demo = sqlite3.connect(":memory:")
demo.execute("CREATE TABLE users (name TEXT, secret TEXT)")
demo.executemany("INSERT INTO users VALUES (?, ?)", [("alice", "a-secret"), ("bob", "b-secret")])
evil = "nobody' OR '1'='1"
bad_sql = f"SELECT name, secret FROM users WHERE name = '{evil}'"
print("BAD sql text:", bad_sql)
print("BAD result (leaks everyone):", demo.execute(bad_sql).fetchall())
print("GOOD result (evil text is just a name):", demo.execute("SELECT name, secret FROM users WHERE name = ?", (evil,)).fetchall())
try:
    demo.execute("SELECT 1; SELECT 2")
except sqlite3.ProgrammingError as exc:
    print("stacked statements refused by execute():", type(exc).__name__)
demo.close()
print("# Rule: values ALWAYS via placeholders. Identifiers (table/column) only from a fixed whitelist.")

# 06. row_factory and sqlite3.Row
# ----------------------------
# - By default rows are plain tuples: you must remember column order.
# - conn.row_factory = sqlite3.Row gives rows addressable by NAME (and
#   index), with .keys(). Convert with dict(row).
# - You can also set any callable, e.g. a function returning a dict.

conn.row_factory = sqlite3.Row
row = conn.execute("SELECT id, name, age FROM person WHERE name = ?", ("Asha",)).fetchone()
print("by name:", row["name"], "| by index:", row[2], "| keys:", row.keys())
print("as dict:", dict(row))
conn.row_factory = lambda c, r: {col[0]: val for col, val in zip(c.description, r)}
print("custom factory:", conn.execute("SELECT name FROM person WHERE id = 2").fetchone())
conn.row_factory = None
print("# Gotcha: a sqlite3.Row is not a dict - no .get(); wrap in dict(row) first.")

# 07. Transactions: commit and rollback
# ----------------------------
# - Changes (INSERT/UPDATE/DELETE) happen inside a transaction. Until
#   commit() they are visible only to THIS connection.
# - rollback() throws away everything since the last commit.
# - Use transactions to make multi-step changes all-or-nothing, e.g.
#   moving money between two accounts.

conn.execute("CREATE TABLE account (name TEXT PRIMARY KEY, balance INTEGER CHECK (balance >= 0))")
conn.executemany("INSERT INTO account VALUES (?, ?)", [("A", 100), ("B", 50)])
conn.commit()


def transfer(src, dst, amount):
    try:
        conn.execute("UPDATE account SET balance = balance - ? WHERE name = ?", (amount, src))
        conn.execute("UPDATE account SET balance = balance + ? WHERE name = ?", (amount, dst))
        conn.commit()
        return "ok"
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        return f"rolled back ({exc})"


print("transfer 30:", transfer("A", "B", 30), conn.execute("SELECT * FROM account ORDER BY name").fetchall())
print("transfer 500:", transfer("A", "B", 500), conn.execute("SELECT * FROM account ORDER BY name").fetchall())
print("in_transaction after commit/rollback:", conn.in_transaction)

# 08. Connection as a Context Manager (and its trap)
# ----------------------------
# - "with conn:" COMMITS if the block succeeds and ROLLS BACK if it
#   raises. That is its whole job.
# - TRAP: it does NOT close the connection. Use contextlib.closing(conn)
#   (or call conn.close()) for that.

with conn:
    conn.execute("UPDATE account SET balance = 0 WHERE name = 'B'")
print("committed by with-block:", conn.execute("SELECT balance FROM account WHERE name='B'").fetchone()[0])
try:
    with conn:
        conn.execute("UPDATE account SET balance = 999 WHERE name = 'B'")
        raise RuntimeError("boom")
except RuntimeError:
    pass
print("after exception, rolled back:", conn.execute("SELECT balance FROM account WHERE name='B'").fetchone()[0])
tmp = sqlite3.connect(":memory:")
with tmp:
    pass
tmp.execute("SELECT 1")
print("still usable after 'with tmp:' -> connection NOT closed")
tmp.close()

# 09. Isolation Levels and autocommit
# ----------------------------
# - Python's default (legacy mode) opens a transaction implicitly before
#   INSERT/UPDATE/DELETE and leaves SELECT outside it.
# - isolation_level=None means autocommit: every statement commits at
#   once, and you control transactions yourself with BEGIN/COMMIT.
# - Python 3.12 added the 'autocommit' attribute (True/False/legacy) as
#   the cleaner, future-proof control.
# - SQLite allows ONE writer at a time; readers don't block each other.
#   "BEGIN IMMEDIATE" grabs the write lock early to avoid surprises.

print("default isolation_level:", repr(conn.isolation_level))
auto = sqlite3.connect(":memory:", isolation_level=None)
auto.execute("CREATE TABLE t (x)")
auto.execute("BEGIN IMMEDIATE")
auto.execute("INSERT INTO t VALUES (1)")
print("in_transaction after BEGIN:", auto.in_transaction)
auto.execute("ROLLBACK")
print("rows after manual ROLLBACK:", auto.execute("SELECT COUNT(*) FROM t").fetchone()[0])
auto.close()
print("# Gotcha: DDL (CREATE TABLE) is transactional in SQLite, unlike many databases.")

# 10. PRAGMA foreign_keys and Foreign Keys
# ----------------------------
# - SQLite does NOT enforce foreign keys unless you turn them on PER
#   CONNECTION: PRAGMA foreign_keys = ON. Forgetting this is the classic
#   silent bug.
# - ON DELETE CASCADE / SET NULL / RESTRICT define what happens to child
#   rows.
# - Inside an open transaction the pragma is SILENTLY IGNORED - commit first.

fk = sqlite3.connect(":memory:")
fk.executescript("""
    CREATE TABLE author (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE book (id INTEGER PRIMARY KEY, title TEXT,
        author_id INTEGER REFERENCES author(id) ON DELETE CASCADE);
    INSERT INTO author VALUES (1, 'Tagore');
""")
print("foreign_keys default:", fk.execute("PRAGMA foreign_keys").fetchone()[0])
fk.execute("INSERT INTO book (title, author_id) VALUES ('Orphan', 99)")
print("orphan row accepted while OFF:", fk.execute("SELECT COUNT(*) FROM book").fetchone()[0])
fk.execute("DELETE FROM book")
fk.execute("PRAGMA foreign_keys = ON")
print("ON inside an open transaction is silently ignored:", fk.execute("PRAGMA foreign_keys").fetchone()[0])
fk.commit()
fk.execute("PRAGMA foreign_keys = ON")
print("after commit, then ON:", fk.execute("PRAGMA foreign_keys").fetchone()[0])
try:
    fk.execute("INSERT INTO book (title, author_id) VALUES ('Orphan', 99)")
except sqlite3.IntegrityError as exc:
    print("with ON:", exc)
fk.execute("INSERT INTO book (title, author_id) VALUES ('Gitanjali', 1)")
fk.execute("DELETE FROM author WHERE id = 1")
print("books after cascade delete:", fk.execute("SELECT COUNT(*) FROM book").fetchone()[0])
fk.close()

# 11. Constraints: NOT NULL, UNIQUE, CHECK
# ----------------------------
# - Let the database guard the data: NOT NULL, UNIQUE, CHECK, PRIMARY
#   KEY, DEFAULT. They catch bugs no matter which code path inserted.
# - Violations raise sqlite3.IntegrityError (a subclass of
#   sqlite3.DatabaseError). Catch it and decide what to do.
# - INSERT OR IGNORE / OR REPLACE / UPSERT (ON CONFLICT DO UPDATE)
#   handle duplicates in SQL.

conn.execute("""CREATE TABLE product (
    sku TEXT PRIMARY KEY, name TEXT NOT NULL, price REAL CHECK (price > 0), qty INTEGER DEFAULT 0)""")
tests = [
    ("INSERT INTO product (sku, name, price) VALUES ('A1', 'Pen', 1.5)", "valid"),
    ("INSERT INTO product (sku, name, price) VALUES ('A1', 'Dup', 2)", "dup pk"),
    ("INSERT INTO product (sku, name, price) VALUES ('B1', NULL, 2)", "null name"),
    ("INSERT INTO product (sku, name, price) VALUES ('C1', 'Free', 0)", "check"),
]
for sql, label in tests:
    try:
        conn.execute(sql)
        print(f"{label:10} -> inserted")
    except sqlite3.IntegrityError as exc:
        print(f"{label:10} -> IntegrityError: {exc}")
conn.execute("""INSERT INTO product (sku, name, price) VALUES ('A1', 'Pen', 1.5)
    ON CONFLICT(sku) DO UPDATE SET qty = qty + 10""")
print("upsert result:", conn.execute("SELECT sku, qty FROM product").fetchall())
conn.commit()

# 12. Adapters, Converters and detect_types
# ----------------------------
# - SQLite stores only NULL, INTEGER, REAL, TEXT, BLOB. Python types
#   like Decimal or custom classes need a translation layer.
# - register_adapter(type, func): Python -> SQLite value.
# - register_converter("NAME", func): SQLite bytes -> Python, matched by
#   the declared column type, only when detect_types=PARSE_DECLTYPES.
# - Python 3.12 deprecates the DEFAULT date/datetime adapters, so we
#   register our own (next section) to stay warning-free.

from decimal import Decimal

sqlite3.register_adapter(Decimal, str)
sqlite3.register_converter("DECIMAL", lambda b: Decimal(b.decode()))
dconn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dconn.execute("CREATE TABLE price (amount DECIMAL)")
dconn.execute("INSERT INTO price VALUES (?)", (Decimal("19.99"),))
value = dconn.execute("SELECT amount FROM price").fetchone()[0]
print("round trip:", repr(value), "| type:", type(value).__name__)
print("exact math:", value + Decimal("0.01"))
dconn.close()
print("# Gotcha: converter names are matched case-insensitively against the declared column type.")

# 13. Dates and Times
# ----------------------------
# - SQLite has NO real date type. Store ISO-8601 text ('2024-05-01
#   13:45:00') or Unix integers; both sort correctly as plain values.
# - Use our own adapters/converters (default ones are deprecated in 3.12).
# - SQL date functions: date(), time(), datetime(), strftime(),
#   julianday(). Avoid 'now' in demos - it changes every run.
# - Keep timezone-aware data in UTC and convert at the edges.

sqlite3.register_adapter(datetime.date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime.datetime, lambda d: d.isoformat(sep=" "))
sqlite3.register_converter("DATE", lambda b: datetime.date.fromisoformat(b.decode()))
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.datetime.fromisoformat(b.decode()))
tconn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
tconn.execute("CREATE TABLE event (name TEXT, day DATE, at TIMESTAMP)")
tconn.execute("INSERT INTO event VALUES (?, ?, ?)", ("launch", datetime.date(2024, 5, 1), datetime.datetime(2024, 5, 1, 13, 45)))
name, day, at = tconn.execute("SELECT * FROM event").fetchone()
print("python types back:", type(day).__name__, type(at).__name__, day, at)
print("raw stored text:", tconn.execute("SELECT CAST(day AS TEXT) || ' | ' || CAST(at AS TEXT) FROM event").fetchone()[0])
print("SQL date math:", tconn.execute("SELECT date(day, '+30 days'), strftime('%Y-%W', day), julianday('2024-05-11') - julianday(day) FROM event").fetchone())
tconn.close()

# 14. JSON1 Functions
# ----------------------------
# - SQLite (3.38+ built in) can query inside JSON text: json_extract(),
#   the -> and ->> operators, json_each(), json_set(), json_group_array().
# - Handy for semi-structured fields, but you lose normal indexing and
#   type checks - don't use it to avoid designing tables.
# - ->> returns an SQL value (text/number); -> returns JSON text.

jconn = sqlite3.connect(":memory:")
jconn.execute("CREATE TABLE doc (id INTEGER PRIMARY KEY, body TEXT CHECK (json_valid(body)))")
jconn.executemany("INSERT INTO doc (body) VALUES (?)", [
    (json.dumps({"user": "asha", "tags": ["a", "b"], "score": 7}),),
    (json.dumps({"user": "ben", "tags": ["b"], "score": 3}),),
])
print("json_extract:", jconn.execute("SELECT json_extract(body, '$.user') FROM doc").fetchall())
print("->> operator:", jconn.execute("SELECT body ->> '$.score' FROM doc ORDER BY 1 DESC").fetchall())
print("-> keeps JSON:", jconn.execute("SELECT body -> '$.tags' FROM doc WHERE id = 1").fetchone())
print("json_each tag counts:", jconn.execute(
    "SELECT value, COUNT(*) FROM doc, json_each(doc.body, '$.tags') GROUP BY value ORDER BY value").fetchall())
print("json_set:", jconn.execute("SELECT json_set(body, '$.score', 10) FROM doc WHERE id = 2").fetchone()[0])
try:
    jconn.execute("INSERT INTO doc (body) VALUES ('not json')")
except sqlite3.IntegrityError as exc:
    print("invalid json blocked:", exc)
jconn.close()

# 15. Indexes and EXPLAIN QUERY PLAN
# ----------------------------
# - An index lets SQLite jump to rows instead of scanning the whole
#   table. EXPLAIN QUERY PLAN shows which it will do: SCAN (slow, whole
#   table) vs SEARCH ... USING INDEX.
# - Index columns you filter/join/sort on often. Each index costs write
#   speed and disk, so don't index everything.
# - A function on the column (lower(name)) bypasses a plain index.

iconn = sqlite3.connect(":memory:")
iconn.execute("CREATE TABLE log (id INTEGER PRIMARY KEY, user TEXT, level TEXT)")
iconn.executemany("INSERT INTO log (user, level) VALUES (?, ?)", [(f"u{i % 50}", "info") for i in range(500)])


def plan(sql, params=()):
    return [r[3] for r in iconn.execute("EXPLAIN QUERY PLAN " + sql, params)]


q = "SELECT * FROM log WHERE user = ?"
print("before index:", plan(q, ("u7",)))
iconn.execute("CREATE INDEX idx_log_user ON log(user)")
print("after index :", plan(q, ("u7",)))
print("lower(user) :", plan("SELECT * FROM log WHERE lower(user) = ?", ("u7",)))
print("PK lookup   :", plan("SELECT * FROM log WHERE id = ?", (3,)))
iconn.close()

# 16. Backup API
# ----------------------------
# - conn.backup(target_conn) copies a live database safely, page by
#   page - far better than copying the .db file while it is in use.
# - Common uses: snapshot :memory: to a file, take hot backups, or load
#   a file into memory for fast tests.

workdir = tempfile.mkdtemp(prefix="sqlite_demo_")
try:
    path = os.path.join(workdir, "backup.db")
    disk = sqlite3.connect(path)
    conn.backup(disk)
    disk.close()
    print("backup file exists:", os.path.exists(path), "| size > 0:", os.path.getsize(path) > 0)
    reopened = sqlite3.connect(path)
    print("tables in backup:", [r[0] for r in reopened.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
    reopened.close()
finally:
    for f in os.listdir(workdir):
        os.remove(os.path.join(workdir, f))
    os.rmdir(workdir)
print("temp dir removed:", not os.path.exists(workdir))

# 17. User-Defined Functions and Aggregates
# ----------------------------
# - create_function(name, nargs, func, deterministic=True) lets SQL call
#   your Python. deterministic=True allows use in indexes.
# - create_aggregate(name, nargs, cls) with step()/finalize() builds
#   custom aggregates; create_window_function adds window versions.
# - create_collation customises sorting (e.g. case-insensitive).
# - Callbacks run in Python per row: convenient but slower than built-in
#   SQL functions.

conn.create_function("shout", 1, lambda s: s.upper() + "!", deterministic=True)
print("UDF:", conn.execute("SELECT shout(name) FROM person ORDER BY id LIMIT 2").fetchall())


class Median:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        v = sorted(self.values)
        mid = len(v) // 2
        return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2


conn.create_aggregate("median", 1, Median)
print("median age:", conn.execute("SELECT median(age) FROM person").fetchone()[0])
conn.create_collation("nocase_py", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
print("custom collation:", [r[0] for r in conn.execute("SELECT name FROM city ORDER BY name COLLATE nocase_py DESC")])

# 18. Connection Per Thread
# ----------------------------
# - By default a connection may be used ONLY in the thread that created
#   it; otherwise ProgrammingError (check_same_thread).
# - Safest rule: one connection PER thread. check_same_thread=False
#   turns the check off but YOU must then serialise access with a lock.
# - A :memory: db is per-connection, so threads need a file (or a
#   shared-cache URI) to see the same data.

errors = []


def use_main_connection():
    try:
        conn.execute("SELECT 1")
    except sqlite3.ProgrammingError as exc:
        errors.append(type(exc).__name__)


t = threading.Thread(target=use_main_connection)
t.start()
t.join()
print("using main conn in another thread ->", errors)

tdir = tempfile.mkdtemp(prefix="sqlite_threads_")
try:
    tpath = os.path.join(tdir, "shared.db")
    setup = sqlite3.connect(tpath)
    setup.execute("CREATE TABLE hits (who TEXT)")
    setup.commit()
    setup.close()

    def worker(n):
        local = sqlite3.connect(tpath, timeout=10)
        with local:
            local.execute("INSERT INTO hits VALUES (?)", (f"t{n}",))
        local.close()

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    check = sqlite3.connect(tpath)
    print("rows written by 4 threads:", sorted(r[0] for r in check.execute("SELECT who FROM hits")))
    check.close()
finally:
    for f in os.listdir(tdir):
        os.remove(os.path.join(tdir, f))
    os.rmdir(tdir)
print("# Tip: set timeout= so a busy writer waits instead of raising 'database is locked'.")

# 19. Migrations with PRAGMA user_version
# ----------------------------
# - SQLite has a free integer slot, PRAGMA user_version, to remember the
#   schema version. Apply numbered migrations in order, bump the number.
# - Run each migration + version bump in ONE transaction so a failure
#   leaves the old version intact.
# - Bigger projects use tools (Alembic, yoyo); the idea is the same.
# - PRAGMA values cannot be parameterised: format only trusted ints.

MIGRATIONS = [
    "CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)",
    "ALTER TABLE note ADD COLUMN created TEXT DEFAULT '2024-01-01'",
    "CREATE INDEX idx_note_created ON note(created)",
]


def migrate(db):
    current = db.execute("PRAGMA user_version").fetchone()[0]
    for number, sql in enumerate(MIGRATIONS[current:], start=current + 1):
        db.execute("BEGIN")
        db.execute(sql)
        db.execute(f"PRAGMA user_version = {int(number)}")
        db.execute("COMMIT")
    return current, db.execute("PRAGMA user_version").fetchone()[0]


mdb = sqlite3.connect(":memory:", isolation_level=None)
print("first run (from, to):", migrate(mdb))
print("second run (nothing to do):", migrate(mdb))
print("columns:", [r[1] for r in mdb.execute("PRAGMA table_info(note)")])
mdb.close()

# 20. Repository Class Wrapper
# ----------------------------
# - Hide SQL behind a small class so the rest of the app talks in
#   Python objects. It centralises placeholders, row mapping and
#   transactions, and makes swapping the storage easier.
# - Accept the connection in __init__ (easy to test with :memory:).
# - Use a dataclass for the row shape, and always parameterise.

from contextlib import closing
from dataclasses import dataclass


@dataclass
class Todo:
    id: int | None
    title: str
    done: bool = False


class TodoRepo:
    def __init__(self, db):
        self.db = db
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE IF NOT EXISTS todo (id INTEGER PRIMARY KEY, title TEXT NOT NULL UNIQUE, done INTEGER NOT NULL DEFAULT 0)")

    def add(self, title):
        with self.db:
            cur = self.db.execute("INSERT INTO todo (title) VALUES (?)", (title,))
        return Todo(cur.lastrowid, title)

    def get(self, todo_id):
        r = self.db.execute("SELECT * FROM todo WHERE id = ?", (todo_id,)).fetchone()
        return Todo(r["id"], r["title"], bool(r["done"])) if r else None

    def complete(self, todo_id):
        with self.db:
            return self.db.execute("UPDATE todo SET done = 1 WHERE id = ?", (todo_id,)).rowcount == 1

    def list(self, only_open=False):
        sql = "SELECT * FROM todo" + (" WHERE done = 0" if only_open else "") + " ORDER BY id"
        return [Todo(r["id"], r["title"], bool(r["done"])) for r in self.db.execute(sql)]


with closing(sqlite3.connect(":memory:")) as repo_db:
    repo = TodoRepo(repo_db)
    a = repo.add("learn sqlite3")
    b = repo.add("write tests")
    repo.complete(a.id)
    print("all:", repo.list())
    print("open:", [t.title for t in repo.list(only_open=True)])
    print("get missing:", repo.get(99), "| complete missing:", repo.complete(99))
    try:
        repo.add("write tests")
    except sqlite3.IntegrityError as exc:
        print("duplicate title:", exc)

conn.close()
print("done; all connections closed")
