import sqlite3

import pytest

SCHEMA = """
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, status TEXT, placed_on TEXT);
CREATE TABLE employees(id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
CREATE TABLE prices(sku TEXT PRIMARY KEY, price REAL);
CREATE TABLE accounts(id INTEGER PRIMARY KEY, balance REAL);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Ravi','Pune'),(3,'Meera','Delhi'),(4,'Kiran','Delhi');
INSERT INTO orders VALUES
 (1,1,50,'paid','2024-01-10'),(2,2,20,'paid','2024-01-15'),(3,1,30,'pending','2024-02-05'),
 (4,1,100,'paid','2024-01-20'),(5,4,40,'paid','2024-02-11'),(6,99,5,'paid','2024-02-12');
INSERT INTO employees VALUES
 (1,'Zoya','Eng',120),(2,'Yan','Eng',100),(3,'Xu','Eng',100),
 (4,'Ian','Ops',70),(5,'Olu','Ops',60),(6,'Ann','Hr',50),(7,'Abe','Hr',50);
INSERT INTO accounts VALUES (1,100),(2,0);
"""


@pytest.fixture(scope="module")
def ex(load):
    return load("ex12_sql_and_data_access")


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    yield c
    c.close()


@pytest.fixture
def empty_customers(conn):
    conn.execute("DELETE FROM customers")
    conn.commit()
    return conn


# 1 customers_in_city
def test_customers_in_city_sorted(ex, conn):
    assert ex.customers_in_city(conn, "Pune") == ["Asha", "Ravi"]


def test_customers_in_city_unknown_city(ex, conn):
    assert ex.customers_in_city(conn, "Oslo") == []


def test_customers_in_city_is_injection_safe(ex, conn):
    assert ex.customers_in_city(conn, "x' OR '1'='1") == []


# 2 orders_with_customer
def test_orders_with_customer_rows(ex, conn):
    assert ex.orders_with_customer(conn) == [
        (1, "Asha", 50.0), (2, "Ravi", 20.0), (3, "Asha", 30.0), (4, "Asha", 100.0), (5, "Kiran", 40.0)]


def test_orders_with_customer_skips_orphans(ex, conn):
    assert 6 not in [r[0] for r in ex.orders_with_customer(conn)]


def test_orders_with_customer_no_orders(ex, conn):
    conn.execute("DELETE FROM orders")
    assert ex.orders_with_customer(conn) == []


# 3 customers_without_orders
def test_customers_without_orders(ex, conn):
    assert ex.customers_without_orders(conn) == ["Meera"]


def test_customers_without_orders_after_new_customer(ex, conn):
    conn.execute("INSERT INTO customers VALUES (5,'Bela','Goa')")
    assert ex.customers_without_orders(conn) == ["Bela", "Meera"]


def test_customers_without_orders_none_left(ex, conn):
    conn.execute("INSERT INTO orders VALUES (7,3,1,'paid','2024-03-01')")
    assert ex.customers_without_orders(conn) == []


# 4 total_per_customer
def test_total_per_customer_order_and_zero(ex, conn):
    assert ex.total_per_customer(conn) == [("Asha", 180.0), ("Kiran", 40.0), ("Ravi", 20.0), ("Meera", 0)]


def test_total_per_customer_tie_by_name(ex, conn):
    conn.execute("INSERT INTO orders VALUES (7,3,40,'paid','2024-03-01')")
    names = [r[0] for r in ex.total_per_customer(conn)]
    assert names[:3] == ["Asha", "Kiran", "Meera"]


def test_total_per_customer_row_per_customer(ex, conn):
    assert len(ex.total_per_customer(conn)) == 4


# 5 big_spenders
def test_big_spenders_threshold(ex, conn):
    assert ex.big_spenders(conn, 100) == [("Asha", 3, 180.0)]


def test_big_spenders_min_orders_one(ex, conn):
    assert ex.big_spenders(conn, 30, min_orders=1) == [("Asha", 3, 180.0), ("Kiran", 1, 40.0)]


def test_big_spenders_default_needs_two_orders(ex, conn):
    assert [r[0] for r in ex.big_spenders(conn, 0)] == ["Asha"]


def test_big_spenders_nobody(ex, conn):
    assert ex.big_spenders(conn, 10_000) == []


# 6 monthly_revenue
def test_monthly_revenue_paid_only(ex, conn):
    assert ex.monthly_revenue(conn) == [("2024-01", 170.0), ("2024-02", 45.0)]


def test_monthly_revenue_ignores_unpaid_months(ex, conn):
    conn.execute("INSERT INTO orders VALUES (7,1,999,'pending','2024-05-01')")
    assert [m for m, _ in ex.monthly_revenue(conn)] == ["2024-01", "2024-02"]


def test_monthly_revenue_empty(ex, conn):
    conn.execute("DELETE FROM orders")
    assert ex.monthly_revenue(conn) == []


# 7 running_total_per_customer
def test_running_total_values(ex, conn):
    assert ex.running_total_per_customer(conn) == [
        (1, 1, 50.0, 50.0), (1, 4, 100.0, 150.0), (1, 3, 30.0, 180.0),
        (2, 2, 20.0, 20.0), (4, 5, 40.0, 40.0), (99, 6, 5.0, 5.0)]


def test_running_total_last_equals_customer_total(ex, conn):
    rows = ex.running_total_per_customer(conn)
    assert [r[3] for r in rows if r[0] == 1][-1] == 180.0


def test_running_total_same_day_uses_id_order(ex, conn):
    conn.execute("INSERT INTO orders VALUES (8,2,10,'paid','2024-01-15')")
    rows = [r for r in ex.running_total_per_customer(conn) if r[0] == 2]
    assert rows == [(2, 2, 20.0, 20.0), (2, 8, 10.0, 30.0)]


# 8 salary_rank_in_dept
def test_salary_rank_values(ex, conn):
    assert ex.salary_rank_in_dept(conn) == [
        ("Zoya", "Eng", 120, 1), ("Xu", "Eng", 100, 2), ("Yan", "Eng", 100, 2),
        ("Abe", "Hr", 50, 1), ("Ann", "Hr", 50, 1),
        ("Ian", "Ops", 70, 1), ("Olu", "Ops", 60, 2)]


def test_salary_rank_does_not_skip(ex, conn):
    conn.execute("INSERT INTO employees VALUES (8,'Low','Eng',10)")
    assert [r for r in ex.salary_rank_in_dept(conn) if r[0] == "Low"][0][3] == 3


def test_salary_rank_single_employee(ex, conn):
    conn.execute("INSERT INTO employees VALUES (9,'Solo','Legal',1)")
    assert [r for r in ex.salary_rank_in_dept(conn) if r[1] == "Legal"] == [("Solo", "Legal", 1, 1)]


# 9 top_earner_per_dept
def test_top_earner_per_dept(ex, conn):
    assert ex.top_earner_per_dept(conn) == [("Eng", "Zoya", 120), ("Hr", "Abe", 50), ("Ops", "Ian", 70)]


def test_top_earner_one_row_per_dept_even_with_ties(ex, conn):
    depts = [r[0] for r in ex.top_earner_per_dept(conn)]
    assert depts == sorted(set(depts))


def test_top_earner_changes_with_data(ex, conn):
    conn.execute("UPDATE employees SET salary = 500 WHERE name = 'Olu'")
    assert ("Ops", "Olu", 500) in ex.top_earner_per_dept(conn)


# 10 upsert_price
def test_upsert_price_inserts(ex, conn):
    ex.upsert_price(conn, "A1", 9.5)
    assert conn.execute("SELECT * FROM prices").fetchall() == [("A1", 9.5)]


def test_upsert_price_updates_without_duplicate(ex, conn):
    ex.upsert_price(conn, "A1", 9.5)
    ex.upsert_price(conn, "A1", 12)
    assert conn.execute("SELECT sku, price FROM prices").fetchall() == [("A1", 12.0)]


def test_upsert_price_keeps_other_skus_and_commits(ex, tmp_path):
    path = tmp_path / "p.db"
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    ex.upsert_price(c, "A1", 1)
    ex.upsert_price(c, "B2", 2)
    c.close()
    c2 = sqlite3.connect(path)
    assert c2.execute("SELECT sku, price FROM prices ORDER BY sku").fetchall() == [("A1", 1.0), ("B2", 2.0)]
    c2.close()


# 11 transfer
def balances(conn):
    return conn.execute("SELECT balance FROM accounts ORDER BY id").fetchall()


def test_transfer_moves_money(ex, conn):
    ex.transfer(conn, 1, 2, 30)
    assert balances(conn) == [(70.0,), (30.0,)]


def test_transfer_insufficient_funds_changes_nothing(ex, conn):
    with pytest.raises(ValueError):
        ex.transfer(conn, 1, 2, 500)
    assert balances(conn) == [(100.0,), (0.0,)]


def test_transfer_unknown_destination_rolls_back(ex, conn):
    with pytest.raises(ValueError):
        ex.transfer(conn, 1, 99, 10)
    assert balances(conn) == [(100.0,), (0.0,)]


def test_transfer_rejects_non_positive_amount(ex, conn):
    for bad in (0, -5):
        with pytest.raises(ValueError):
            ex.transfer(conn, 1, 2, bad)
    assert balances(conn) == [(100.0,), (0.0,)]


def test_transfer_whole_balance_allowed(ex, conn):
    ex.transfer(conn, 1, 2, 100)
    assert balances(conn) == [(0.0,), (100.0,)]


# 12 CustomerRepo
@pytest.fixture
def repo(ex, empty_customers):
    return ex.CustomerRepo(empty_customers)


def test_repo_add_and_get(repo):
    new_id = repo.add("Asha", "Pune")
    assert repo.get(new_id) == {"id": new_id, "name": "Asha", "city": "Pune"}


def test_repo_get_missing_is_none(repo):
    assert repo.get(12345) is None


def test_repo_ids_are_different(repo):
    assert repo.add("A", "X") != repo.add("B", "X")


def test_repo_find_by_city_sorted(repo):
    repo.add("Ravi", "Pune")
    repo.add("Asha", "Pune")
    repo.add("Meera", "Delhi")
    assert [c["name"] for c in repo.find_by_city("Pune")] == ["Asha", "Ravi"]
    assert repo.find_by_city("Nowhere") == []


def test_repo_update_city(repo):
    i = repo.add("Asha", "Pune")
    assert repo.update_city(i, "Goa") is True
    assert repo.get(i)["city"] == "Goa"
    assert repo.update_city(9999, "Goa") is False


def test_repo_delete_and_count(repo):
    i = repo.add("Asha", "Pune")
    repo.add("Ravi", "Pune")
    assert repo.count() == 2
    assert repo.delete(i) is True
    assert repo.delete(i) is False
    assert repo.count() == 1
    assert repo.get(i) is None


def test_repo_values_are_parameterised(repo):
    nasty = "Bob'); DROP TABLE customers;--"
    i = repo.add(nasty, "X")
    assert repo.get(i)["name"] == nasty
    assert repo.count() == 1
