import csv
import json

import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex06_errors_and_files")


# 1 parse_ints
def test_parse_ints_mixed(ex):
    assert ex.parse_ints(["1", "x", " 3 ", None, "4.5"]) == ([1, 3], ["x", None, "4.5"])


def test_parse_ints_empty_and_all_good(ex):
    assert ex.parse_ints([]) == ([], [])
    assert ex.parse_ints(["7", 8, "-9"]) == ([7, 8, -9], [])


def test_parse_ints_all_bad(ex):
    assert ex.parse_ints(["", "a", [1]]) == ([], ["", "a", [1]])


# 2 custom exceptions
def test_insufficient_funds_attributes_and_message(ex):
    err = ex.InsufficientFundsError(30, 50)
    assert (err.balance, err.amount, err.shortfall) == (30, 50, 20)
    assert str(err) == "need 50, have 30"


def test_exception_hierarchy(ex):
    assert issubclass(ex.InsufficientFundsError, ex.BankError)
    assert issubclass(ex.BankError, Exception)
    assert isinstance(ex.InsufficientFundsError(1, 2), ex.BankError)


def test_withdraw(ex):
    assert ex.withdraw(100, 30) == 70
    assert ex.withdraw(30, 30) == 0
    with pytest.raises(ex.InsufficientFundsError) as info:
        ex.withdraw(30, 50)
    assert info.value.shortfall == 20
    with pytest.raises(ex.BankError):
        ex.withdraw(1, 2)
    for bad in (0, -5):
        with pytest.raises(ValueError):
            ex.withdraw(100, bad)


# 3 validate_user
GOOD = {"name": "Asha", "email": "a@b.com", "age": 30}


def test_validate_user_ok(ex):
    assert ex.validate_user(dict(GOOD)) == GOOD
    assert ex.validate_user({**GOOD, "age": 0})["age"] == 0


def test_validate_user_reports_all_errors(ex):
    with pytest.raises(ex.ValidationError) as info:
        ex.validate_user({"name": "  ", "age": 200})
    assert set(info.value.errors) == {"name", "email", "age"}
    assert "age" in str(info.value)


def test_validate_user_single_field_problems(ex):
    for patch, field in [({"name": ""}, "name"), ({"email": "nope"}, "email"),
                         ({"email": "a@b"}, "email"), ({"age": -1}, "age"),
                         ({"age": "30"}, "age"), ({"age": True}, "age"),
                         ({"age": 151}, "age")]:
        with pytest.raises(ex.ValidationError) as info:
            ex.validate_user({**GOOD, **patch})
        assert set(info.value.errors) == {field}


def test_validate_user_missing_keys(ex):
    with pytest.raises(ex.ValidationError) as info:
        ex.validate_user({})
    assert set(info.value.errors) == {"name", "email", "age"}


# 4 raise from
def test_get_setting_found(ex):
    assert ex.get_setting({"db": {"port": 5432}}, "db.port") == 5432
    assert ex.get_setting({"debug": False}, "debug") is False


def test_get_setting_missing_is_chained(ex):
    with pytest.raises(ex.ConfigError, match="db.host") as info:
        ex.get_setting({"db": {"port": 1}}, "db.host")
    assert isinstance(info.value.__cause__, KeyError)


def test_get_setting_wrong_shape(ex):
    with pytest.raises(ex.ConfigError) as info:
        ex.get_setting({"db": 5}, "db.port")
    assert info.value.__cause__ is not None


# 5 finally
def test_cleanup_after_success(ex):
    log = []
    assert ex.run_with_cleanup(lambda: 42, log) == 42
    assert log == ["start", "cleanup"]


def test_cleanup_after_error_and_error_escapes(ex):
    log = []

    def boom():
        raise ValueError("bad")

    with pytest.raises(ValueError):
        ex.run_with_cleanup(boom, log)
    assert log == ["start", "cleanup"]


def test_cleanup_runs_after_action(ex):
    log = []
    ex.run_with_cleanup(lambda: log.append("action"), log)
    assert log == ["start", "action", "cleanup"]


# 6 Transaction
class Boom(Exception):
    pass


def test_transaction_commit(ex):
    d = {"a": [1]}
    with ex.Transaction(d) as t:
        assert t is d
        t["a"].append(2)
        t["b"] = 1
    assert d == {"a": [1, 2], "b": 1}


def test_transaction_rollback_nested(ex):
    d = {"a": [1], "n": 0}
    with pytest.raises(Boom):
        with ex.Transaction(d) as t:
            t["a"].append(2)
            t["n"] = 5
            t["new"] = True
            raise Boom("fail")
    assert d == {"a": [1], "n": 0}


def test_transaction_can_be_reused(ex):
    d = {"x": 1}
    tx = ex.Transaction(d)
    with tx:
        d["x"] = 2
    with pytest.raises(KeyError):
        with tx:
            d["x"] = 3
            raise KeyError("k")
    assert d == {"x": 2}


# 7 temp_attr
class Box:
    pass


def test_temp_attr_replaces_and_restores(ex):
    b = Box()
    b.debug = False
    with ex.temp_attr(b, "debug", True):
        assert b.debug is True
    assert b.debug is False


def test_temp_attr_removes_new_attribute(ex):
    b = Box()
    with ex.temp_attr(b, "extra", 1):
        assert b.extra == 1
    assert not hasattr(b, "extra")


def test_temp_attr_restores_on_error(ex):
    b = Box()
    b.mode = "a"
    with pytest.raises(ValueError):
        with ex.temp_attr(b, "mode", "b"):
            raise ValueError
    assert b.mode == "a"


# 8 text files
def test_write_and_read_lines(ex, tmp_path):
    p = tmp_path / "t.txt"
    ex.write_lines(p, ["a", "b"])
    assert p.read_text() == "a\nb\n"
    assert ex.read_lines(p) == ["a", "b"]


def test_write_lines_replaces_and_handles_empty(ex, tmp_path):
    p = tmp_path / "t.txt"
    ex.write_lines(p, ["old", "old2"])
    ex.write_lines(p, [])
    assert p.read_text() == ""
    ex.write_lines(p, ["héllo"])
    assert ex.read_lines(p) == ["héllo"]


def test_read_lines_skips_blank_and_strips(ex, tmp_path):
    p = tmp_path / "t.txt"
    p.write_text("a\n\n  b  \n   \n")
    assert ex.read_lines(p) == ["a", "b"]


def test_read_lines_missing(ex, tmp_path):
    missing = tmp_path / "nope.txt"
    with pytest.raises(FileNotFoundError):
        ex.read_lines(missing)
    assert ex.read_lines(missing, missing_ok=True) == []


def test_count_words(ex, tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("Hi, hi! Bye.\nbye; ...  HI")
    assert ex.count_words(p) == {"hi": 3, "bye": 2}


def test_count_words_empty_file(ex, tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("")
    assert ex.count_words(p) == {}
    p.write_text("... !!")
    assert ex.count_words(p) == {}


# 9 csv
def test_write_rows_has_header_and_rows(ex, tmp_path):
    p = tmp_path / "r.csv"
    ex.write_rows(p, [{"name": "Ann", "amount": 5}], ["name", "amount"])
    with open(p, newline="") as f:
        assert list(csv.reader(f)) == [["name", "amount"], ["Ann", "5"]]


def test_write_rows_quotes_special_values(ex, tmp_path):
    p = tmp_path / "r.csv"
    rows = [{"name": 'Lee, "Jr"', "amount": 1}]
    ex.write_rows(p, rows, ["name", "amount"])
    with open(p, newline="") as f:
        assert next(csv.DictReader(f))["name"] == 'Lee, "Jr"'


def test_write_rows_empty_gives_header_only(ex, tmp_path):
    p = tmp_path / "r.csv"
    ex.write_rows(p, [], ["a", "b"])
    assert p.read_text().strip() == "a,b"


def test_total_by_category(ex, tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("category,amount\nfood,10.5\nfood,4.5\nbus,x\nbus,2\n bus ,1\n")
    totals = ex.total_by_category(p)
    assert totals == {"food": pytest.approx(15.0), "bus": pytest.approx(3.0)}


def test_total_by_category_empty_amounts_and_no_rows(ex, tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("category,amount\nfood,\n")
    assert ex.total_by_category(p) == {}
    p.write_text("category,amount\n")
    assert ex.total_by_category(p) == {}


# 10 json
def test_save_json_format(ex, tmp_path):
    p = tmp_path / "d.json"
    ex.save_json(p, {"b": 1, "a": [1, 2]})
    text = p.read_text()
    assert text.index('"a"') < text.index('"b"')
    assert text.endswith("\n")
    assert '  "a"' in text
    assert json.loads(text) == {"a": [1, 2], "b": 1}


def test_save_and_load_roundtrip(ex, tmp_path):
    p = tmp_path / "d.json"
    data = {"name": "Zoë", "n": [1, {"x": None}]}
    ex.save_json(p, data)
    assert ex.load_json(p) == data


def test_load_json_defaults(ex, tmp_path):
    assert ex.load_json(tmp_path / "missing.json") is None
    assert ex.load_json(tmp_path / "missing.json", {}) == {}
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert ex.load_json(bad, []) == []


# 11 pathlib
def test_list_by_extension(ex, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_text("")
    (tmp_path / "sub" / "b.TXT").write_text("")
    (tmp_path / "sub" / "c.py").write_text("")
    (tmp_path / "README").write_text("")
    assert ex.list_by_extension(tmp_path) == {
        ".txt": ["a.txt", "sub/b.TXT"], ".py": ["sub/c.py"], "": ["README"]}


def test_list_by_extension_ignores_dirs_and_empty(ex, tmp_path):
    assert ex.list_by_extension(tmp_path) == {}
    (tmp_path / "only_dir.d").mkdir()
    assert ex.list_by_extension(tmp_path) == {}


def test_list_by_extension_accepts_str_and_sorts(ex, tmp_path):
    for n in ("z.md", "a.md", "m.md"):
        (tmp_path / n).write_text("")
    assert ex.list_by_extension(str(tmp_path)) == {".md": ["a.md", "m.md", "z.md"]}


def test_safe_write_creates_folders(ex, tmp_path):
    target = tmp_path / "a" / "b" / "c.txt"
    result = ex.safe_write(target, "hi")
    assert result == target
    assert target.read_text() == "hi"


def test_safe_write_overwrites_and_leaves_no_tmp(ex, tmp_path):
    target = tmp_path / "f.txt"
    ex.safe_write(target, "one")
    ex.safe_write(str(target), "two")
    assert target.read_text() == "two"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["f.txt"]


# 12 retry
def test_retry_succeeds_after_failures(ex):
    calls = []

    @ex.retry(3, (ConnectionError,))
    def fetch():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError
        return "ok"

    assert fetch() == "ok"
    assert len(calls) == 3


def test_retry_gives_up_and_raises_last_error(ex):
    calls = []

    @ex.retry(3)
    def always():
        calls.append(1)
        raise ValueError(len(calls))

    with pytest.raises(ValueError) as info:
        always()
    assert info.value.args == (3,)
    assert len(calls) == 3


def test_retry_does_not_catch_other_exceptions(ex):
    calls = []

    @ex.retry(5, (ConnectionError,))
    def f():
        calls.append(1)
        raise KeyError

    with pytest.raises(KeyError):
        f()
    assert len(calls) == 1


def test_retry_passes_args_and_keeps_name(ex):
    @ex.retry(2)
    def add(a, b=0):
        "docs"
        return a + b

    assert add(1, b=2) == 3
    assert add.__name__ == "add"
    assert add.__doc__ == "docs"


def test_retry_rejects_bad_times(ex):
    with pytest.raises(ValueError):
        ex.retry(0)
