# 01. Engine and Connection
# 02. text(): Raw SQL with Bound Parameters
# 03. MetaData and Table
# 04. Core insert()
# 05. Core select(): where, order_by, limit
# 06. Core Joins, Aggregates, group_by
# 07. Core update() and delete()
# 08. ORM Models: DeclarativeBase, Mapped, mapped_column
# 09. Session and the Unit of Work
# 10. ORM select(): scalars, where, get
# 11. Relationships: One-to-Many
# 12. Relationships: Many-to-Many
# 13. Joins in the ORM
# 14. Lazy Loading and the N+1 Problem
# 15. Eager Loading: selectinload and joinedload
# 16. Transactions: begin, commit, rollback
# 17. Bulk Operations
# 18. Hybrid Properties
# 19. Connection Pooling Notes
# 20. Migrations with Alembic (Notes)
#
# SQLAlchemy 2.0 style only (select(), Session, Mapped[]). No legacy
# session.query(). Everything uses in-memory SQLite, so nothing is left
# on disk. Compare with the stdlib driver in 05-SQLite-With-Python.py.

try:
    import sqlalchemy as sa
    from sqlalchemy import ForeignKey, String, event, func, select, text
    from sqlalchemy.ext.hybrid import hybrid_property
    from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, joinedload,
                                mapped_column, relationship, selectinload)
    HAVE_SA = True
except ImportError:
    HAVE_SA = False
    print("sqlalchemy not installed: skipping every section (pip install sqlalchemy)")

if HAVE_SA:
    print("SQLAlchemy major version:", sa.__version__.split(".")[0])

# 01. Engine and Connection
# ----------------------------
# - create_engine(url) describes HOW to reach a database; it connects
#   lazily on first use. The engine owns a connection pool.
# - "sqlite://" (no path) = in-memory SQLite. echo=True would log SQL.
# - engine.connect() gives a Connection; use it in a "with" block.
# - 2.0 style: connections do NOT autocommit. Call conn.commit() or use
#   engine.begin() which commits for you at the end of the block.

if HAVE_SA:
    engine = sa.create_engine("sqlite://")
    print("dialect:", engine.dialect.name, "| url:", engine.url)
    with engine.connect() as conn:
        print("SELECT 1 ->", conn.execute(text("SELECT 1")).scalar())
    print("# Gotcha: forgetting conn.commit() means your INSERT is rolled back when the block ends.")

# 02. text(): Raw SQL with Bound Parameters
# ----------------------------
# - text("... :name ...") wraps raw SQL. Values go in a dict as
#   :named bind parameters - the same injection-safe idea as ? in sqlite3.
# - Results are Row objects: tuple-like with attribute access
#   (row.label) and row._mapping for dict-style access.
# - A list of dicts passed to execute() runs as executemany.
# - With in-memory SQLite, SQLAlchemy uses a pool that keeps ONE
#   connection, so every checkout sees the same database.

if HAVE_SA:
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE raw_demo (id INTEGER PRIMARY KEY, label TEXT)"))
        conn.execute(text("INSERT INTO raw_demo (label) VALUES (:label)"), [{"label": "a"}, {"label": "b"}, {"label": "c"}])
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, label FROM raw_demo WHERE id >= :min ORDER BY id"), {"min": 2}).all()
        print("rows:", rows)
        print("attribute access:", rows[0].label, "| mapping:", dict(rows[0]._mapping))
        print("keys:", list(rows[0]._mapping.keys()))
        evil = "a' OR '1'='1"
        print("injection attempt returns:", conn.execute(text("SELECT * FROM raw_demo WHERE label = :v"), {"v": evil}).all())

# 03. MetaData and Table
# ----------------------------
# - Core describes tables as Python objects: MetaData holds Table
#   objects, each with Column(name, type, ...).
# - metadata.create_all(engine) emits CREATE TABLE (skips ones that
#   already exist). drop_all removes them.
# - table.c.name (or table.c["name"]) is the column collection used to
#   build expressions.
# - Reflection (Table("x", md, autoload_with=engine)) reads an existing
#   schema instead; sa.inspect(engine) lists tables and columns.

if HAVE_SA:
    metadata = sa.MetaData()
    users = sa.Table(
        "users", metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("age", sa.Integer),
    )
    orders = sa.Table(
        "orders", metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    metadata.create_all(engine)
    print("tables:", sorted(metadata.tables))
    print("columns of users:", [c.name for c in users.c])
    print("reflected:", [c["name"] for c in sa.inspect(engine).get_columns("orders")])

# 04. Core insert()
# ----------------------------
# - insert(table).values(...) builds the statement; execute it with
#   a connection. Passing a LIST of dicts to execute() runs an
#   executemany (fast bulk insert).
# - result.inserted_primary_key gives the new id for a single insert.
# - Printing a statement shows the SQL with :bind placeholders.

if HAVE_SA:
    print("SQL text:", str(sa.insert(users).values(name="x", age=1)))
    with engine.begin() as conn:
        r = conn.execute(sa.insert(users).values(name="Asha", age=30))
        print("inserted_primary_key:", r.inserted_primary_key)
        conn.execute(sa.insert(users), [{"name": "Ben", "age": 25}, {"name": "Chitra", "age": 41}, {"name": "Dev", "age": 19}])
        conn.execute(sa.insert(orders), [
            {"user_id": 1, "amount": 10.50}, {"user_id": 1, "amount": 20},
            {"user_id": 2, "amount": 5}, {"user_id": 3, "amount": 99.99},
        ])
    with engine.connect() as conn:
        print("user count:", conn.execute(select(func.count()).select_from(users)).scalar())

# 05. Core select(): where, order_by, limit
# ----------------------------
# - select(table) or select(table.c.col1, table.c.col2).
# - Python operators build SQL: == != < > & (AND) | (OR) ~ (NOT).
#   Use & and | with parentheses - NOT Python's and/or.
# - Column helpers: .like(), .in_(), .between(), .is_(None), .desc().
# - Result helpers: .all(), .first(), .one(), .scalars(), .mappings().

if HAVE_SA:
    with engine.connect() as conn:
        stmt = select(users.c.name, users.c.age).where(users.c.age > 20).order_by(users.c.age.desc()).limit(2)
        print("SQL:", " ".join(str(stmt).split()))
        print("rows:", conn.execute(stmt).all())
        print("OR:", conn.execute(select(users.c.name).where((users.c.age < 26) | (users.c.name == "Chitra")).order_by(users.c.id)).scalars().all())
        print("in_ + like:", conn.execute(select(users.c.name).where(users.c.name.in_(["Ben", "Dev"]), users.c.name.like("D%"))).scalars().all())
        print("mappings:", dict(conn.execute(select(users.c.id, users.c.name).where(users.c.id == 1)).mappings().one()))
        print("first() on no match:", conn.execute(select(users).where(users.c.id == 999)).first())
    print("# Gotcha: 'a and b' on SQL expressions raises TypeError - use & / | (with parentheses) or where(a, b).")

# 06. Core Joins, Aggregates, group_by
# ----------------------------
# - select(...).join(other, onclause) - SQLAlchemy can infer the ON
#   clause from the ForeignKey.
# - func.sum / func.count / func.avg make SQL functions; .label() names
#   the output column.
# - outerjoin keeps rows with no match (like SQL LEFT JOIN).
# - Numeric columns come back as Decimal (exact money-style maths).

if HAVE_SA:
    with engine.connect() as conn:
        total = func.sum(orders.c.amount).label("total")
        stmt = select(users.c.name, total).join(orders, orders.c.user_id == users.c.id).group_by(users.c.name).order_by(users.c.name)
        print("inner join totals:", [(n, float(t)) for n, t in conn.execute(stmt)])
        stmt = (select(users.c.name, func.count(orders.c.id).label("n")).outerjoin(orders, orders.c.user_id == users.c.id)
                .group_by(users.c.name).having(func.count(orders.c.id) == 0))
        print("users with no orders:", conn.execute(stmt).all())
        print("amount python type:", type(conn.execute(select(orders.c.amount).limit(1)).scalar()).__name__)

# 07. Core update() and delete()
# ----------------------------
# - update(table).where(...).values(...) and delete(table).where(...).
# - result.rowcount tells how many rows changed.
# - Forgetting .where() changes EVERY row - SQL does what you ask.
# - Expressions work inside values(): values(age=users.c.age + 1).

if HAVE_SA:
    with engine.begin() as conn:
        r = conn.execute(sa.update(users).where(users.c.name == "Dev").values(age=users.c.age + 1))
        print("updated rows:", r.rowcount, "| Dev age now:", conn.execute(select(users.c.age).where(users.c.name == "Dev")).scalar())
        r = conn.execute(sa.delete(orders).where(orders.c.amount < 6))
        print("deleted rows:", r.rowcount)
        r = conn.execute(sa.update(users).where(users.c.id == 999).values(age=0))
        print("no-match update rowcount:", r.rowcount)

# 08. ORM Models: DeclarativeBase, Mapped, mapped_column
# ----------------------------
# - 2.0 ORM: subclass DeclarativeBase, then declare columns with
#   Mapped[type] annotations and mapped_column().
# - Mapped[str] = NOT NULL; Mapped[str | None] = nullable.
#   mapped_column(...) adds types, keys, defaults, unique, indexes.
# - Base.metadata.create_all(engine) creates the tables.
# - The ORM here uses its own Base.metadata, separate from the Core
#   MetaData above.

if HAVE_SA:
    class Base(DeclarativeBase):
        pass

    post_tag = sa.Table(
        "post_tag", Base.metadata,
        sa.Column("post_id", ForeignKey("post.id"), primary_key=True),
        sa.Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    )

    class Author(Base):
        __tablename__ = "author"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50), unique=True)
        bio: Mapped[str | None]
        posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

        def __repr__(self):
            return f"Author({self.name!r})"

    class Post(Base):
        __tablename__ = "post"
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(100))
        words: Mapped[int] = mapped_column(default=0)
        author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
        author: Mapped[Author] = relationship(back_populates="posts")
        tags: Mapped[list["Tag"]] = relationship(secondary=post_tag, back_populates="posts")

        @hybrid_property
        def is_long(self):
            return self.words >= 500

        def __repr__(self):
            return f"Post({self.title!r})"

    class Tag(Base):
        __tablename__ = "tag"
        id: Mapped[int] = mapped_column(primary_key=True)
        label: Mapped[str] = mapped_column(String(30), unique=True)
        posts: Mapped[list[Post]] = relationship(secondary=post_tag, back_populates="tags")

        def __repr__(self):
            return f"Tag({self.label!r})"

    orm_engine = sa.create_engine("sqlite://")
    Base.metadata.create_all(orm_engine)
    print("ORM tables:", sorted(Base.metadata.tables))
    print("Author columns:", [(c.name, str(c.type), c.nullable) for c in Author.__table__.c])

# 09. Session and the Unit of Work
# ----------------------------
# - A Session tracks objects you load or add, and FLUSHES changes to
#   the database as one unit of work when you commit (or autoflush
#   before a query).
# - session.add(obj) marks it pending; no SQL yet. flush() sends SQL
#   (ids get assigned) but doesn't commit. commit() flushes + commits.
# - Changing an attribute of a loaded object is detected automatically
#   (dirty tracking) - no explicit "save" needed.
# - After commit, objects are "expired": next attribute access reloads
#   (expire_on_commit=True default).
# - Use "with Session(engine) as session" so it closes properly.

if HAVE_SA:
    with Session(orm_engine) as session:
        asha = Author(name="Asha")
        print("before add: id =", asha.id, "| in session:", asha in session)
        session.add(asha)
        print("pending:", asha in session.new, "| id still", asha.id)
        session.flush()
        print("after flush: id =", asha.id)
        asha.bio = "writes about Python"
        print("dirty:", asha in session.dirty)
        session.commit()
        print("after commit, state expired?", "bio" not in asha.__dict__, "| reload ->", asha.bio)
    print("# Gotcha: using an expired object after session.close() raises DetachedInstanceError.")

# 10. ORM select(): scalars, where, get
# ----------------------------
# - session.execute(select(Model)) returns Row objects each holding ONE
#   entity; session.scalars(select(Model)) unwraps to the entities
#   directly - almost always what you want.
# - session.get(Model, pk) is a primary-key lookup that first checks
#   the identity map (no SQL if already loaded).
# - Identity map: one Python object per primary key per session.
# - .scalar_one() raises if 0 or many rows; .one_or_none() returns
#   None for 0.

if HAVE_SA:
    with Session(orm_engine) as session:
        session.add_all([Author(name="Ben"), Author(name="Chitra", bio="editor")])
        session.commit()
        print("all:", session.scalars(select(Author).order_by(Author.name)).all())
        print("where:", session.scalars(select(Author).where(Author.bio.is_not(None)).order_by(Author.id)).all())
        print("one_or_none:", session.scalars(select(Author).where(Author.name == "Zed")).one_or_none())
        a1 = session.get(Author, 1)
        print("get(1):", a1, "| same object again?", session.get(Author, 1) is a1)
        print("scalar:", session.scalar(select(Author).where(Author.name == "Ben")).id)
        print("columns only:", session.execute(select(Author.id, Author.name).order_by(Author.id)).all())

# 11. Relationships: One-to-Many
# ----------------------------
# - relationship() lets you navigate objects instead of joining by hand.
#   Author.posts (list) <-> Post.author (single), kept in sync by
#   back_populates.
# - Set either side; SQLAlchemy fills the foreign key at flush time.
# - cascade="all, delete-orphan" means deleting an Author deletes their
#   posts, and removing a post from the list deletes it.

if HAVE_SA:
    with Session(orm_engine) as session:
        asha = session.scalar(select(Author).where(Author.name == "Asha"))
        ben = session.scalar(select(Author).where(Author.name == "Ben"))
        asha.posts.append(Post(title="Intro to Python", words=800))
        asha.posts.append(Post(title="Tips", words=200))
        p = Post(title="Ben's post", words=500, author=ben)
        session.add(p)
        session.commit()
        print("asha.posts:", asha.posts)
        print("p.author:", p.author, "| back-populated:", p in ben.posts)
        print("author_id set by flush:", p.author_id)

# 12. Relationships: Many-to-Many
# ----------------------------
# - Two classes, one association table (post_tag) given as
#   secondary=. Each side holds a list of the other.
# - Append to one side and the link row is inserted for you.
# - If the link carries extra data (e.g. date tagged) use the
#   "association object" pattern instead of plain secondary.

if HAVE_SA:
    with Session(orm_engine) as session:
        py, db = Tag(label="python"), Tag(label="database")
        posts = {p.title: p for p in session.scalars(select(Post))}
        posts["Intro to Python"].tags.extend([py, db])
        posts["Tips"].tags.append(py)
        session.commit()
        print("tags on Intro:", sorted(t.label for t in posts["Intro to Python"].tags))
        print("posts for 'python':", sorted(p.title for p in py.posts))
        print("link rows:", session.execute(select(func.count()).select_from(post_tag)).scalar())

# 13. Joins in the ORM
# ----------------------------
# - select(Post).join(Post.author) joins along the relationship - no
#   ON clause to write.
# - Filter on joined table columns, and group_by to aggregate.
# - join() alone does NOT load the related objects into attributes (it
#   only filters). Use eager loading (section 15) for that.
# - .distinct() may be needed when joins multiply rows.

if HAVE_SA:
    with Session(orm_engine) as session:
        stmt = select(Post.title).join(Post.author).where(Author.name == "Asha").order_by(Post.title)
        print("Asha's posts:", session.scalars(stmt).all())
        stmt = select(Author.name, func.count(Post.id)).join(Author.posts).group_by(Author.name).order_by(Author.name)
        print("posts per author:", session.execute(stmt).all())
        stmt = select(Post.title).join(Post.tags).where(Tag.label.in_(["python", "database"])).distinct().order_by(Post.title)
        print("posts tagged python or database:", session.scalars(stmt).all())
        stmt = select(Author.name).outerjoin(Author.posts).where(Post.id.is_(None))
        print("authors with no posts:", session.scalars(stmt).all())

# 14. Lazy Loading and the N+1 Problem
# ----------------------------
# - Default relationship loading is LAZY: accessing author.posts runs a
#   new SELECT the first time, for each author.
# - Loop over N authors and touch .posts -> 1 query for authors + N for
#   posts = N+1 queries. Fine for 3 rows, painful for 3000.
# - We count statements with an event listener on the engine
#   (before_cursor_execute). This is how you PROVE the problem.

if HAVE_SA:
    class Counter:
        def __init__(self, eng):
            self.n = 0
            self.statements = []
            event.listen(eng, "before_cursor_execute", self._hook)

        def _hook(self, conn, cursor, statement, parameters, context, executemany):
            self.n += 1
            self.statements.append(statement.split()[0])

        def reset(self):
            self.n, self.statements = 0, []

    counter = Counter(orm_engine)
    with Session(orm_engine) as session:
        counter.reset()
        authors = session.scalars(select(Author).order_by(Author.id)).all()
        for a in authors:
            _ = [p.title for p in a.posts]
        print(f"lazy loading: {len(authors)} authors -> {counter.n} statements (1 + N)")

# 15. Eager Loading: selectinload and joinedload
# ----------------------------
# - Eager loading fetches related rows up front with the main query.
# - selectinload(Author.posts): one extra SELECT ... WHERE author_id IN
#   (...) for ALL authors - best for collections (one-to-many,
#   many-to-many). 2 statements total regardless of N.
# - joinedload(Post.author): one JOIN in the same statement - best for
#   many-to-one/one-to-one. For collections it multiplies rows, so
#   call .unique() on the result (2.0 makes you do it).
# - lazy="raise" on a relationship turns accidental lazy loads into
#   errors - a good safety net in production code.
# - Chain for depth: selectinload(Author.posts).selectinload(Post.tags).

if HAVE_SA:
    with Session(orm_engine) as session:
        counter.reset()
        authors = session.scalars(select(Author).options(selectinload(Author.posts)).order_by(Author.id)).all()
        for a in authors:
            _ = [p.title for p in a.posts]
        print("selectinload:", counter.n, "statements:", counter.statements)

    with Session(orm_engine) as session:
        counter.reset()
        posts = session.scalars(select(Post).options(joinedload(Post.author)).order_by(Post.id)).all()
        names = [p.author.name for p in posts]
        print("joinedload many-to-one:", counter.n, "statement ->", names)

    with Session(orm_engine) as session:
        counter.reset()
        try:
            session.scalars(select(Author).options(joinedload(Author.posts))).all()
        except sa.exc.InvalidRequestError as exc:
            print("joinedload collection without unique():", type(exc).__name__)
        authors = session.scalars(select(Author).options(joinedload(Author.posts)).order_by(Author.id)).unique().all()
        print("with unique():", [(a.name, len(a.posts)) for a in authors])

    with Session(orm_engine) as session:
        counter.reset()
        authors = session.scalars(select(Author).options(selectinload(Author.posts).selectinload(Post.tags)).order_by(Author.id)).all()
        tag_labels = sorted({t.label for a in authors for p in a.posts for t in p.tags})
        print("nested eager:", counter.n, "statements | tags:", tag_labels)

# 16. Transactions: begin, commit, rollback
# ----------------------------
# - session.begin() as a context manager commits on success and rolls
#   back on error. Same for engine.begin() in Core.
# - After an exception inside a Session, you MUST rollback before reuse
#   (the session is in a failed state).
# - session.rollback() also discards un-flushed pending objects and
#   expires loaded ones.
# - begin_nested() gives a SAVEPOINT: roll back part of the work only.

if HAVE_SA:
    with Session(orm_engine) as session:
        try:
            with session.begin():
                session.add(Author(name="Temp"))
                session.add(Author(name="Asha"))  # duplicate unique name
        except sa.exc.IntegrityError as exc:
            print("IntegrityError, whole block rolled back:", type(exc.orig).__name__)
        print("'Temp' persisted?", session.scalar(select(Author).where(Author.name == "Temp")) is not None)

    with Session(orm_engine) as session:
        with session.begin():
            session.add(Author(name="Keeper"))
            try:
                with session.begin_nested():
                    session.add(Author(name="Asha"))  # fails inside savepoint
                    session.flush()
            except sa.exc.IntegrityError:
                print("savepoint rolled back, outer transaction continues")
        print("Keeper persisted:", session.scalar(select(Author).where(Author.name == "Keeper")) is not None)

# 17. Bulk Operations
# ----------------------------
# - Adding thousands of ORM objects one by one is slow-ish; 2.0 offers
#   Core-style bulk: session.execute(insert(Model), [dicts...]) uses
#   executemany ("insertmanyvalues") and skips object creation.
# - Bulk UPDATE/DELETE with where(): one statement, no per-object
#   loading. synchronize_session controls what happens to objects
#   already in memory (default "auto" works in most cases).
# - Trade-off: bulk statements bypass relationship cascades and
#   Python-side events/validators.

if HAVE_SA:
    with Session(orm_engine) as session:
        counter.reset()
        session.execute(sa.insert(Tag), [{"label": f"bulk{i}"} for i in range(100)])
        session.commit()
        print("bulk insert 100 tags -> tag count:", session.scalar(select(func.count()).select_from(Tag)), "| statements issued < 100:", counter.n < 100)
        res = session.execute(sa.update(Post).where(Post.words < 300).values(words=Post.words + 1))
        print("bulk update rowcount:", res.rowcount)
        res = session.execute(sa.delete(Tag).where(Tag.label.like("bulk%")))
        session.commit()
        print("bulk delete rowcount:", res.rowcount, "| tags left:", session.scalar(select(func.count()).select_from(Tag)))

# 18. Hybrid Properties
# ----------------------------
# - @hybrid_property works on BOTH levels: on an instance it runs
#   plain Python (post.is_long), on the class it produces an SQL
#   expression (Post.is_long) usable in where().
# - Keep the expression simple; if Python and SQL logic must differ,
#   add a separate @is_long.expression function.
# - Great for computed fields you want to filter by without
#   duplicating the rule.

if HAVE_SA:
    with Session(orm_engine) as session:
        long_posts = session.scalars(select(Post).where(Post.is_long).order_by(Post.title)).all()
        print("long posts via SQL:", long_posts)
        print("instance level:", [(p.title, p.is_long) for p in session.scalars(select(Post).order_by(Post.id))])
        print("class level SQL:", " ".join(str(select(Post.id).where(Post.is_long)).split()))

# 19. Connection Pooling Notes
# ----------------------------
# - The Engine keeps a POOL of open connections so each request doesn't
#   pay the connect cost. Checking out = borrowing; closing a
#   connection/session RETURNS it to the pool.
# - For server databases (PostgreSQL, MySQL): QueuePool with pool_size,
#   max_overflow, pool_timeout; pool_pre_ping=True detects dead
#   connections; pool_recycle avoids server-side idle timeouts.
# - SQLite in-memory keeps a single shared connection, so all code sees
#   the same db; for file databases in threads, one connection per
#   thread is the safe pattern.
# - One Engine per database per process - create it once, reuse it.
#   Never share a Session across threads.
# - engine.dispose() closes pooled connections (e.g. after fork).
# - Typical server config (not run here):
#   create_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=1800)

if HAVE_SA:
    print("pool class (in-memory sqlite):", type(orm_engine.pool).__name__)
    mem_engine = sa.create_engine("sqlite://", pool_pre_ping=True)
    with mem_engine.connect() as c1:
        c1.execute(text("CREATE TABLE z (x INT)"))
        c1.commit()
    with mem_engine.connect() as c2:
        print("second checkout sees same in-memory db:", c2.execute(text("SELECT name FROM sqlite_master")).scalars().all())
    mem_engine.dispose()

# 20. Migrations with Alembic (Notes)
# ----------------------------
# - create_all() only creates MISSING tables; it never alters existing
#   ones. Real projects need migrations for schema changes.
# - Alembic (by the SQLAlchemy author) tracks revisions:
#     alembic init migrations
#     alembic revision --autogenerate -m "add bio column"
#     alembic upgrade head        # apply
#     alembic downgrade -1        # undo one step
# - Autogenerate compares your models to the database and writes a
#   draft; ALWAYS review it (renames look like drop+add).
# - SQLite has limited ALTER TABLE; Alembic uses "batch mode" to
#   recreate tables.
# - Same idea as the PRAGMA user_version pattern in the sqlite3 file,
#   just with tooling.

if HAVE_SA:
    print("alembic is only described in comments here; it is never imported")
    orm_engine.dispose()
    engine.dispose()
    print("engines disposed")
