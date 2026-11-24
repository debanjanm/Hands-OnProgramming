import importlib

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal


def mod(name):
    return importlib.import_module(f"salesreport.{name}")


def ts(*dates):
    return pd.to_datetime(list(dates))


# ---------------------------------------------------------------- generate
def test_dataset_is_deterministic():
    g = mod("generate").make_dataset
    a, b = g(seed=7), g(seed=7)
    for name in a:
        assert_frame_equal(a[name], b[name])


def test_dataset_changes_with_seed():
    g = mod("generate").make_dataset
    assert not g(seed=1)["orders"].equals(g(seed=2)["orders"])


def test_dataset_has_deliberate_dirt():
    d = mod("generate").make_dataset()
    o, c, p = d["orders"], d["customers"], d["products"]
    assert o["order_id"].duplicated().any()
    assert o["quantity"].isna().any() and o["unit_price"].isna().any()
    assert (o["quantity"] > 50).any()
    assert pd.to_datetime(o["order_date"], format="%Y-%m-%d", errors="coerce").isna().any()
    assert c["customer_id"].duplicated().any() and c["country"].isna().any()
    assert p["category"].isna().any() and p["product_id"].duplicated().any()


# ---------------------------------------------------------------- clean
@pytest.fixture
def products():
    return pd.DataFrame({"product_id": [1, 2, 2], "category": ["A", None, None], "price": [10.0, 5.0, 5.0]})


def test_clean_products(products):
    out = mod("clean").clean_products(products)
    assert_frame_equal(out, pd.DataFrame({"product_id": [1, 2], "category": pd.Series(["A", "Uncategorized"], dtype="object"), "price": [10.0, 5.0]}))


def test_clean_customers():
    raw = pd.DataFrame({
        "customer_id": [1, 1, 2, 3],
        "signup_date": ["2023-01-05", "2023-01-05", "yesterday", "2023-02-01"],
        "country": ["UK", "UK", None, "US"],
    })
    out = mod("clean").clean_customers(raw)
    assert out["customer_id"].tolist() == [1, 2, 3]
    assert out["country"].tolist() == ["UK", "Unknown", "US"]
    assert out["signup_date"].isna().tolist() == [False, True, False]
    assert out["signup_date"].iloc[0] == pd.Timestamp("2023-01-05")


def _orders(**cols):
    base = {"order_id": [1], "customer_id": [1], "product_id": [1], "order_date": ["2023-01-01"],
            "quantity": [2.0], "unit_price": [10.0], "status": ["completed"]}
    return pd.DataFrame(base | cols)


def test_clean_orders_happy_path(products):
    out = mod("clean").clean_orders(_orders(), products)
    assert len(out) == 1
    assert out["quantity"].dtype.kind == "i"
    assert out["order_date"].iloc[0] == pd.Timestamp("2023-01-01")


def test_clean_orders_drops_duplicate_ids(products):
    raw = pd.concat([_orders(), _orders()], ignore_index=True)
    assert len(mod("clean").clean_orders(raw, products)) == 1


@pytest.mark.parametrize("date", ["31/02/2023", "not a date", None])
def test_clean_orders_drops_bad_dates(products, date):
    assert mod("clean").clean_orders(_orders(order_date=[date]), products).empty


def test_clean_orders_fills_missing_price_from_products(products):
    out = mod("clean").clean_orders(_orders(unit_price=[None]), products)
    assert out["unit_price"].tolist() == [10.0]


def test_clean_orders_drops_missing_quantity(products):
    assert mod("clean").clean_orders(_orders(quantity=[None]), products).empty


@pytest.mark.parametrize("qty", [0.0, -3.0, 500.0])
def test_clean_orders_drops_outlier_quantity(products, qty):
    assert mod("clean").clean_orders(_orders(quantity=[qty]), products).empty


def test_clean_orders_keeps_only_completed(products):
    assert mod("clean").clean_orders(_orders(status=["cancelled"]), products).empty


def test_clean_pipeline_output_is_valid():
    g, c, v = mod("generate"), mod("clean"), mod("validate")
    d = g.make_dataset()
    cust, prod = c.clean_customers(d["customers"]), c.clean_products(d["products"])
    orders = c.clean_orders(d["orders"], prod)
    assert v.validate(orders, cust, prod) == []
    assert len(orders) < len(d["orders"])


# ---------------------------------------------------------------- validate
def good_tables():
    orders = pd.DataFrame({"order_id": [1, 2], "customer_id": [1, 1], "product_id": [1, 1],
                           "order_date": ts("2023-01-01", "2023-02-01"), "quantity": [1, 2], "unit_price": [5.0, 5.0]})
    customers = pd.DataFrame({"customer_id": [1], "signup_date": ts("2023-01-01"), "country": ["UK"]})
    products = pd.DataFrame({"product_id": [1], "category": ["A"], "price": [5.0]})
    return orders, customers, products


def test_validate_ok():
    assert mod("validate").validate(*good_tables()) == []


def test_validate_missing_column():
    o, c, p = good_tables()
    problems = mod("validate").validate(o.drop(columns="quantity"), c, p)
    assert problems == ["orders: missing columns ['quantity']"]


def test_validate_finds_nulls_dupes_orphans_and_bad_numbers():
    o, c, p = good_tables()
    o.loc[1, ["order_id", "customer_id", "quantity"]] = [1, 99, -1]
    o.loc[0, "unit_price"] = None
    text = " | ".join(mod("validate").validate(o, c, p))
    for expected in ["unit_price: 1 missing", "duplicate order_id", "quantity must be positive", "unknown customer_id"]:
        assert expected in text


def test_assert_valid_raises_with_all_problems():
    o, c, p = good_tables()
    o["quantity"] = -1
    with pytest.raises(ValueError, match="quantity must be positive"):
        mod("validate").assert_valid(o, c, p)
    mod("validate").assert_valid(*good_tables())  # no error


# ---------------------------------------------------------------- features
@pytest.fixture
def feats():
    orders = pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "customer_id": [1, 1, 2, 2],
        "product_id": [1, 2, 1, 1],
        "order_date": ts("2023-01-10", "2023-03-05", "2023-02-01", "2023-02-20"),
        "quantity": [1, 2, 3, 1],
        "unit_price": [10.0, 5.0, 10.0, 10.0],
    })
    customers = pd.DataFrame({"customer_id": [1, 2], "country": ["UK", "US"]})
    products = pd.DataFrame({"product_id": [1, 2], "category": ["A", "B"]})
    return mod("features").add_features(orders, customers, products)


def test_features_revenue(feats):
    assert_series_equal(feats["revenue"], pd.Series([10.0, 10.0, 30.0, 10.0]), check_names=False)


def test_features_month_and_joins(feats):
    assert feats["order_month"].tolist() == ["2023-01", "2023-03", "2023-02", "2023-02"]
    assert feats["country"].tolist() == ["UK", "UK", "US", "US"]
    assert feats["category"].tolist() == ["A", "B", "A", "A"]


def test_features_cohort(feats):
    assert feats["first_month"].tolist() == ["2023-01", "2023-01", "2023-02", "2023-02"]
    assert feats["cohort_index"].tolist() == [0, 2, 0, 0]


def test_features_does_not_modify_input():
    o = pd.DataFrame({"order_id": [1], "customer_id": [1], "product_id": [1],
                      "order_date": ts("2023-01-01"), "quantity": [1], "unit_price": [1.0]})
    before = o.copy()
    mod("features").add_features(o, pd.DataFrame({"customer_id": [1], "country": ["UK"]}),
                                 pd.DataFrame({"product_id": [1], "category": ["A"]}))
    assert_frame_equal(o, before)


# ---------------------------------------------------------------- kpis
def test_revenue_by_month(feats):
    out = mod("kpis").revenue_by_month(feats)
    assert_frame_equal(out, pd.DataFrame({"order_month": ["2023-01", "2023-02", "2023-03"], "revenue": [10.0, 40.0, 10.0]}))


def test_revenue_by_category(feats):
    out = mod("kpis").revenue_by_category(feats)
    assert_frame_equal(out, pd.DataFrame({"category": ["A", "B"], "revenue": [50.0, 10.0]}))


def test_top_customers(feats):
    out = mod("kpis").top_customers(feats, n=1)
    assert_frame_equal(out, pd.DataFrame({"customer_id": [2], "orders": [2], "revenue": [40.0]}))


def test_top_customers_tie_breaks_by_id(feats):
    out = mod("kpis").top_customers(feats.assign(revenue=1.0), n=2)
    assert out["customer_id"].tolist() == [1, 2]


def test_average_order_value(feats):
    assert mod("kpis").average_order_value(feats) == 15.0
    assert mod("kpis").average_order_value(feats.iloc[0:0]) == 0.0


def test_cohort_retention(feats):
    out = mod("kpis").cohort_retention(feats)
    expected = pd.DataFrame({0: [1.0, 1.0], 1: [0.0, 0.0], 2: [1.0, 0.0]},
                            index=pd.Index(["2023-01", "2023-02"], name="first_month"))
    assert_frame_equal(out, expected, check_column_type=False)


def test_cohort_retention_first_column_is_one():
    d = mod("generate").make_dataset()
    c, f = mod("clean"), mod("features")
    prod = c.clean_products(d["products"])
    df = f.add_features(c.clean_orders(d["orders"], prod), c.clean_customers(d["customers"]), prod)
    r = mod("kpis").cohort_retention(df)
    assert (r[0] == 1.0).all() and r.to_numpy().max() <= 1.0 and r.to_numpy().min() >= 0.0


# ---------------------------------------------------------------- charts + report
def test_charts_create_png_files(feats, tmp_path):
    out_dir = tmp_path / "charts" / "nested"  # does not exist yet
    files = mod("charts").make_all(feats, out_dir)
    assert sorted(p.name for p in files) == ["cohort_retention.png", "revenue_by_category.png", "revenue_by_month.png"]
    for p in files:
        assert p.exists() and p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_single_chart_function(feats, tmp_path):
    k = mod("kpis")
    path = mod("charts").plot_revenue_by_month(k.revenue_by_month(feats), tmp_path)
    assert path == tmp_path / "revenue_by_month.png" and path.stat().st_size > 0


def test_markdown_table():
    t = mod("report").to_markdown_table(pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}))
    assert t == "| a | b |\n| --- | --- |\n| 1 | x |\n| 2 | y |"


def test_build_report_contents(feats):
    text = mod("report").build_report(feats)
    assert text.startswith("# Sales report")
    assert "- Orders: 4" in text and "- Total revenue: 60.00" in text and "- Average order value: 15.00" in text
    assert "## Revenue by month" in text and "| 2023-02 | 40.0 |" in text
    assert "## Charts" not in text


def test_build_report_lists_charts(feats, tmp_path):
    files = mod("charts").make_all(feats, tmp_path)
    text = mod("report").build_report(feats, files)
    assert "![revenue_by_month](revenue_by_month.png)" in text


def test_write_report(feats, tmp_path):
    path = mod("report").write_report(feats, tmp_path / "out")
    assert path.name == "report.md" and path.read_text(encoding="utf-8").startswith("# Sales report")


def test_run_pipeline_end_to_end(tmp_path):
    result = mod("report").run_pipeline(tmp_path, seed=3)
    assert result["report"].exists()
    assert len(result["charts"]) == 3 and all(p.exists() for p in result["charts"])
    assert not result["features"].empty
    again = mod("report").run_pipeline(tmp_path / "again", seed=3)
    assert_frame_equal(result["features"], again["features"])
    assert result["report"].read_text(encoding="utf-8") == again["report"].read_text(encoding="utf-8")
