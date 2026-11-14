import sqlite3
import sys
import os
import tempfile
import datetime
import warnings
from contextlib import closing
from dataclasses import dataclass
from typing import Optional

# 01. sqlite3 - Introduction
# ------------------------------------
# - sqlite3 is a full SQL database engine that lives INSIDE your Python process.
# - No server to install, no password, no network: the whole database is one file
#   (or just RAM when you use ":memory:").
# - Used everywhere: phone apps, browsers, desktop tools, tests, small web apps,
#   and as a quick local "scratch database" for scripts.
# - This file teaches the PYTHON side (connections, cursors, safety, types).
#   For the SQL language itself (SELECT, JOIN, GROUP BY, constraints,
#   transactions) see the SQL track: 02-DomainSpecificLanguage/SQL/
#   (esp. 01-Fundamentals, 03-Joins, 08-Constraints-And-Keys, 09-Transactions).

print("# 01. sqlite3 - Introduction")
print("# ------------------------------------")
print("python sqlite3 module version:", sqlite3.sqlite_version)

# 02. Connecting - ":memory:" vs a file
# ------------------------------------
# - sqlite3.connect(":memory:") -> a brand-new database in RAM, gone when closed.
#   Perfect for tests and for learning.
# - sqlite3.connect("app.db")   -> a file on disk; created if it does not exist.
# - Every ":memory:" connection is its OWN private database (two connections do
#   not share data).
print("\n# 02. Connecting - ':memory:' vs a file")
mem1 = sqlite3.connect(":memory:")
mem2 = sqlite3.connect(":memory:")
mem1.execute("CREATE TABLE t (x INTEGER)")
try:
    mem2.execute("SELECT * FROM t")
except sqlite3.OperationalError as e:
    print("mem2 cannot see mem1's table ->", type(e).__name__ + ":", e)
mem1.close()
mem2.close()

# A temp directory keeps the file-based demos from leaving anything behind.
tmp = tempfile.TemporaryDirectory()
db_path = os.path.join(tmp.name, "demo.db")
file_conn = sqlite3.connect(db_path)
file_conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
file_conn.execute("INSERT INTO notes (body) VALUES ('hello from a file')")
file_conn.commit()
file_conn.close()
print("file database exists on disk:", os.path.exists(db_path))

reopened = sqlite3.connect(db_path)  # data survived because it is in a file
print("data after reopening:", reopened.execute("SELECT body FROM notes").fetchall())
reopened.close()

# 03. Cursor and execute() - the basic loop
# ------------------------------------
# - connection = the open database.
# - cursor     = an object you run statements through and read results from.
# - conn.execute(...) is a shortcut: it makes a cursor, runs the SQL, returns it.
# - The usual flow: connect -> execute -> (commit if you changed data) -> close.
print("\n# 03. Cursor and execute()")
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE users (
        id    INTEGER PRIMARY KEY,
        name  TEXT NOT NULL,
        email TEXT UNIQUE,
        age   INTEGER
    )
    """
)
cur.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Asha", "asha@example.com", 30))
print("inserted one row, lastrowid =", cur.lastrowid)

# 04. executemany(), lastrowid, rowcount
# ------------------------------------
# - executemany(sql, list_of_param_tuples) runs the same statement for each tuple.
#   Much faster and tidier than a Python loop of execute() calls.
# - cursor.lastrowid : id of the LAST inserted row (for that cursor).
# - cursor.rowcount  : how many rows an INSERT/UPDATE/DELETE changed.
#   (For SELECT it is -1 - it does not know in advance.)
print("\n# 04. executemany(), lastrowid, rowcount")
people = [
    ("Ravi", "ravi@example.com", 25),
    ("Meera", "meera@example.com", 41),
    ("Debanjan", "deb@example.com", 28),
    ("Zoya", "zoya@example.com", 35),
]
cur.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", people)
print("executemany rowcount:", cur.rowcount)
print("lastrowid after executemany:", cur.lastrowid, "(gotcha: NOT updated by executemany - still the old value; use execute() per row if you need each new id)")

cur.execute("UPDATE users SET age = age + 1 WHERE age > 30")
print("UPDATE rowcount (rows changed):", cur.rowcount)
cur.execute("UPDATE users SET age = 0 WHERE name = 'nobody'")
print("UPDATE that matched nothing -> rowcount:", cur.rowcount, "(check this to detect 'not found')")
cur.execute("SELECT * FROM users")
print("SELECT rowcount:", cur.rowcount)
conn.commit()

# 05. Fetching results - fetchone / fetchmany / fetchall / iteration
# ------------------------------------
# - After a SELECT the rows are waiting inside the cursor. You pull them out:
#     fetchone()   -> next row as a tuple, or None when finished
#     fetchmany(n) -> list of up to n rows (good for batches)
#     fetchall()   -> list of ALL remaining rows (careful with huge tables!)
#     for row in cursor -> one at a time, lazy, memory friendly (preferred)
# - A cursor is a one-shot stream: once a row is fetched it is gone.
print("\n# 05. Fetching results")
cur.execute("SELECT id, name, age FROM users ORDER BY id")
print("fetchone  :", cur.fetchone())
print("fetchmany :", cur.fetchmany(2))
print("fetchall  :", cur.fetchall(), "(only the remaining rows)")
print("fetchone again:", cur.fetchone(), "(None = exhausted)")

print("iterating a cursor directly:")
for row in cur.execute("SELECT id, name FROM users ORDER BY id"):
    print("  ", row)

# cursor.description holds the column names (handy for printing tables)
cur.execute("SELECT id, name, age FROM users LIMIT 1")
print("column names from description:", [d[0] for d in cur.description])

# 06. Parameterized queries - "?" and ":name"
# ------------------------------------
# - NEVER paste values into SQL text. Put placeholders and pass values separately;
#   the driver sends them as DATA, never as SQL code.
# - Qmark style  : WHERE age > ?        with a tuple/list  (age_min,)
# - Named style  : WHERE age > :min     with a dict        {"min": 30}
# - Placeholders work for VALUES only. You cannot parameterize table or column
#   names (see the gotcha below).
print("\n# 06. Parameterized queries")
print("qmark :", conn.execute("SELECT name FROM users WHERE age > ? AND name != ?", (30, "Zoya")).fetchall())
print("named :", conn.execute(
    "SELECT name FROM users WHERE age BETWEEN :lo AND :hi ORDER BY name", {"lo": 25, "hi": 35}
).fetchall())
# Gotcha: a single parameter must still be a tuple -> ("Asha",) with the comma.
try:
    conn.execute("SELECT * FROM users WHERE name = ?", "Asha")  # a str is a sequence of 4 chars!
except sqlite3.ProgrammingError as e:
    print("forgot the tuple comma ->", type(e).__name__ + ":", e)
print("with ('Asha',):", conn.execute("SELECT name FROM users WHERE name = ?", ("Asha",)).fetchall())

# Table/column names cannot be placeholders. If you MUST choose one dynamically,
# validate it against a whitelist, then format it in.
ALLOWED_SORT = {"id", "name", "age"}
sort_col = "age"
assert sort_col in ALLOWED_SORT
print("whitelisted ORDER BY:", conn.execute(f"SELECT name FROM users ORDER BY {sort_col} DESC LIMIT 2").fetchall())

# 07. SQL injection - the attack and the defence
# ------------------------------------
# - SQL injection = user text that changes the MEANING of your query.
# - It is consistently one of the most common real-world security holes.
# - Below: a toy login check. Same attacker input, two implementations.
print("\n# 07. SQL injection demo")
sec = sqlite3.connect(":memory:")
sec.execute("CREATE TABLE accounts (username TEXT, password TEXT)")
sec.execute("INSERT INTO accounts VALUES ('admin', 's3cr3t')")
sec.execute("INSERT INTO accounts VALUES ('guest', 'guest123')")


def login_unsafe(username, password):
    # BAD: values are glued into the SQL text with an f-string.
    sql = f"SELECT username FROM accounts WHERE username = '{username}' AND password = '{password}'"
    return sec.execute(sql).fetchall(), sql


def login_safe(username, password):
    # GOOD: placeholders. The values can never become SQL syntax.
    sql = "SELECT username FROM accounts WHERE username = ? AND password = ?"
    return sec.execute(sql, (username, password)).fetchall(), sql


attack_user = "admin"
attack_pass = "' OR '1'='1"  # classic: makes the WHERE clause always true

rows, sql = login_unsafe(attack_user, attack_pass)
print("UNSAFE sql sent to the db:", sql)
print("UNSAFE result (login bypassed!):", rows)

rows, sql = login_safe(attack_user, attack_pass)
print("SAFE   sql sent to the db:", sql)
print("SAFE   result:", rows, "(no match - the quote was treated as plain text)")
print("SAFE   real login works:", login_safe("admin", "s3cr3t")[0])

# A second classic: "stacked queries" ('; DROP TABLE ...'). sqlite3's execute()
# refuses more than one statement, which blocks THIS particular trick - but do
# not rely on that; the OR '1'='1' attack above needed no second statement.
try:
    sec.execute("SELECT * FROM accounts WHERE username = 'x'; DROP TABLE accounts")
except (sqlite3.ProgrammingError, sqlite3.Warning) as e:
    print("execute() refuses 2 statements ->", type(e).__name__ + ":", e)
sec.close()

# 08. row_factory - rows you can access by NAME
# ------------------------------------
# - By default rows are plain tuples: row[2] - easy to get the index wrong.
# - conn.row_factory = sqlite3.Row  -> rows support row["name"] AND row[0],
#   plus .keys(). Case-insensitive column names. Cheap and built in.
# - For real dicts: use your own factory function.
print("\n# 08. row_factory")
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT id, name, age FROM users WHERE name = ?", ("Asha",)).fetchone()
print("row['name'] =", row["name"], "| row[0] =", row[0], "| keys =", row.keys())
print("dict(row)   =", dict(row))


def dict_factory(cursor, row):
    # cursor.description gives the column names, zip them with the values.
    return {col[0]: value for col, value in zip(cursor.description, row)}


conn.row_factory = dict_factory
print("dict rows:", conn.execute("SELECT id, name FROM users ORDER BY id LIMIT 2").fetchall())
conn.row_factory = None  # back to plain tuples

# 09. Transactions - commit() and rollback()
# ------------------------------------
# - A transaction groups changes: either ALL of them are saved (commit) or NONE
#   (rollback). Classic example: moving money - debit and credit must both happen.
# - Python's sqlite3 (default "legacy" mode) opens a transaction automatically
#   before INSERT/UPDATE/DELETE. It stays open until you commit() or rollback().
# - conn.in_transaction tells you if one is open right now.
# - Forgetting commit() = your changes vanish when the connection closes.
print("\n# 09. Transactions - commit() and rollback()")
bank = sqlite3.connect(":memory:")
bank.execute("CREATE TABLE wallet (owner TEXT PRIMARY KEY, balance INTEGER CHECK (balance >= 0))")
bank.executemany("INSERT INTO wallet VALUES (?, ?)", [("A", 100), ("B", 50)])
bank.commit()
print("in_transaction after commit:", bank.in_transaction)

bank.execute("UPDATE wallet SET balance = balance - 30 WHERE owner = 'A'")
print("in_transaction after an UPDATE:", bank.in_transaction)
bank.rollback()  # change my mind
print("after rollback:", bank.execute("SELECT * FROM wallet ORDER BY owner").fetchall())


def transfer(connection, src, dst, amount):
    # `with connection:` -> commit if the block succeeds, rollback if it raises.
    with connection:
        connection.execute("UPDATE wallet SET balance = balance + ? WHERE owner = ?", (amount, dst))
        connection.execute("UPDATE wallet SET balance = balance - ? WHERE owner = ?", (amount, src))


transfer(bank, "A", "B", 40)
print("after transfer 40 A->B:", bank.execute("SELECT * FROM wallet ORDER BY owner").fetchall())
try:
    transfer(bank, "A", "B", 500)  # A only has 60 -> CHECK constraint fails halfway
except sqlite3.IntegrityError as e:
    print("transfer 500 failed ->", e)
print("balances unchanged (the half-done credit was rolled back):",
      bank.execute("SELECT * FROM wallet ORDER BY owner").fetchall())

# Seeing that uncommitted data is private to the writing connection:
tx_path = os.path.join(tmp.name, "tx.db")
writer = sqlite3.connect(tx_path)
reader = sqlite3.connect(tx_path)
writer.execute("CREATE TABLE log (msg TEXT)")
writer.commit()
writer.execute("INSERT INTO log VALUES ('pending')")
print("reader sees (before writer commits):", reader.execute("SELECT COUNT(*) FROM log").fetchone()[0])
writer.commit()
print("reader sees (after writer commits) :", reader.execute("SELECT COUNT(*) FROM log").fetchone()[0])
writer.close()
reader.close()
bank.close()

# 10. The connection as a context manager does NOT close it
# ------------------------------------
# - `with sqlite3.connect(...) as conn:` manages the TRANSACTION (commit/rollback),
#   not the connection's lifetime. After the block the connection is still open!
# - Use contextlib.closing(...) to really close it. Combine both for full safety.
print("\n# 10. 'with conn' commits but does NOT close")
c = sqlite3.connect(":memory:")
with c:
    c.execute("CREATE TABLE t (x)")
    c.execute("INSERT INTO t VALUES (1)")
print("still usable after the with-block:", c.execute("SELECT x FROM t").fetchall())
c.close()
try:
    c.execute("SELECT 1")
except sqlite3.ProgrammingError as e:
    print("after close() ->", type(e).__name__ + ":", e)

with closing(sqlite3.connect(":memory:")) as c2:  # closes on exit
    with c2:  # commits / rolls back on exit
        c2.execute("CREATE TABLE t (x)")
        c2.execute("INSERT INTO t VALUES (42)")
    print("closing + with pattern:", c2.execute("SELECT x FROM t").fetchone())
try:
    c2.execute("SELECT 1")
except sqlite3.ProgrammingError as e:
    print("c2 really closed ->", type(e).__name__)

# 11. isolation_level and autocommit
# ------------------------------------
# - isolation_level controls WHEN Python issues BEGIN:
#     "" / "DEFERRED" (default) : auto-BEGIN before INSERT/UPDATE/DELETE
#     "IMMEDIATE" / "EXCLUSIVE" : take the write lock right at BEGIN
#     None                      : never auto-BEGIN (autocommit); you write
#                                 BEGIN / COMMIT yourself
# - Python 3.12 added the `autocommit` attribute, which is the modern, PEP 249
#   compliant switch. Default is the legacy behaviour above.
print("\n# 11. isolation_level and autocommit")
with closing(sqlite3.connect(":memory:")) as c3:
    print("default isolation_level:", repr(c3.isolation_level))
    c3.isolation_level = None  # manual transaction control
    c3.execute("CREATE TABLE t (x)")
    c3.execute("BEGIN")
    c3.execute("INSERT INTO t VALUES (1)")
    print("manual BEGIN -> in_transaction:", c3.in_transaction)
    c3.execute("ROLLBACK")
    print("rows after manual ROLLBACK:", c3.execute("SELECT COUNT(*) FROM t").fetchone()[0])

if sys.version_info >= (3, 12):
    with closing(sqlite3.connect(":memory:", autocommit=True)) as c4:
        print("autocommit =", c4.autocommit)
        c4.execute("CREATE TABLE t (x)")
        c4.execute("INSERT INTO t VALUES (1)")
        print("in_transaction (autocommit=True keeps it False):", c4.in_transaction)
    with closing(sqlite3.connect(":memory:")) as c5:
        print("default autocommit is LEGACY:", c5.autocommit == sqlite3.LEGACY_TRANSACTION_CONTROL)
else:
    print("skipped: the autocommit attribute needs Python 3.12+ (you have", sys.version.split()[0] + ")")

# 12. Types, adapters and converters
# ------------------------------------
# - SQLite natively stores only: NULL, INTEGER, REAL, TEXT, BLOB.
#   Python None/int/float/str/bytes map straight onto them.
# - Everything else (datetime, Decimal, your own classes) needs
#     ADAPTER   : Python object -> something SQLite can store  (on the way IN)
#     CONVERTER : stored bytes  -> Python object               (on the way OUT)
# - Converters only run if you connect with detect_types=...
#     PARSE_DECLTYPES : use the declared column type (CREATE TABLE ... ts TIMESTAMP)
#     PARSE_COLNAMES  : use a tag in the query:  SELECT ts AS "ts [timestamp]"
# - Python 3.12 DEPRECATED the built-in default datetime/date adapters and
#   converters (they warn). The fix is simple: register your own - then the
#   deprecated defaults are never used. Registration is process-wide.
print("\n# 12. Types, adapters and converters")


def adapt_datetime(dt):
    return dt.isoformat(" ")  # "2024-05-01 10:30:00"


def convert_timestamp(raw_bytes):
    return datetime.datetime.fromisoformat(raw_bytes.decode())


def adapt_date(d):
    return d.isoformat()


def convert_date(raw_bytes):
    return datetime.date.fromisoformat(raw_bytes.decode())


sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("timestamp", convert_timestamp)  # converter names are case-insensitive
sqlite3.register_converter("date", convert_date)

with warnings.catch_warnings():
    warnings.simplefilter("error")  # turn any DeprecationWarning into a failure: prove we avoid them
    with closing(sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)) as tc:
        tc.execute("CREATE TABLE events (name TEXT, happened_at TIMESTAMP, day DATE)")
        moment = datetime.datetime(2024, 5, 1, 10, 30, 0)
        tc.execute("INSERT INTO events VALUES (?, ?, ?)", ("launch", moment, moment.date()))
        raw = tc.execute("SELECT typeof(happened_at), happened_at FROM events").fetchone()
        print("stored inside sqlite as:", raw)  # typeof shows TEXT -> converter ran on the 2nd value
        name, when, day = tc.execute("SELECT name, happened_at, day FROM events").fetchone()
        print("read back (python objects):", repr(when), repr(day))
        print("arithmetic works on it:", when + datetime.timedelta(days=1))
        # PARSE_COLNAMES: tag a computed column so it is converted too
        tagged = tc.execute('SELECT happened_at AS "when [timestamp]" FROM events').fetchone()[0]
        print("PARSE_COLNAMES result:", repr(tagged))
print("no DeprecationWarning raised (we registered our own adapters)")

# Dynamic typing gotcha: SQLite columns have "affinity", not strict types.
with closing(sqlite3.connect(":memory:")) as tc2:
    tc2.execute("CREATE TABLE loose (n INTEGER)")
    tc2.execute("INSERT INTO loose VALUES ('not a number')")  # accepted!
    print("loose INTEGER column accepts text:", tc2.execute("SELECT n, typeof(n) FROM loose").fetchone())
    if sqlite3.sqlite_version_info >= (3, 37, 0):
        tc2.execute("CREATE TABLE strict_t (n INTEGER) STRICT")  # STRICT tables enforce types
        try:
            tc2.execute("INSERT INTO strict_t VALUES ('not a number')")
        except sqlite3.IntegrityError as e:
            print("STRICT table rejects it ->", e)
    else:
        print("skipped: STRICT tables need SQLite 3.37+")

# 13. Custom SQL functions - create_function and create_aggregate
# ------------------------------------
# - You can teach SQL new tricks by registering Python functions.
# - create_function(name, num_args, func)  : scalar, one value per row
#       (deterministic=True lets SQLite cache/optimise it - only if it is pure)
# - create_aggregate(name, num_args, cls)  : like SUM/AVG; class with
#       step(value) called per row and finalize() called once at the end.
print("\n# 13. create_function and create_aggregate")


def initials(full_name):
    return "".join(part[0].upper() for part in full_name.split())


class Median:
    def __init__(self):
        self.values = []

    def step(self, value):  # called once per row
        if value is not None:
            self.values.append(value)

    def finalize(self):  # called once at the end -> the result
        if not self.values:
            return None
        vals = sorted(self.values)
        mid = len(vals) // 2
        return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


conn.create_function("initials", 1, initials, deterministic=True)
conn.create_aggregate("median", 1, Median)
print("custom scalar:", conn.execute("SELECT name, initials(name || ' Kumar') FROM users ORDER BY id LIMIT 3").fetchall())
print("custom aggregate median(age):", conn.execute("SELECT median(age) FROM users").fetchone()[0])
print("built-in avg(age)           :", conn.execute("SELECT avg(age) FROM users").fetchone()[0])
print("(there is also create_window_function for OVER (...) style functions)")

# 14. Foreign keys are OFF by default
# ------------------------------------
# - SQLite parses FOREIGN KEY clauses but does NOT enforce them unless you run
#   PRAGMA foreign_keys = ON - and it must be run on EVERY new connection
#   (it is per-connection, and a no-op inside an open transaction).
print("\n# 14. Foreign keys need PRAGMA foreign_keys=ON")
fk = sqlite3.connect(":memory:")
fk.executescript(
    """
    CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE
    );
    INSERT INTO authors VALUES (1, 'Tagore');
    """
)
print("default foreign_keys:", fk.execute("PRAGMA foreign_keys").fetchone()[0])
fk.execute("INSERT INTO books (title, author_id) VALUES ('Orphan book', 999)")  # author 999 does not exist!
print("orphan row accepted silently:", fk.execute("SELECT title, author_id FROM books").fetchall())
fk.execute("DELETE FROM books")
fk.commit()

fk.execute("PRAGMA foreign_keys = ON")
print("after PRAGMA ON:", fk.execute("PRAGMA foreign_keys").fetchone()[0])
try:
    fk.execute("INSERT INTO books (title, author_id) VALUES ('Orphan book', 999)")
except sqlite3.IntegrityError as e:
    print("now rejected ->", type(e).__name__ + ":", e)
fk.execute("INSERT INTO books (title, author_id) VALUES ('Gitanjali', 1)")
fk.execute("DELETE FROM authors WHERE id = 1")  # ON DELETE CASCADE removes the book too
print("books after deleting author (cascade):", fk.execute("SELECT COUNT(*) FROM books").fetchone()[0])
fk.close()

# 15. Exceptions - the sqlite3 hierarchy
# ------------------------------------
# - Exception
#     sqlite3.Warning
#     sqlite3.Error
#         InterfaceError          misuse of the API itself
#         DatabaseError
#             DataError           bad data (e.g. value too big)
#             OperationalError    db-level trouble: no such table, db locked, syntax error
#             IntegrityError      constraint broken: UNIQUE, NOT NULL, FOREIGN KEY, CHECK
#             InternalError       sqlite internal problem
#             ProgrammingError    your bug: wrong param count, closed connection
#             NotSupportedError   feature not available
# - Catch the SPECIFIC one you can handle; catch sqlite3.Error as a last resort.
print("\n# 15. Exceptions hierarchy")
for cls in (sqlite3.IntegrityError, sqlite3.OperationalError, sqlite3.ProgrammingError):
    print(" ", cls.__name__, "->", " > ".join(k.__name__ for k in reversed(cls.__mro__[:-2])))

try:
    conn.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Clone", "asha@example.com", 1))
except sqlite3.IntegrityError as e:
    print("UNIQUE violation  ->", e)
try:
    conn.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (None, "x@example.com", 1))
except sqlite3.IntegrityError as e:
    print("NOT NULL violation ->", e)
try:
    conn.execute("SELECT * FROM no_such_table")
except sqlite3.OperationalError as e:
    print("OperationalError  ->", e)
try:
    conn.execute("SELEC 1")
except sqlite3.OperationalError as e:
    print("syntax error      ->", e)
try:
    conn.execute("SELECT * FROM users WHERE id = ? AND age = ?", (1,))
except sqlite3.ProgrammingError as e:
    print("wrong param count ->", e)
conn.rollback()  # clean slate after the failed statements

# 16. PRAGMA basics
# ------------------------------------
# - PRAGMA = SQLite's own settings/inspection commands (not standard SQL).
#     table_info(t)    : columns of a table (cid, name, type, notnull, default, pk)
#     table_list       : tables (3.37+), or query sqlite_master (works everywhere)
#     journal_mode     : how SQLite protects data. DELETE (default) or WAL
#                        (readers don't block the writer - good for web apps).
#     foreign_keys     : see above
#     user_version     : a free integer slot for YOU (used for migrations below)
print("\n# 16. PRAGMA basics")
print("table_info(users):")
for col in conn.execute("PRAGMA table_info(users)"):
    print("  ", col)
print("tables via sqlite_master:", [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print("journal_mode (memory db):", conn.execute("PRAGMA journal_mode").fetchone()[0])

wal_path = os.path.join(tmp.name, "wal.db")
with closing(sqlite3.connect(wal_path)) as wc:
    print("journal_mode (new file db):", wc.execute("PRAGMA journal_mode").fetchone()[0])
    print("switched to:", wc.execute("PRAGMA journal_mode = WAL").fetchone()[0], "(this setting is remembered in the file)")

# 17. executescript() - and its commit gotcha
# ------------------------------------
# - executescript(sql_text) runs MANY statements separated by ';' in one call.
#   Great for schema setup and migrations written as .sql files.
# - GOTCHAS:
#     1. It first COMMITS any transaction that is already open (legacy mode) -
#        so it can silently save things you meant to roll back.
#     2. It takes NO parameters - never build the script from user input.
print("\n# 17. executescript() commit gotcha")
with closing(sqlite3.connect(":memory:")) as sc:
    sc.execute("CREATE TABLE t (x)")
    sc.execute("INSERT INTO t VALUES (1)")  # opens a transaction (uncommitted)
    print("before executescript, in_transaction:", sc.in_transaction)
    sc.executescript("CREATE TABLE other (y);")  # implicit COMMIT first!
    print("after  executescript, in_transaction:", sc.in_transaction)
    sc.rollback()  # too late - the INSERT was already committed
    print("rollback did not undo the insert:", sc.execute("SELECT x FROM t").fetchall())

# 18. Simple migrations with PRAGMA user_version
# ------------------------------------
# - Real apps change their schema over time. A migration = a numbered list of
#   changes applied in order, remembering which ones already ran.
# - SQLite gives you one spare integer in the file header: PRAGMA user_version.
#   Store the schema version there; on startup, apply any newer migrations.
# - SQLite DDL is transactional, so each step can be all-or-nothing.
# - PRAGMA values cannot be parameterized -> format an int (never user text).
print("\n# 18. Migrations with PRAGMA user_version")
MIGRATIONS = [
    # (version, [statements])
    (1, ["CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"]),
    (2, ["ALTER TABLE members ADD COLUMN email TEXT"]),
    (3, ["CREATE INDEX idx_members_name ON members(name)",
         "INSERT INTO members (name, email) VALUES ('seed', 'seed@example.com')"]),
]


def migrate(connection):
    current = connection.execute("PRAGMA user_version").fetchone()[0]
    for version, statements in MIGRATIONS:
        if version <= current:
            continue
        with connection:  # one transaction per migration step
            for stmt in statements:
                connection.execute(stmt)
            connection.execute(f"PRAGMA user_version = {int(version)}")
        print(f"  applied migration {version}")
    return connection.execute("PRAGMA user_version").fetchone()[0]


mig_path = os.path.join(tmp.name, "migrate.db")
with closing(sqlite3.connect(mig_path)) as mc:
    print("fresh db version:", mc.execute("PRAGMA user_version").fetchone()[0])
    print("after first migrate():", migrate(mc))
    print("second migrate() (nothing to do):", migrate(mc))
    print("columns now:", [r[1] for r in mc.execute("PRAGMA table_info(members)")])

# 19. A tiny repository (DAO) class - CRUD wrapper
# ------------------------------------
# - Repository/DAO pattern: ONE class owns all the SQL for one table. The rest of
#   your app calls repo.add(...), repo.get(...) and never writes SQL.
# - Benefits: SQL in one place, easy to test with ":memory:", easy to swap the
#   storage later.
print("\n# 19. Repository / DAO class")


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    age: int


class UserRepository:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS users (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        age   INTEGER NOT NULL CHECK (age >= 0)
    )
    """

    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        with self.conn:
            self.conn.execute(self.SCHEMA)

    # context-manager support so callers can write: with UserRepository() as repo:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.conn.close()

    @staticmethod
    def _to_user(row):
        return User(**dict(row)) if row else None

    # Create
    def add(self, name, email, age):
        with self.conn:
            cur = self.conn.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age))
        return cur.lastrowid

    # Read
    def get(self, user_id):
        return self._to_user(self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())

    def find_by_email(self, email):
        return self._to_user(self.conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone())

    def list(self, min_age=0):
        rows = self.conn.execute("SELECT * FROM users WHERE age >= ? ORDER BY id", (min_age,))
        return [self._to_user(r) for r in rows]

    # Update
    def update_age(self, user_id, age):
        with self.conn:
            cur = self.conn.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))
        return cur.rowcount == 1  # True if a row was really changed

    # Delete
    def delete(self, user_id):
        with self.conn:
            cur = self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cur.rowcount == 1


with UserRepository() as repo:
    a = repo.add("Asha", "asha@example.com", 30)
    b = repo.add("Ravi", "ravi@example.com", 25)
    print("added ids:", a, b)
    print("get(1)       :", repo.get(a))
    print("by email     :", repo.find_by_email("ravi@example.com"))
    print("update_age   :", repo.update_age(b, 26), "| unknown id:", repo.update_age(999, 1))
    print("list(min 26) :", repo.list(min_age=26))
    try:
        repo.add("Dup", "asha@example.com", 20)
    except sqlite3.IntegrityError as e:
        print("duplicate email rejected ->", e)
    try:
        repo.add("Baby", "baby@example.com", -5)
    except sqlite3.IntegrityError as e:
        print("CHECK age>=0 rejected    ->", e)
    print("delete       :", repo.delete(a), "| again:", repo.delete(a))
    print("final list   :", [u.name for u in repo.list()])

# 20. Query results into pandas (optional)
# ------------------------------------
# - pandas.read_sql(query, connection) turns a query straight into a DataFrame,
#   and df.to_sql("table", connection) writes one back. See
#   08-Pandas/09-Input-Output.py for the full pandas I/O story.
# - pandas is a third-party package, so this block is guarded.
print("\n# 20. Loading query results into pandas (guarded)")
try:
    import pandas as pd
except ImportError:
    print("skipped: pandas is not installed (pip install pandas) - see 08-Pandas/09-Input-Output.py")
else:
    df = pd.read_sql("SELECT name, age FROM users ORDER BY age DESC", conn)
    print(df)
    print("mean age via pandas:", df["age"].mean())

# 21. Cleanup
# ------------------------------------
# - Always close what you open, and remove temp files.
conn.close()
tmp.cleanup()
print("\n# 21. Cleanup done - temp directory removed:", not os.path.exists(db_path))

# 22. Summary - which tool for which job
# ------------------------------------
# - One value into SQL            -> "?" placeholder, always
# - Many rows at once             -> executemany()
# - Read all rows                 -> fetchall() (small) / iterate the cursor (big)
# - Access columns by name        -> row_factory = sqlite3.Row
# - All-or-nothing changes        -> `with conn:` (commit / rollback)
# - Really close the connection   -> contextlib.closing(conn)
# - datetime / custom types       -> register_adapter + register_converter + detect_types
# - Enforce relations             -> PRAGMA foreign_keys = ON (every connection!)
# - Schema versioning             -> PRAGMA user_version
# - Heavy analysis / many users   -> use a client-server DB (PostgreSQL) - SQLite is
#                                    superb for one-writer-at-a-time workloads
