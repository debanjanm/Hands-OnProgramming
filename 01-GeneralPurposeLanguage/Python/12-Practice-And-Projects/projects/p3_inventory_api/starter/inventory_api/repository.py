"""sqlite3 storage. No FastAPI in here, so it can be tested on its own."""
import sqlite3


class NotFound(Exception):
    """No product with that id."""


class Conflict(Exception):
    """The change clashes with existing data (e.g. duplicate sku)."""


class InsufficientStock(Conflict):
    """A stock adjustment would make stock negative."""


class ProductRepository:
    """CRUD + search + stock adjustments for products."""

    def __init__(self, db_path: str = ":memory:") -> None:
        """Open the database and create the `products` table if missing.

        Columns: id (autoincrement pk), name, sku (UNIQUE), price (>= 0), stock (>= 0), category (nullable).
        Hint: sqlite3.connect(db_path, check_same_thread=False) and row_factory = sqlite3.Row.
        """
        # TODO (milestone 2)
        raise NotImplementedError

    def close(self) -> None:
        """Close the connection."""
        raise NotImplementedError

    def create(self, **fields) -> dict:
        """Insert a product and return it as a dict (with id). Duplicate sku -> raise Conflict."""
        # TODO (milestone 2): catch sqlite3.IntegrityError and raise Conflict
        raise NotImplementedError

    def get(self, product_id: int) -> dict:
        """Return one product as a dict, or raise NotFound."""
        raise NotImplementedError

    def list(self, q: str | None = None, category: str | None = None,
             min_price: float | None = None, max_price: float | None = None,
             limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
        """Return (items on this page, total number of matches), ordered by id.

        `q` matches name OR sku (case-insensitive substring). Filters combine with AND.
        """
        # TODO (milestone 5): build the WHERE clause with ? placeholders - never f-string user values!
        raise NotImplementedError

    def update(self, product_id: int, **fields) -> dict:
        """Change some columns (never stock) and return the product. NotFound / Conflict as above."""
        # TODO (milestone 3)
        raise NotImplementedError

    def delete(self, product_id: int) -> None:
        """Delete a product or raise NotFound."""
        raise NotImplementedError

    def adjust_stock(self, product_id: int, delta: int) -> dict:
        """Add delta (may be negative) to stock and return the product.

        Unknown id -> NotFound. Result would be < 0 -> InsufficientStock (and stock is unchanged).
        Hint: one UPDATE ... WHERE id = ? AND stock + ? >= 0 and check rowcount.
        """
        # TODO (milestone 4)
        raise NotImplementedError
