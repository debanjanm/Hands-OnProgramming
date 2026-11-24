"""Tests for the task manager, grouped by milestone."""
import csv
import io
import json
import sqlite3
from datetime import date

import pytest

TODAY = date(2025, 6, 15)


# ---- Milestone 1: dates ----------------------------------------------------
class TestDates:
    def test_iso(self, dates):
        assert dates.parse_due("2025-12-31", TODAY) == date(2025, 12, 31)

    def test_today_tomorrow(self, dates):
        assert dates.parse_due("today", TODAY) == TODAY
        assert dates.parse_due("Tomorrow", TODAY) == date(2025, 6, 16)

    def test_relative(self, dates):
        assert dates.parse_due("+10d", TODAY) == date(2025, 6, 25)

    @pytest.mark.parametrize("bad", ["", "soon", "2025-13-01", "2025-02-30", "15/06/2025", "20250615", "+d"])
    def test_invalid(self, dates, bad):
        with pytest.raises(ValueError):
            dates.parse_due(bad, TODAY)

    def test_overdue_rules(self, dates):
        yesterday = date(2025, 6, 14)
        assert dates.is_overdue(yesterday, False, TODAY)
        assert not dates.is_overdue(TODAY, False, TODAY)
        assert not dates.is_overdue(yesterday, True, TODAY)
        assert not dates.is_overdue(None, False, TODAY)


# ---- Milestone 2/3: storage ------------------------------------------------
class TestStore:
    def test_add_and_get(self, store):
        t = store.add("Buy milk", priority=3, due=date(2025, 7, 1), tags=["Home", "home", " shop "])
        assert t.id == 1
        got = store.get(1)
        assert got.title == "Buy milk" and got.priority == 3
        assert got.due == date(2025, 7, 1)
        assert got.tags == ["home", "shop"]
        assert got.done is False

    def test_ids_increase(self, store):
        assert store.add("a").id == 1
        assert store.add("b").id == 2

    @pytest.mark.parametrize("title", ["", "   "])
    def test_empty_title_rejected(self, store, title):
        with pytest.raises(ValueError):
            store.add(title)

    def test_bad_priority_rejected(self, store):
        with pytest.raises(ValueError):
            store.add("x", priority=9)

    def test_missing_id(self, store, store_mod):
        with pytest.raises(store_mod.TaskNotFound):
            store.get(42)
        with pytest.raises(store_mod.TaskNotFound):
            store.mark_done(42)
        with pytest.raises(store_mod.TaskNotFound):
            store.delete(42)

    def test_done_hides_from_default_list(self, store):
        store.add("a")
        store.add("b")
        store.mark_done(1)
        assert [t.title for t in store.list()] == ["b"]
        assert [t.title for t in store.list(include_done=True)] == ["a", "b"]

    def test_delete(self, store):
        store.add("a")
        store.delete(1)
        assert store.list(include_done=True) == []

    def test_persists_between_connections(self, tmp_path, store_mod):
        path = str(tmp_path / "p.db")
        with store_mod.TaskStore(path) as s:
            s.add("keep me")
        with store_mod.TaskStore(path) as s:
            assert [t.title for t in s.list()] == ["keep me"]

    def test_sort_order(self, store):
        store.add("no due, high", priority=3)
        store.add("later", due=date(2025, 8, 1))
        store.add("soon low", priority=1, due=date(2025, 7, 1))
        store.add("soon high", priority=3, due=date(2025, 7, 1))
        assert [t.title for t in store.list()] == ["soon high", "soon low", "later", "no due, high"]

    def test_filter_tag_and_overdue(self, store):
        store.add("old", due=date(2025, 1, 1), tags=["work"])
        store.add("future", due=date(2030, 1, 1), tags=["work", "home"])
        store.add("plain")
        assert [t.title for t in store.list(tag="WORK")] == ["old", "future"]
        assert [t.title for t in store.list(tag="home")] == ["future"]
        assert [t.title for t in store.list(overdue_only=True, today=TODAY)] == ["old"]

    def test_search_title_and_tag(self, store):
        store.add("Pay Rent", tags=["money"])
        store.add("Call mum")
        store.mark_done(2)
        assert [t.title for t in store.search("rent")] == ["Pay Rent"]
        assert [t.title for t in store.search("MONEY")] == ["Pay Rent"]
        assert [t.title for t in store.search("mum")] == ["Call mum"]  # done tasks included
        assert store.search("zzz") == []

    def test_sql_injection_is_just_text(self, store):
        t = store.add("x'); DROP TABLE tasks;--")
        assert store.get(t.id).title.startswith("x')")


# ---- Milestone 4: export ---------------------------------------------------
class TestExport:
    @pytest.fixture
    def tasks(self, store):
        store.add("Write, test", priority=3, due=date(2025, 7, 1), tags=["a", "b"])
        store.add("Plain")
        store.mark_done(2)
        return store.list(include_done=True)

    def test_json(self, export_mod, tasks):
        data = json.loads(export_mod.to_json(tasks))
        assert data[0] == {"id": 1, "title": "Write, test", "priority": "high",
                           "due": "2025-07-01", "tags": ["a", "b"], "done": False}
        assert data[1]["due"] is None and data[1]["done"] is True

    def test_csv(self, export_mod, tasks):
        rows = list(csv.reader(io.StringIO(export_mod.to_csv(tasks))))
        assert rows[0] == ["id", "title", "priority", "due", "tags", "done"]
        assert rows[1] == ["1", "Write, test", "high", "2025-07-01", "a;b", "false"]
        assert rows[2] == ["2", "Plain", "normal", "", "", "true"]

    def test_empty(self, export_mod):
        assert json.loads(export_mod.to_json([])) == []
        assert export_mod.to_csv([]).strip() == "id,title,priority,due,tags,done"


# ---- Milestone 5/6: the CLI ------------------------------------------------
class TestCli:
    def test_add_then_list(self, run):
        code, out, _ = run("add", "Pay rent", "-p", "high", "-d", "2025-06-01", "-t", "home")
        assert code == 0 and "added task 1" in out
        code, out, _ = run("list")
        assert code == 0
        assert "Pay rent" in out and "high" in out and "#home" in out
        assert "OVERDUE" in out

    def test_empty_list(self, run):
        assert run("list") == (0, "no tasks\n", "")

    def test_relative_due_uses_frozen_today(self, run):
        run("add", "x", "-d", "+3d")
        assert "2025-06-18" in run("list")[1]

    def test_bad_date_exit_2(self, run):
        code, out, err = run("add", "x", "-d", "someday")
        assert code == 2 and out == ""
        assert err.startswith("error:") and "someday" in err

    def test_empty_title_exit_2(self, run):
        code, _, err = run("add", "  ")
        assert code == 2 and "title" in err

    def test_done_and_hidden(self, run):
        run("add", "a")
        assert run("done", "1")[0] == 0
        assert run("list")[1] == "no tasks\n"
        assert "[x]" in run("list", "--all")[1]

    def test_done_missing_exit_1(self, run):
        code, _, err = run("done", "99")
        assert code == 1 and "99" in err

    def test_delete(self, run):
        run("add", "a")
        code, out, _ = run("delete", "1")
        assert code == 0 and "deleted task 1" in out
        assert run("delete", "1")[0] == 1

    def test_list_filters(self, run):
        run("add", "old", "-d", "2025-01-01", "-t", "work")
        run("add", "new", "-d", "2030-01-01")
        out = run("list", "--overdue")[1]
        assert "old" in out and "new" not in out
        out = run("list", "--tag", "work")[1]
        assert "old" in out and "new" not in out

    def test_search(self, run):
        run("add", "Buy milk")
        assert "Buy milk" in run("search", "MILK")[1]
        assert run("search", "nothing") == (0, "no matches\n", "")

    def test_export_json_stdout(self, run):
        run("add", "a", "-p", "low")
        code, out, _ = run("export")
        assert code == 0
        assert json.loads(out)[0]["priority"] == "low"

    def test_export_csv_file(self, run, tmp_path):
        run("add", "a")
        target = tmp_path / "out.csv"
        code, out, _ = run("export", "--format", "csv", "-o", str(target))
        assert code == 0 and "1 tasks" in out
        assert target.read_text().splitlines()[0] == "id,title,priority,due,tags,done"

    def test_export_unwritable_exit_3(self, run, tmp_path):
        code, _, err = run("export", "-o", str(tmp_path / "no_such_dir" / "x.json"))
        assert code == 3 and err.startswith("error:")

    @pytest.mark.parametrize("argv", [[], ["bogus"], ["done", "abc"], ["add"], ["add", "x", "-p", "urgent"]])
    def test_usage_errors_exit_2(self, run, argv):
        assert run(*argv)[0] == 2

    def test_db_from_env_var(self, cli, tmp_path, monkeypatch, capsys):
        db = tmp_path / "env.db"
        monkeypatch.setenv("TASKMAN_DB", str(db))
        assert cli.main(["add", "via env"]) == 0
        capsys.readouterr()
        assert db.exists()
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT title FROM tasks").fetchone() == ("via env",)

    def test_db_flag_beats_env(self, cli, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("TASKMAN_DB", str(tmp_path / "env.db"))
        flag_db = tmp_path / "flag.db"
        cli.main(["--db", str(flag_db), "add", "x"])
        assert flag_db.exists() and not (tmp_path / "env.db").exists()

    def test_bad_database_exit_3(self, cli, tmp_path, capsys):
        bad = tmp_path / "notadb.db"
        bad.write_text("this is not a sqlite file" * 50)
        assert cli.main(["--db", str(bad), "list"]) == 3
        assert capsys.readouterr().err.startswith("error:")

    def test_verbose_logs(self, run, caplog):
        import logging
        with caplog.at_level(logging.INFO, logger="taskman"):
            run("-v", "add", "logged")
        assert any("added task" in r.getMessage() for r in caplog.records)


def test_tag_separator_is_rejected_before_write(store):
    with pytest.raises(ValueError, match="comma"):
        store.add("task", tags=["work,home"])
    assert store.list(include_done=True) == []
