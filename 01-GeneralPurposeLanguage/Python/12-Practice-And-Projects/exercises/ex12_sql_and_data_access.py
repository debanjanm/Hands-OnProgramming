"""ex12_sql_and_data_access - SQL with sqlite3 (in-memory) and a small repository class.

Every function gets an open sqlite3 connection `conn`. Write the SQL yourself and
ALWAYS pass user values as parameters (?), never with f-strings.

Tables used (the tests create them):
    customers(id INTEGER PRIMARY KEY, name TEXT, city TEXT)
    orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL,
           status TEXT, placed_on TEXT)             -- placed_on like '2024-03-15'
    employees(id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER)
    prices(sku TEXT PRIMARY KEY, price REAL)
    accounts(id INTEGER PRIMARY KEY, balance REAL)
Functions return plain lists of tuples (or lists of names) in the order described.
"""


def customers_in_city(conn, city):
    """Return the names of customers living in `city`, sorted A-Z.

    Example: customers_in_city(conn, "Pune") -> ["Asha", "Ravi"]
    Level: easy
    Hint: WHERE city = ? and pass (city,) as the parameters.
    """
    raise NotImplementedError


def orders_with_customer(conn):
    """Return (order_id, customer_name, amount) for every order, ordered by order_id.
    Orders whose customer does not exist are left out.

    Example: -> [(1, "Asha", 50.0), (2, "Ravi", 20.0)]
    Level: easy
    Hint: INNER JOIN customers ON customers.id = orders.customer_id
    """
    raise NotImplementedError


def customers_without_orders(conn):
    """Return the names of customers who have no orders, sorted A-Z.

    Example: -> ["Meera"]
    Level: easy
    Hint: LEFT JOIN orders and keep rows where orders.id IS NULL (or use NOT EXISTS).
    """
    raise NotImplementedError


def total_per_customer(conn):
    """Return (name, total_amount) for EVERY customer (0 if no orders), biggest total first,
    ties by name A-Z. Use all statuses.

    Example: -> [("Asha", 80.0), ("Ravi", 20.0), ("Meera", 0)]
    Level: medium
    Hint: LEFT JOIN + GROUP BY + COALESCE(SUM(...), 0).
    """
    raise NotImplementedError


def big_spenders(conn, min_total, min_orders=2):
    """Return (name, order_count, total) for customers with at least `min_orders` orders
    AND a total of at least `min_total`, ordered by total descending then name.

    Example: big_spenders(conn, 100) -> [("Asha", 3, 180.0)]
    Level: medium
    Hint: HAVING filters groups after GROUP BY (WHERE filters rows before).
    """
    raise NotImplementedError


def monthly_revenue(conn):
    """Return (month, revenue) like ('2024-01', 150.0) for orders with status 'paid',
    one row per month that has paid orders, oldest month first. Use a CTE.

    Example: -> [("2024-01", 150.0), ("2024-02", 40.0)]
    Level: medium
    Hint: WITH paid AS (SELECT ...) SELECT strftime('%Y-%m', placed_on) ... GROUP BY 1
    """
    raise NotImplementedError


def running_total_per_customer(conn):
    """Return (customer_id, order_id, amount, running_total) for every order, where
    running_total is the sum of that customer's amounts up to and including this order,
    ordering the orders by placed_on then id. Final rows sorted by customer_id, placed_on, id.

    Example: customer 1 amounts 10, 5 -> (1, 1, 10.0, 10.0), (1, 2, 5.0, 15.0)
    Level: hard
    Hint: SUM(amount) OVER (PARTITION BY customer_id ORDER BY placed_on, id)
    """
    raise NotImplementedError


def salary_rank_in_dept(conn):
    """Return (name, dept, salary, rank) where rank is 1 for the highest salary in the
    department. Equal salaries share a rank and the next rank is NOT skipped (1,1,2).
    Sort by dept, rank, name.

    Example: salaries 90, 90, 70 in one dept -> ranks 1, 1, 2
    Level: hard
    Hint: DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC)
    """
    raise NotImplementedError


def top_earner_per_dept(conn):
    """Return (dept, name, salary) of exactly ONE top-paid employee per department
    (if tied, the name that sorts first). Sorted by dept. Use a CTE.

    Example: -> [("Eng", "Zoya", 120), ("Ops", "Ian", 70)]
    Level: hard
    Hint: ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name) in a CTE, keep 1.
    """
    raise NotImplementedError


def upsert_price(conn, sku, price):
    """Insert the (sku, price) row into `prices`, or update the price if the sku already
    exists. Save the change (commit).

    Example: upsert_price(conn, "A1", 9.5) twice with 9.5 then 12 -> one row, price 12
    Level: medium
    Hint: INSERT ... ON CONFLICT(sku) DO UPDATE SET price = excluded.price
    """
    raise NotImplementedError


def transfer(conn, src, dst, amount):
    """Move `amount` from account `src` to account `dst` as ONE transaction.
    Raise ValueError (and change nothing) if the amount is not positive, an account
    does not exist, or src has too little balance.

    Example: balances 100, 0 -> transfer(conn, 1, 2, 30) -> 70, 30
    Level: hard
    Hint: `with conn:` commits or rolls back; raising inside it undoes the first UPDATE.
    """
    raise NotImplementedError


class CustomerRepo:
    """Small repository around the `customers` table. Rows are returned as dicts
    {"id": ..., "name": ..., "city": ...}.

    Methods: add(name, city) -> new id; get(id) -> dict or None;
    find_by_city(city) -> list of dicts ordered by name; update_city(id, city) -> True if a
    row changed; delete(id) -> True if a row was removed; count() -> int.

    Example: repo.add("Asha", "Pune") -> 1; repo.get(1) -> {"id": 1, "name": "Asha", "city": "Pune"}
    Level: hard
    Hint: keep the connection in self.conn; cursor.lastrowid and cursor.rowcount help.
    """

    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _row(r):
        return {"id": r[0], "name": r[1], "city": r[2]}

    def add(self, name, city):
        """Insert a customer and return its new id.

        Level: easy
        Hint: cursor.lastrowid
        """
        raise NotImplementedError

    def get(self, customer_id):
        """Return the customer as a dict, or None if it does not exist.

        Level: easy
        Hint: fetchone() returns None when nothing matches.
        """
        raise NotImplementedError

    def find_by_city(self, city):
        """Return all customers of the city as dicts, ordered by name.

        Level: medium
        Hint: build the dicts from the rows.
        """
        raise NotImplementedError

    def update_city(self, customer_id, city):
        """Change the city. Return True if a customer was updated, False if the id is unknown.

        Level: medium
        Hint: cursor.rowcount tells how many rows changed.
        """
        raise NotImplementedError

    def delete(self, customer_id):
        """Delete the customer. Return True if a row was removed, False otherwise.

        Level: medium
        Hint: DELETE FROM ... WHERE id = ? then check rowcount.
        """
        raise NotImplementedError

    def count(self):
        """Return how many customers exist.

        Level: easy
        Hint: SELECT COUNT(*) ... fetchone()[0]
        """
        raise NotImplementedError
