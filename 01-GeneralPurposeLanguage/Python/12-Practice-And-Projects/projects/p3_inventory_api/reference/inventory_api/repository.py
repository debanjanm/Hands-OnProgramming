"""sqlite3 storage. No FastAPI in here, so it can be tested on its own."""
import sqlite3

from .models import MAX_SQLITE_INT, MIN_SQLITE_INT


class NotFound(Exception):
    """No product with that id."""


class Conflict(Exception):
    """The change clashes with existing data (e.g. duplicate sku)."""


class InsufficientStock(Conflict):
    """A stock adjustment would make stock negative."""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    sku      TEXT    NOT NULL UNIQUE,
    price    REAL    NOT NULL CHECK (price >= 0),
    stock    INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category TEXT
)
"""
_COLUMNS = {"name", "sku", "price", "stock", "category"}


class ProductRepository:
    """CRUD + search + stock adjustments for products."""

    def __init__(self, db_path: str = ":memory:") -> None:
        # check_same_thread=False: FastAPI runs sync endpoints in a thread pool.
        # ponytail: one shared connection, add a lock or a pool for real concurrency.
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute(_SCHEMA)
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def create(self, **fields) -> dict:
        """Insert a product and return it (with its new id). Duplicate sku -> Conflict."""
        try:
            cur = self._db.execute(
                "INSERT INTO products (name, sku, price, stock, category) "
                "VALUES (:name, :sku, :price, :stock, :category)",
                {"stock": 0, "category": None, **fields},
            )
            self._db.commit()
        except sqlite3.IntegrityError as exc:
            self._db.rollback()
            raise Conflict(f"sku {fields.get('sku')!r} already exists") from exc
        return self.get(cur.lastrowid)

    def get(self, product_id: int) -> dict:
        row = self._db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if row is None:
            raise NotFound(f"product {product_id} not found")
        return dict(row)

    def list(self, q: str | None = None, category: str | None = None,
             min_price: float | None = None, max_price: float | None = None,
             limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
        """Return (items on this page, total matches). `q` matches name or sku, case-insensitive."""
        where, args = [], []
        if q:
            where.append("(name LIKE ? OR sku LIKE ?)")
            args += [f"%{q}%", f"%{q}%"]
        if category is not None:
            where.append("category = ?")
            args.append(category)
        if min_price is not None:
            where.append("price >= ?")
            args.append(min_price)
        if max_price is not None:
            where.append("price <= ?")
            args.append(max_price)
        clause = f" WHERE {' AND '.join(where)}" if where else ""
        total = self._db.execute(f"SELECT COUNT(*) FROM products{clause}", args).fetchone()[0]
        rows = self._db.execute(
            f"SELECT * FROM products{clause} ORDER BY id LIMIT ? OFFSET ?", [*args, limit, offset]
        ).fetchall()
        return [dict(r) for r in rows], total

    def update(self, product_id: int, **fields) -> dict:
        """Change some columns (not stock). Unknown id -> NotFound, duplicate sku -> Conflict."""
        self.get(product_id)
        fields = {k: v for k, v in fields.items() if k in _COLUMNS - {"stock"}}
        if fields:
            sets = ", ".join(f"{k} = :{k}" for k in fields)  # keys are whitelisted above
            try:
                self._db.execute(f"UPDATE products SET {sets} WHERE id = :id", {**fields, "id": product_id})
                self._db.commit()
            except sqlite3.IntegrityError as exc:
                self._db.rollback()
                raise Conflict(f"sku {fields.get('sku')!r} already exists") from exc
        return self.get(product_id)

    def delete(self, product_id: int) -> None:
        cur = self._db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self._db.commit()
        if cur.rowcount == 0:
            raise NotFound(f"product {product_id} not found")

    def adjust_stock(self, product_id: int, delta: int) -> dict:
        """Add `delta` (may be negative) to stock. Never goes below 0 -> InsufficientStock."""
        if not MIN_SQLITE_INT <= delta <= MAX_SQLITE_INT:
            raise ValueError("delta is outside SQLite's integer range")
        # Compare before adding so SQLite cannot promote an overflowing integer to REAL.
        lower, upper = max(0, -delta), min(MAX_SQLITE_INT, MAX_SQLITE_INT - delta)
        if lower > upper:
            product = self.get(product_id)
            raise InsufficientStock(f"only {product['stock']} in stock, cannot remove {-delta}")
        cur = self._db.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ? AND stock BETWEEN ? AND ?",
            (delta, product_id, lower, upper),
        )
        self._db.commit()
        if cur.rowcount == 0:
            product = self.get(product_id)  # raises NotFound if the id is wrong
            if delta > 0:
                raise Conflict("stock would exceed SQLite's maximum integer")
            raise InsufficientStock(f"only {product['stock']} in stock, cannot remove {-delta}")
        return self.get(product_id)
