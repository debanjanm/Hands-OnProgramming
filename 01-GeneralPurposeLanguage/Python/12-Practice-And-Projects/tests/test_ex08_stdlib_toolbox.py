import logging
from datetime import date

import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex08_stdlib_toolbox")


# 1 extract_emails
def test_extract_emails_lowercase_dedupe_order(ex):
    text = "Mail Bob@Example.com, or bob@example.com. Cc: a.b+c@x.co.uk"
    assert ex.extract_emails(text) == ["bob@example.com", "a.b+c@x.co.uk"]


def test_extract_emails_none_found(ex):
    assert ex.extract_emails("no emails here @ all") == []
    assert ex.extract_emails("") == []


def test_extract_emails_trailing_full_stop_removed(ex):
    assert ex.extract_emails("write to me@site.org.") == ["me@site.org"]


# 2 add_business_days
def test_add_business_days_friday_to_monday(ex):
    assert ex.add_business_days(date(2024, 3, 8), 1) == date(2024, 3, 11)


def test_add_business_days_full_week_and_zero(ex):
    assert ex.add_business_days(date(2024, 3, 6), 5) == date(2024, 3, 13)
    assert ex.add_business_days(date(2024, 3, 6), 0) == date(2024, 3, 6)


def test_add_business_days_from_weekend(ex):
    assert ex.add_business_days(date(2024, 3, 9), 1) == date(2024, 3, 11)
    assert ex.add_business_days(date(2024, 3, 10), 5) == date(2024, 3, 15)


def test_add_business_days_negative_rejected(ex):
    with pytest.raises(ValueError):
        ex.add_business_days(date(2024, 3, 6), -1)


# 3 word_frequencies
def test_word_frequencies_top_n(ex):
    assert ex.word_frequencies("the cat and The dog and the bird", 2) == [("the", 3), ("and", 2)]


def test_word_frequencies_ties_alphabetical(ex):
    assert ex.word_frequencies("b a b a c", 3) == [("a", 2), ("b", 2), ("c", 1)]


def test_word_frequencies_empty_and_large_n(ex):
    assert ex.word_frequencies("", 5) == []
    assert ex.word_frequencies("Hi, hi! don't", 10) == [("hi", 2), ("don't", 1)]


# 4 group_anagrams
def test_group_anagrams_basic(ex):
    out = ex.group_anagrams(["listen", "silent", "cat", "act", "dog"])
    assert out == [["act", "cat"], ["dog"], ["listen", "silent"]]


def test_group_anagrams_ignores_case_and_empty(ex):
    assert ex.group_anagrams([]) == []
    assert ex.group_anagrams(["Tea", "eat"]) == [["Tea", "eat"]]


def test_group_anagrams_all_different(ex):
    assert ex.group_anagrams(["b", "a"]) == [["a"], ["b"]]


# 5 tail
def test_tail_last_items(ex):
    assert ex.tail(["a", "b", "c", "d"], 2) == ["c", "d"]


def test_tail_one_shot_iterator(ex):
    assert ex.tail(iter(range(1000)), 3) == [997, 998, 999]


def test_tail_short_input_and_zero(ex):
    assert ex.tail([1], 5) == [1]
    assert ex.tail([1, 2, 3], 0) == []


def test_tail_negative_rejected(ex):
    with pytest.raises(ValueError):
        ex.tail([1], -1)


# 6 schedule
def test_schedule_round_robin_rooms(ex):
    assert ex.schedule(["Ann", "Bo", "Cy"], ["R1", "R2"]) == [
        ("Ann", "Bo", "R1"),
        ("Ann", "Cy", "R2"),
        ("Bo", "Cy", "R1"),
    ]


def test_schedule_too_few_people(ex):
    assert ex.schedule([], ["R1"]) == []
    assert ex.schedule(["Solo"], ["R1"]) == []


def test_schedule_pair_count(ex):
    assert len(ex.schedule(list("abcde"), ["x"])) == 10


# 7 compose
def test_compose_left_to_right(ex):
    f = ex.compose(str.strip, str.upper, lambda s: s + "!")
    assert f("  hi ") == "HI!"


def test_compose_no_functions_is_identity(ex):
    assert ex.compose()(5) == 5


def test_compose_order_matters(ex):
    add1 = lambda x: x + 1
    double = lambda x: x * 2
    assert ex.compose(add1, double)(3) == 8
    assert ex.compose(double, add1)(3) == 7


# 8 merge_configs
def test_merge_configs_deep(ex):
    out = ex.merge_configs('{"a": 1, "db": {"host": "x", "port": 1}}', '{"db": {"port": 2}}')
    assert out == '{\n  "a": 1,\n  "db": {\n    "host": "x",\n    "port": 2\n  }\n}'


def test_merge_configs_replaces_non_dicts_and_adds_keys(ex):
    import json

    out = json.loads(ex.merge_configs('{"a": [1], "b": {"x": 1}}', '{"a": [2, 3], "b": 5, "c": null}'))
    assert out == {"a": [2, 3], "b": 5, "c": None}


def test_merge_configs_sorted_keys(ex):
    assert ex.merge_configs('{"b": 1}', '{"a": 2}').index('"a"') < ex.merge_configs('{"b": 1}', '{"a": 2}').index('"b"')


def test_merge_configs_bad_json(ex):
    with pytest.raises(ValueError):
        ex.merge_configs("{", "{}")


# 9 summarize_dir
def test_summarize_dir_counts_by_extension(ex, tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.PY").write_text("")
    (tmp_path / "notes.txt").write_text("")
    (tmp_path / "README").write_text("")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.py").write_text("")
    out = ex.summarize_dir(tmp_path)
    assert out == {"(none)": 1, ".py": 3, ".txt": 1}
    assert list(out) == ["(none)", ".py", ".txt"]


def test_summarize_dir_empty_folder(ex, tmp_path):
    assert ex.summarize_dir(tmp_path) == {}


def test_summarize_dir_folders_not_counted(ex, tmp_path):
    (tmp_path / "x.d").mkdir()
    (tmp_path / "x.d" / "deep").mkdir()
    assert ex.summarize_dir(tmp_path) == {}


# 10 wrap_text
def test_wrap_text_example(ex):
    assert ex.wrap_text("    one two three\n    four", 12) == "  one two\n  three four"


def test_wrap_text_lines_fit_and_paragraphs_kept(ex):
    text = """
        The quick brown fox
        jumps over the lazy dog.

        Second   paragraph here.
    """
    out = ex.wrap_text(text, 20)
    assert all(len(line) <= 20 for line in out.splitlines())
    assert out.count("\n\n") == 1
    assert out.startswith("  The quick brown")
    assert "Second paragraph" in out


def test_wrap_text_empty(ex):
    assert ex.wrap_text("", 10) == ""
    assert ex.wrap_text("   \n  ", 10) == ""


# 11 grade_report
def test_grade_report_top_two(ex):
    out = ex.grade_report({"ann": 92.5, "bo": 71, "cy": 58.25}, 2)
    assert out == ["ann       92.5  A", "bo        71.0  C"]


def test_grade_report_boundaries(ex):
    scores = {"a": 90, "b": 80, "c": 70, "d": 60, "e": 59.9}
    out = ex.grade_report(scores, 5)
    assert [line[-1] for line in out] == list("ABCDF")


def test_grade_report_ties_and_k_larger_than_data(ex):
    out = ex.grade_report({"zed": 85, "amy": 85}, 10)
    assert [line.split()[0] for line in out] == ["amy", "zed"]
    assert ex.grade_report({}, 3) == []


# 12 Status + process_orders
def test_process_orders_counts(ex):
    log = logging.getLogger("t12a")
    result = ex.process_orders([{"id": 1, "qty": 2}, {"id": 2, "qty": 0}, {"id": 3}], log)
    assert result == {ex.Status.OK: 1, ex.Status.INVALID: 2}


def test_process_orders_logs_warnings(ex, caplog):
    log = logging.getLogger("t12b")
    with caplog.at_level(logging.WARNING, logger="t12b"):
        ex.process_orders([{"id": 1, "qty": 2}, {"id": 2, "qty": 0}, {"qty": "5"}], log)
    messages = [r.getMessage() for r in caplog.records]
    assert messages == ["order 2 skipped: qty=0", "order ? skipped: qty='5'"]
    assert all(r.levelno == logging.WARNING for r in caplog.records)
    assert caplog.records[0].args == (2, 0)  # lazy % formatting, not an f-string


def test_process_orders_clean_input_logs_nothing_and_bool_is_invalid(ex, caplog):
    log = logging.getLogger("t12c")
    with caplog.at_level(logging.WARNING, logger="t12c"):
        ok = ex.process_orders([{"id": 1, "qty": 1}], log)
        assert caplog.records == []
        bad = ex.process_orders([{"id": 2, "qty": True}], log)
    assert ok == {ex.Status.OK: 1, ex.Status.INVALID: 0}
    assert bad == {ex.Status.OK: 0, ex.Status.INVALID: 1}
    assert ex.process_orders([], log) == {ex.Status.OK: 0, ex.Status.INVALID: 0}
