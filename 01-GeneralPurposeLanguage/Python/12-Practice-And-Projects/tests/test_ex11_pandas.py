import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal


@pytest.fixture(scope="module")
def ex(load):
    return load("ex11_pandas")


# 1 adult_contacts
def test_adult_contacts_filters_and_picks_columns(ex):
    df = pd.DataFrame({"name": ["a", "b", "c"], "age": [12, 30, 18], "city": ["X", "Y", "Z"]})
    out = ex.adult_contacts(df)
    assert_frame_equal(out, pd.DataFrame({"name": ["b", "c"], "city": ["Y", "Z"]}, index=[1, 2]))


def test_adult_contacts_nobody(ex):
    df = pd.DataFrame({"name": ["a"], "age": [5], "city": ["X"]})
    assert ex.adult_contacts(df).empty
    assert list(ex.adult_contacts(df).columns) == ["name", "city"]


def test_adult_contacts_keeps_input(ex):
    df = pd.DataFrame({"name": ["a"], "age": [20], "city": ["X"]})
    ex.adult_contacts(df)
    assert list(df.columns) == ["name", "age", "city"]


# 2 fill_missing
def test_fill_missing_values(ex):
    df = pd.DataFrame({"price": [1.0, np.nan, 3.0], "category": ["a", None, "b"], "qty": [1, 2, 3]})
    out = ex.fill_missing(df)
    assert out["price"].tolist() == [1.0, 2.0, 3.0]
    assert out["category"].tolist() == ["a", "unknown", "b"]
    assert out["qty"].tolist() == [1, 2, 3]


def test_fill_missing_leaves_input_untouched(ex):
    df = pd.DataFrame({"price": [1.0, np.nan], "category": [None, "x"]})
    ex.fill_missing(df)
    assert df["price"].isna().sum() == 1 and df["category"].isna().sum() == 1


def test_fill_missing_no_missing_is_unchanged(ex):
    df = pd.DataFrame({"price": [1.0, 5.0], "category": ["a", "b"]})
    assert_frame_equal(ex.fill_missing(df), df)


# 3 clean_names
def test_clean_names_example(ex):
    s = pd.Series(["  aNNa   maria ", "BOB"])
    assert_series_equal(ex.clean_names(s), pd.Series(["Anna Maria", "Bob"]))


def test_clean_names_tabs_and_missing(ex):
    s = pd.Series(["x\t\ty", None])
    out = ex.clean_names(s)
    assert out[0] == "X Y"
    assert pd.isna(out[1])


def test_clean_names_keeps_index(ex):
    s = pd.Series([" a "], index=["k"])
    assert ex.clean_names(s).index.tolist() == ["k"]


# 5 add_store_share
def test_add_store_share_values(ex):
    df = pd.DataFrame({"store": ["X", "X", "Y"], "amount": [1.0, 3.0, 5.0]})
    out = ex.add_store_share(df)
    assert out["share"].tolist() == [0.25, 0.75, 1.0]


def test_add_store_share_shares_sum_to_one_per_store(ex):
    df = pd.DataFrame({"store": list("ababab"), "amount": [1, 2, 3, 4, 5, 6]})
    out = ex.add_store_share(df)
    sums = out.groupby("store")["share"].sum()
    assert np.allclose(sums, 1.0)


def test_add_store_share_original_not_modified_and_order_kept(ex):
    df = pd.DataFrame({"store": ["Y", "X"], "amount": [2, 2]})
    out = ex.add_store_share(df)
    assert "share" not in df.columns
    assert out["store"].tolist() == ["Y", "X"]


# 6 team_summary
def test_team_summary_values(ex):
    df = pd.DataFrame({"team": ["A", "A", "B"], "score": [10, 20, 7]})
    expected = pd.DataFrame({"n": [2, 1], "avg": [15.0, 7.0], "best": [20, 7]},
                            index=pd.Index(["A", "B"], name="team"))
    assert_frame_equal(ex.team_summary(df), expected)


def test_team_summary_columns_order(ex):
    df = pd.DataFrame({"team": ["A"], "score": [1]})
    assert list(ex.team_summary(df).columns) == ["n", "avg", "best"]


def test_team_summary_one_team_many_rows(ex):
    df = pd.DataFrame({"team": ["Z"] * 4, "score": [1, 2, 3, 4]})
    row = ex.team_summary(df).loc["Z"]
    assert (row["n"], row["avg"], row["best"]) == (4, 2.5, 4)


# 7 orders_with_names
def test_orders_with_names_basic(ex):
    orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": [10, 99, 10], "amount": [5, 6, 7]})
    customers = pd.DataFrame({"customer_id": [10, 11], "name": ["Ann", "Bob"]})
    out = ex.orders_with_names(orders, customers)
    assert list(out.columns) == ["order_id", "customer_id", "amount", "name"]
    assert out["name"].tolist() == ["Ann", "Unknown", "Ann"]
    assert out["order_id"].tolist() == [1, 2, 3]


def test_orders_with_names_keeps_row_count(ex):
    orders = pd.DataFrame({"order_id": [1], "customer_id": [5], "amount": [1]})
    customers = pd.DataFrame({"customer_id": [5, 6], "name": ["A", "B"]})
    assert len(ex.orders_with_names(orders, customers)) == 1


def test_orders_with_names_no_customers(ex):
    orders = pd.DataFrame({"order_id": [1, 2], "customer_id": [1, 2], "amount": [1, 2]})
    customers = pd.DataFrame({"customer_id": pd.Series([], dtype="int64"), "name": pd.Series([], dtype="object")})
    assert ex.orders_with_names(orders, customers)["name"].tolist() == ["Unknown", "Unknown"]


# 8 sales_table
def test_sales_table_values(ex):
    df = pd.DataFrame({"region": ["N", "N", "S"], "month": ["Jan", "Jan", "Feb"], "sales": [5, 2, 4]})
    out = ex.sales_table(df)
    assert out.loc["N", "Jan"] == 7
    assert out.loc["N", "Feb"] == 0
    assert out.loc["S", "Jan"] == 0
    assert out.loc["S", "Feb"] == 4


def test_sales_table_shape_and_no_nan(ex):
    df = pd.DataFrame({"region": list("NSNS"), "month": ["a", "a", "b", "c"], "sales": [1, 2, 3, 4]})
    out = ex.sales_table(df)
    assert out.shape == (2, 3)
    assert not out.isna().any().any()


def test_sales_table_single_cell(ex):
    df = pd.DataFrame({"region": ["N"], "month": ["Jan"], "sales": [3]})
    assert ex.sales_table(df).to_numpy().tolist() == [[3]]


# 9 scores_long
def test_scores_long_values(ex):
    df = pd.DataFrame({"student": ["bo", "ann"], "math": [70, 90], "art": [60, 80]})
    expected = pd.DataFrame({"student": ["ann", "ann", "bo", "bo"],
                             "subject": ["art", "math", "art", "math"],
                             "score": [80, 90, 60, 70]})
    assert_frame_equal(ex.scores_long(df), expected)


def test_scores_long_row_count(ex):
    df = pd.DataFrame({"student": list("abc"), "x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})
    assert len(ex.scores_long(df)) == 9


def test_scores_long_index_is_fresh(ex):
    df = pd.DataFrame({"student": ["b", "a"], "x": [1, 2]})
    assert ex.scores_long(df).index.tolist() == [0, 1]


# 10 monthly_totals
def test_monthly_totals_fills_gaps(ex):
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-03", "2024-01-20", "2024-03-02"]), "amount": [5, 5, 1]})
    out = ex.monthly_totals(df)
    assert out.tolist() == [10, 0, 1]
    assert list(out.index) == list(pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]))


def test_monthly_totals_unsorted_input(ex):
    df = pd.DataFrame({"date": pd.to_datetime(["2024-02-10", "2024-01-10"]), "amount": [2, 1]})
    assert ex.monthly_totals(df).tolist() == [1, 2]


def test_monthly_totals_single_row(ex):
    df = pd.DataFrame({"date": pd.to_datetime(["2024-05-31"]), "amount": [9]})
    out = ex.monthly_totals(df)
    assert out.index[0] == pd.Timestamp("2024-05-01") and out.iloc[0] == 9


# 11 top_n_per_group
@pytest.fixture
def scores():
    return pd.DataFrame({"group": ["b", "a", "a", "b", "a"], "who": list("vwxyz"), "score": [5, 1, 9, 7, 9]})


def test_top_n_per_group_top_one(ex, scores):
    out = ex.top_n_per_group(scores, 1)
    assert out["who"].tolist() == ["x", "y"]


def test_top_n_per_group_order_and_ties(ex, scores):
    out = ex.top_n_per_group(scores, 2)
    assert out["group"].tolist() == ["a", "a", "b", "b"]
    assert out["who"].tolist() == ["x", "z", "y", "v"]
    assert out.index.tolist() == [0, 1, 2, 3]


def test_top_n_per_group_n_larger_than_group(ex, scores):
    assert len(ex.top_n_per_group(scores, 10)) == 5


# 12 add_rank_in_group
def test_add_rank_in_group_ties_share_rank(ex):
    df = pd.DataFrame({"group": ["a"] * 3, "score": [90, 90, 70]})
    assert ex.add_rank_in_group(df)["rank"].tolist() == [1, 1, 3]


def test_add_rank_in_group_per_group_and_dtype(ex):
    df = pd.DataFrame({"group": ["a", "b", "a", "b"], "score": [1, 10, 2, 5]})
    out = ex.add_rank_in_group(df)
    assert out["rank"].tolist() == [2, 1, 1, 2]
    assert out["rank"].dtype.kind == "i"


def test_add_rank_in_group_keeps_row_order(ex):
    df = pd.DataFrame({"group": ["a", "a"], "score": [1, 2]})
    out = ex.add_rank_in_group(df)
    assert out["score"].tolist() == [1, 2]
    assert "rank" not in df.columns


# 13 clean_sales
@pytest.fixture
def messy():
    return pd.DataFrame({
        " Date": ["2024-02-01", "2024-01-05", "2024-01-05", "oops", None, "2024-03-09"],
        "Region ": [" south", " north ", " north ", "x", "y", "EAST"],
        "AMOUNT": [4.0, 10.0, 10.0, 3.0, 2.0, np.nan],
    })


def test_clean_sales_result(ex, messy):
    out = ex.clean_sales(messy)
    expected = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-05", "2024-02-01"]),
        "region": ["North", "South"],
        "amount": [10.0, 4.0],
        "month": [1, 2],
    })
    assert_frame_equal(out, expected, check_dtype=False)


def test_clean_sales_columns_and_index(ex, messy):
    out = ex.clean_sales(messy)
    assert list(out.columns) == ["date", "region", "amount", "month"]
    assert out.index.tolist() == [0, 1]


def test_clean_sales_does_not_touch_input(ex, messy):
    ex.clean_sales(messy)
    assert list(messy.columns) == [" Date", "Region ", "AMOUNT"]
    assert len(messy) == 6
