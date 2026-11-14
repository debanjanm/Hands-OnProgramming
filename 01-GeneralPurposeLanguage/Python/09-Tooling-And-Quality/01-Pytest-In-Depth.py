import os
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

# 01. pytest In Depth - Introduction
# ------------------------------------
# - pytest is THE standard Python test runner. unittest (see
#   06-Standard Library/09-Unittest-Basics.py) ships with Python, but pytest
#   needs far less ceremony and gives far better failure messages.
# - Why people switch from unittest:
#     * plain `assert x == y` instead of self.assertEqual / assertTrue / ...
#     * on failure pytest REWRITES the assert and shows both sides + a diff
#     * fixtures (dependency injection) replace setUp/tearDown inheritance
#     * parametrize runs one test body over many inputs, each reported alone
#     * marks, selection flags, and a big plugin ecosystem
#     * it also RUNS your old unittest.TestCase classes unchanged
# - This file TEACHES by building tiny projects inside a temp directory and
#   running real pytest on them (python -m pytest in a subprocess), so you see
#   the genuine output. Nothing is written inside the repository.
# - Needs: pip install pytest (this file exits politely if it is missing).

try:
    import pytest
except ImportError:
    print("pytest is not installed (pip install pytest) - skipping this demo.")
    sys.exit(0)

print("# 01. pytest In Depth - Introduction")
print("# ------------------------------------")

# 02. Demo Helpers (not pytest itself - just plumbing for this file)
# ------------------------------------
# - We run pytest in a CHILD process with a clean environment:
#     * PYTHONPATH removed  -> no surprise imports from the caller's shell
#     * PYTEST_* removed    -> a stray PYTEST_ADDOPTS cannot change results
#     * PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -> only core pytest, so the output
#       is the same on every machine regardless of installed plugins
#     * PYTHONDONTWRITEBYTECODE=1 -> no __pycache__ clutter
# - Output is "scrubbed": timings, platform/rootdir lines and temp paths are
#   removed so the transcript is stable and readable.
# - Exit codes worth memorising:
#     0 all passed | 1 some failed | 2 interrupted (Ctrl-C / -x) |
#     3 internal error | 4 command-line usage error | 5 no tests collected

_TMP = tempfile.TemporaryDirectory(prefix="pytest_demo_")
BASE = Path(_TMP.name)

ENV = {k: v for k, v in os.environ.items()
       if not k.startswith("PYTEST_") and k != "PYTHONPATH"}
ENV.update(PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
           NO_COLOR="1", COLUMNS="100")


def scrub(text, proj):
    for p in sorted({str(proj), str(Path(proj).resolve())}, key=len, reverse=True):
        text = text.replace(p, "<tmp>")
    skip = ("platform ", "rootdir:", "configfile:", "plugins:", "cachedir:")
    lines = [ln.rstrip() for ln in text.splitlines() if not ln.startswith(skip)]
    text = "\n".join(lines)
    text = re.sub(r" in \d+\.\d+s( \(\d+:\d+:\d+\))?", "", text)  # timings
    return text.strip("\n")


def make_project(name, files):
    """Create BASE/name and write dedented files into it."""
    proj = BASE / name
    proj.mkdir()
    if "pytest.ini" not in files:  # pin rootdir here; never look upward
        files = {"pytest.ini": "[pytest]\n", **files}
    for fname, body in files.items():
        f = proj / fname
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(textwrap.dedent(body).lstrip("\n"))
    return proj


def show(proj, fname, max_lines=40):
    text = (Path(proj) / fname).read_text().rstrip("\n")
    print(f"  --- {fname} ---")
    for ln in text.splitlines()[:max_lines]:
        print(f"  | {ln}")


def pytest_run(proj, *args, cache=False, max_lines=60):
    """Run `python -m pytest <args>` in proj and print the scrubbed output."""
    cmd = [sys.executable, "-m", "pytest"]
    if not cache:
        cmd += ["-p", "no:cacheprovider"]  # keep the .pytest_cache dir away
    r = subprocess.run(cmd + list(args), capture_output=True, text=True,
                       cwd=proj, env=ENV, timeout=60)
    out = scrub(r.stdout + r.stderr, proj).splitlines()
    print(f"  $ pytest {shlex.join(args)}    -> exit code {r.returncode}")
    for ln in out[:max_lines]:
        print(f"  | {ln}")
    if len(out) > max_lines:
        print(f"  | ... ({len(out) - max_lines} more lines trimmed)")
    return r


print("\n# 02. Demo Helpers")
print("pytest runs in a child process with a clean environment; output is scrubbed.")

# 03. The Smallest Possible pytest Project
# ------------------------------------
# - Discovery rules (defaults, all configurable):
#     files      test_*.py or *_test.py
#     functions  test_*          (module level)
#     classes    Test*           (NO __init__ method) containing test_* methods
# - A test PASSES if it finishes without raising. That is the whole contract.
# - `python -m pytest` (vs bare `pytest`) also puts the current directory on
#   sys.path, so `import calc` works. Prefer it while learning.

print("\n# 03. The Smallest Possible pytest Project")
proj = make_project("calc_proj", {
    "calc.py": '''
        def add(a, b):
            return a + b

        def divide(a, b):
            if b == 0:
                raise ValueError("cannot divide by zero")
            return a / b

        def average(numbers):
            return sum(numbers) / len(numbers)
    ''',
    "test_calc.py": '''
        from calc import add, divide, average

        def test_add():
            assert add(2, 3) == 5

        def test_divide():
            assert divide(10, 4) == 2.5

        def test_average():
            assert average([1, 2, 3, 4]) == 2.5
    ''',
})
show(proj, "test_calc.py")
pytest_run(proj, "-v")
print("  # No class, no self.assertEqual, no main(): just functions and `assert`.")

# 04. Plain assert And Rewritten Failure Messages
# ------------------------------------
# - pytest rewrites `assert` statements at import time (assertion rewriting)
#   so that on failure it can show the VALUES of every sub-expression and a
#   readable diff for strings, lists, dicts and sets.
# - This is the single biggest quality-of-life win over unittest: you see WHY
#   it failed without adding debug prints.
# - Output marker meanings: `>` the failing line, `E` the explanation.
# - --tb=short trims the code context; --tb=line gives one line per failure;
#   --tb=no hides tracebacks; -vv shows full diffs of long structures.

print("\n# 04. Plain assert And Rewritten Failure Messages")
proj = make_project("failing_proj", {
    "test_fail.py": '''
        import pytest

        def test_numbers():
            total = 2 + 2
            assert total == 5

        def test_dicts():
            expected = {"name": "Asha", "age": 30, "city": "Pune"}
            actual = {"name": "Asha", "age": 31, "city": "Pune"}
            assert actual == expected

        def test_lists():
            assert [1, 2, 3, 4] == [1, 2, 4, 3]

        def test_strings():
            assert "hello world" == "hello there"

        def test_membership():
            assert "x" in ["a", "b", "c"]

        def test_floats_naive():
            assert 0.30001 == pytest.approx(0.3)
    ''',
})
pytest_run(proj, "--tb=short", "-q", max_lines=70)
print("  # Every failure shows the compared values; dict/list/str get a diff.")
print("  # Exit code 1 = at least one test failed.")

# 05. pytest.raises - Asserting That Code Raises
# ------------------------------------
# - `with pytest.raises(SomeError):` passes only if the block raises that
#   exception (or a subclass); it FAILS if nothing is raised.
# - match="regex" runs re.search against str(exception) - use it so you do not
#   accept the right type with the wrong message.
# - `as excinfo` gives you .type, .value (the exception object), .traceback.
# - Gotchas:
#     * code after the raising line INSIDE the with-block never runs
#     * inspect excinfo OUTSIDE the with-block (it is filled in on exit)
#     * pytest.raises(Exception) is too broad - it hides unrelated bugs
# - These helpers work in a plain script too, so we can print real values:

print("\n# 05. pytest.raises")


def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


with pytest.raises(ValueError, match="divide by zero") as excinfo:
    divide(1, 0)
print("excinfo.type      :", excinfo.type)
print("excinfo.typename  :", excinfo.typename)
print("excinfo.value     :", repr(excinfo.value))
print("str(excinfo.value):", str(excinfo.value))
print("excinfo.match()   :", bool(excinfo.match(r"zero$")))

try:
    with pytest.raises(ValueError):
        divide(1, 2)  # does NOT raise -> pytest.raises itself fails
except pytest.fail.Exception as e:
    print("no exception raised ->", str(e))

try:
    with pytest.raises(ValueError, match="negative"):
        divide(1, 0)  # raises ValueError, but the message does not match
except AssertionError as e:
    print("wrong message ->", str(e).splitlines()[0])

# - Also: pytest.warns(DeprecationWarning) checks warnings the same way, and
#   `pytest.raises(E, check=...)` exists only in newer pytest (not used here).

# 06. pytest.approx - Comparing Floats Safely
# ------------------------------------
# - 0.1 + 0.2 != 0.3 in binary floating point. approx compares within a
#   tolerance: default relative 1e-6 and absolute 1e-12 (the larger wins).
# - Works on numbers, lists, tuples, dicts and numpy arrays.
# - Do NOT use approx for money - use decimal.Decimal and compare exactly.

print("\n# 06. pytest.approx")
print("0.1 + 0.2 == 0.3                    ->", 0.1 + 0.2 == 0.3)
print("0.1 + 0.2 == approx(0.3)            ->", 0.1 + 0.2 == pytest.approx(0.3))
print("repr(approx(0.3))                   ->", repr(pytest.approx(0.3)))
print("[0.1+0.2, 1/3] == approx([.3, .333333]) ->",
      [0.1 + 0.2, 1 / 3] == pytest.approx([0.3, 0.333333], rel=1e-5))
print("{'a': 0.1+0.2} == approx({'a': .3}) ->", {"a": 0.1 + 0.2} == pytest.approx({"a": 0.3}))
print("100.5 == approx(100, rel=0.01)      ->", 100.5 == pytest.approx(100, rel=0.01))
print("1.05 == approx(1, abs=0.1)          ->", 1.05 == pytest.approx(1, abs=0.1))
print("0.0001 == approx(0)  (rel useless at 0) ->", 0.0001 == pytest.approx(0))
print("0.0001 == approx(0, abs=1e-3)       ->", 0.0001 == pytest.approx(0, abs=1e-3))

# 07. Fixtures - Setup/Teardown As Dependency Injection
# ------------------------------------
# - A fixture is a function decorated with @pytest.fixture. A test (or another
#   fixture) asks for it simply by naming it as a PARAMETER. pytest runs the
#   fixture first and passes the result in. No inheritance, no self.
# - `return value`        -> setup only.
# - `yield value` + code  -> code AFTER the yield is TEARDOWN; it runs even if
#   the test failed. (One fixture = setup and teardown kept side by side.)
# - scope controls how long the value lives and how often setup runs:
#     function (default)  new for every test
#     class / module      once per class / file
#     package / session   once per package / whole run  (expensive things:
#                         DB connection, docker container, loaded model)
# - A fixture may request other fixtures; a fixture can only depend on fixtures
#   of equal or WIDER scope (session fixture cannot use a function fixture).
# - autouse=True applies the fixture to every test in its reach, even if no
#   test names it (use sparingly - it is implicit magic).
# - `--setup-show` prints SETUP / TEARDOWN so the order is visible:
#     S=session  M=module  F=function

print("\n# 07. Fixtures")
proj = make_project("fixture_proj", {
    "test_fixtures.py": '''
        import pytest

        @pytest.fixture(scope="session")
        def config():
            return {"env": "test"}

        @pytest.fixture(scope="module")
        def db(config):                       # fixture using another fixture
            conn = {"open": True, "env": config["env"]}
            yield conn                        # <- test runs here
            conn["open"] = False              # teardown (runs after the tests)

        @pytest.fixture
        def user(db):                         # function scope: new per test
            return {"name": "asha", "db": db}

        @pytest.fixture(autouse=True)
        def reset_state():                    # no test asks for me by name
            yield

        def test_user_has_db(user):
            assert user["db"]["open"] is True

        def test_each_test_gets_a_fresh_user(user):
            user["name"] = "changed"          # does not leak into other tests
            assert user["name"] == "changed"

        def test_db_is_shared_within_module(db):
            assert db["env"] == "test"
    ''',
})
show(proj, "test_fixtures.py", max_lines=50)
pytest_run(proj, "--setup-show", "-q")
print("  # config + db are set up ONCE (S, M); `user` and the autouse fixture")
print("  # are rebuilt for every test (F). db teardown happens after the module.")

# - Teardown after a FAILING test still runs - that is the point of yield:
proj = make_project("teardown_proj", {
    "test_cleanup.py": '''
        import pytest

        @pytest.fixture
        def temp_resource():
            yield "res"
            # cleanup code goes here - it runs even when the test fails

        def test_that_fails(temp_resource):
            assert temp_resource == "something else"
    ''',
})
pytest_run(proj, "--tb=no", "-q", "--setup-show")
print("  # The test FAILED (F) yet TEARDOWN still ran right after it.")

# - Gotcha: a fixture that raises during SETUP reports an ERROR (not a FAIL):
#   the test body never ran. Read the first line of the error to find it.
# - request.addfinalizer(fn) is the older, callback-style teardown. With
#   `yield` you rarely need it, except to register several cleanups as you go.

# 08. conftest.py - Fixtures Shared Across Files
# ------------------------------------
# - conftest.py is a special file pytest loads automatically (never import
#   from it). Fixtures defined there are visible to every test in that
#   directory and BELOW it. A nearer conftest overrides a farther one.
# - Put shared fixtures/hooks there; keep one-off fixtures in the test file.
# - Gotcha: two test files with the SAME basename in different folders and no
#   __init__.py collide ("import file mismatch"). Give them unique names, or
#   add __init__.py files so each becomes part of a package.

print("\n# 08. conftest.py")
proj = make_project("conftest_proj", {
    "conftest.py": '''
        import pytest

        @pytest.fixture
        def sample_users():
            return ["asha", "ravi", "meena"]
    ''',
    "tests/test_users.py": '''
        def test_count(sample_users):               # no import needed
            assert len(sample_users) == 3
    ''',
    "tests/sub/test_names.py": '''
        def test_first(sample_users):               # visible in sub-folders too
            assert sample_users[0] == "asha"
    ''',
})
pytest_run(proj, "-v")

proj = make_project("collide_proj", {
    "a/test_utils.py": "def test_a():\n    pass\n",
    "b/test_utils.py": "def test_b():\n    pass\n",
})
pytest_run(proj, "-q", max_lines=14)
print("  # Same basename, no __init__.py -> collection error. Rename or add __init__.py.")

# 09. Parametrization - One Test Body, Many Inputs
# ------------------------------------
# - @pytest.mark.parametrize("names", [values...]) generates one INDEPENDENT
#   test per value; each passes/fails and is selectable on its own.
# - Several args: "a, b, expected" with a list of tuples.
# - ids=[...] gives readable test names (otherwise pytest builds them from the
#   values, e.g. 1-2-3). Good ids make failure reports self-explaining.
# - Stack decorators and you get the CROSS PRODUCT (2 x 2 = 4 tests).
# - pytest.param(value, id=..., marks=...) tweaks ONE case: expected failure,
#   skip, custom id.
# - Gotcha: values are built at import (collection) time - keep them cheap and
#   do not parametrize with mutable objects you then modify.

print("\n# 09. Parametrization")
proj = make_project("param_proj", {
    "test_param.py": '''
        import pytest

        @pytest.mark.parametrize(
            "a, b, expected",
            [(1, 2, 3), (0, 0, 0), (-1, 1, 0)],
            ids=["positives", "zeros", "cancel-out"],
        )
        def test_add(a, b, expected):
            assert a + b == expected

        @pytest.mark.parametrize("x", [1, 2])
        @pytest.mark.parametrize("y", [10, 20])
        def test_cross_product(x, y):               # 2 x 2 = 4 tests
            assert x < y

        @pytest.mark.parametrize("n", [
            1,
            pytest.param(2, marks=pytest.mark.xfail(reason="known bug #12")),
            pytest.param(3, marks=pytest.mark.skip(reason="not ready")),
            pytest.param(4, id="four"),
        ])
        def test_with_marks(n):
            assert n != 2
    ''',
})
pytest_run(proj, "-v", "-rxs")

# - Pattern: parametrize BOTH good and bad inputs, expecting an error in some.
#   contextlib.nullcontext() stands in for "expect no exception".
proj = make_project("param_raises_proj", {
    "test_param_raises.py": '''
        import pytest
        from contextlib import nullcontext

        def to_int(text):
            return int(text)

        @pytest.mark.parametrize("text, expectation", [
            ("42", nullcontext(42)),
            ("x1", pytest.raises(ValueError)),
        ])
        def test_to_int(text, expectation):
            with expectation as expected:
                assert to_int(text) == expected
    ''',
})
pytest_run(proj, "-q")

# 10. Built-in Fixtures: tmp_path, monkeypatch, capsys/capfd, caplog
# ------------------------------------
# - tmp_path   : a fresh pathlib.Path directory per test (older: tmpdir).
#                Test file IO against it - never against real project files.
# - monkeypatch: temporarily change things; ALL changes are undone after the
#                test:  setattr / delattr / setitem / delitem / setenv /
#                delenv / syspath_prepend / chdir.
# - capsys     : capture what code prints to stdout/stderr -> readouterr().
# - capfd      : same but at the file-descriptor level, so it also catches
#                output from subprocesses and C extensions.
# - caplog     : capture logging records (see 06-Standard Library/07-Logging.py)
#                .records, .messages, .text, and caplog.at_level(...)

print("\n# 10. Built-in Fixtures")
proj = make_project("builtin_proj", {
    "app.py": '''
        import logging
        import os

        log = logging.getLogger("app")

        def greet(name):
            print(f"Hello, {name}!")

        def region():
            return os.environ.get("APP_REGION", "local")

        def save_note(path, text):
            path.write_text(text)
            return path

        def fetch_price(item):
            raise RuntimeError("real network call - never in unit tests")

        def risky(n):
            if n < 0:
                log.warning("negative input: %s", n)
                return 0
            return n
    ''',
    "test_builtins.py": '''
        import logging
        import os
        import app

        def test_tmp_path(tmp_path):
            note = app.save_note(tmp_path / "note.txt", "hi")
            assert note.read_text() == "hi"
            assert note.parent == tmp_path

        def test_monkeypatch_env(monkeypatch):
            assert app.region() == "local"
            monkeypatch.setenv("APP_REGION", "eu-west")
            assert app.region() == "eu-west"

        def test_env_is_restored_after_previous_test():
            assert "APP_REGION" not in os.environ

        def test_monkeypatch_delenv(monkeypatch):
            monkeypatch.setenv("APP_REGION", "x")
            monkeypatch.delenv("APP_REGION")
            monkeypatch.delenv("NEVER_SET", raising=False)   # no KeyError
            assert app.region() == "local"

        def test_monkeypatch_setattr(monkeypatch):
            monkeypatch.setattr(app, "fetch_price", lambda item: 7)
            assert app.fetch_price("book") == 7

        def test_monkeypatch_delattr(monkeypatch):
            monkeypatch.delattr(app, "greet")
            assert not hasattr(app, "greet")

        def test_monkeypatch_setitem_and_chdir(monkeypatch, tmp_path):
            data = {"mode": "prod"}
            monkeypatch.setitem(data, "mode", "test")
            assert data["mode"] == "test"
            monkeypatch.chdir(tmp_path)
            assert os.getcwd() == str(tmp_path.resolve())

        def test_capsys(capsys):
            app.greet("Asha")
            captured = capsys.readouterr()
            assert captured.out == "Hello, Asha!\\n"
            assert captured.err == ""

        def test_capfd(capfd):
            os.write(1, b"raw fd write\\n")        # bypasses sys.stdout
            assert "raw fd write" in capfd.readouterr().out

        def test_caplog(caplog):
            with caplog.at_level(logging.WARNING, logger="app"):
                assert app.risky(-5) == 0
            assert "negative input: -5" in caplog.messages
            assert caplog.records[0].levelname == "WARNING"
    ''',
})
show(proj, "test_builtins.py", max_lines=12)
print("  | ... (full file generated in temp dir)")
pytest_run(proj, "-v")
print("  # Note test_env_is_restored_...: monkeypatch undid setenv automatically.")

# 11. Marks: skip, skipif, xfail, custom marks
# ------------------------------------
# - @pytest.mark.skip(reason=...)       never run it
# - @pytest.mark.skipif(cond, reason=...) skip when the condition is true
#   (platform, Python version, missing optional dependency)
# - pytest.importorskip("numpy")        skip the test if the import fails
# - @pytest.mark.xfail(reason=...)      "expected failure": a KNOWN bug.
#     fails  -> reported xfailed (not a red build)
#     passes -> XPASS (just noted)... unless strict=True, then XPASS = FAIL,
#     which forces you to remove the marker once the bug is fixed.
# - Custom marks (slow, db, integration ...) let you select groups with -m.
#   REGISTER them (pytest.ini / pyproject.toml) and add --strict-markers so a
#   typo like @pytest.mark.slwo is an error instead of a silently ignored tag.
#   pyproject.toml equivalent:
#       [tool.pytest.ini_options]
#       markers = ["slow: takes long", "db: needs a database"]
#       addopts = "--strict-markers"

print("\n# 11. Marks")
proj = make_project("marks_proj", {
    "pytest.ini": '''
        [pytest]
        markers =
            slow: tests that take a long time
            db: tests that need a database
        addopts = --strict-markers
    ''',
    "test_marks.py": '''
        import sys
        import pytest

        @pytest.mark.skip(reason="feature not built yet")
        def test_skipped():
            assert False

        @pytest.mark.skipif(sys.version_info >= (3, 8), reason="only for ancient Pythons")
        def test_skipif():
            assert False

        @pytest.mark.xfail(reason="known bug #101")
        def test_known_bug():
            assert 1 + 1 == 3

        @pytest.mark.xfail(strict=True, reason="bug fixed? remove this mark")
        def test_strict_xpass():
            assert True                       # unexpectedly passes -> FAILED

        @pytest.mark.slow
        def test_slow_report():
            assert sum(range(1000)) == 499500

        @pytest.mark.db
        def test_db_query():
            assert True

        def test_fast():
            assert True
    ''',
    "test_typo.py": '''
        import pytest

        @pytest.mark.slwo                     # typo - not registered
        def test_typo():
            pass
    ''',
})
show(proj, "pytest.ini")
pytest_run(proj, "test_marks.py", "-q", "-rsxXf", "--tb=no")
print("  # -r letters add a short summary: s=skipped x=xfailed X=xpassed f=failed")
print("  # Note the strict xfail that unexpectedly passed is reported as FAILED.")
print("  # -m selects by mark expression:")
pytest_run(proj, "test_marks.py", "-q", "-m", "slow or db", "--tb=no")
pytest_run(proj, "test_marks.py", "-q", "-m", "not slow and not skip", "--tb=no", "--co")
print("  # --strict-markers turns a typo'd mark into a clear error:")
pytest_run(proj, "test_typo.py", "-q", max_lines=8)

# 12. Selection And Reporting Flags
# ------------------------------------
# - Running one thing (node ids):   pytest tests/test_x.py::TestCart::test_add
# - -k "expr"      select by substring/boolean of test names: -k "login and not bad"
# - -x             stop at the FIRST failure         (exit 2)
# - --maxfail=N    stop after N failures
# - --lf / --ff    rerun only Last Failed / run failed First (needs the cache
#                  plugin, i.e. do not disable cacheprovider)
# - --sw           "stepwise": stop at a failure, resume from it next time
# - -q / -v / -vv  quieter / more verbose / full diffs
# - --tb=auto|long|short|line|no|native   traceback style
# - -rA            end-of-run summary of ALL outcomes (-rf failed, -rs skipped)
# - --collect-only (--co) list what WOULD run, without running it
# - -s             do not capture stdout (see print() live); same as --capture=no
# - --durations=5  show the 5 slowest tests

print("\n# 12. Selection And Reporting Flags")
proj = make_project("select_proj", {
    "test_sel.py": '''
        class TestCart:
            def test_add(self):
                assert True

            def test_remove(self):
                assert True

        def test_login_ok():
            assert True

        def test_login_bad_password():
            assert "secret" == "Secret"

        def test_logout():
            assert True

        def test_profile():
            assert 1 == 2
    ''',
})
pytest_run(proj, "--collect-only", "-q")
print("  # -k picks by name; boolean logic works:")
pytest_run(proj, "-k", "login and not bad", "-v", "--tb=no")
print("  # node id selects exactly one test (note the class in the path):")
pytest_run(proj, "test_sel.py::TestCart::test_add", "-v", "--tb=no")
print("  # -x stops at the first failure, --maxfail=2 allows two:")
pytest_run(proj, "-x", "-q", "--tb=line")
pytest_run(proj, "--maxfail=2", "-q", "--tb=no")
print("  # -rA prints a summary of every outcome at the end:")
pytest_run(proj, "-q", "--tb=no", "-rA")
print("  # --lf re-runs only what failed last time (first run writes the cache):")
pytest_run(proj, "-q", "--tb=no", cache=True)
pytest_run(proj, "--lf", "-q", "--tb=no", cache=True)

# 13. Mocking: unittest.mock And monkeypatch
# ------------------------------------
# - Mock = replace a collaborator (HTTP client, clock, DB) so a unit test is
#   fast and deterministic.
# - pytest has NO built-in `mocker`; that comes from the pytest-mock plugin
#   (pip install pytest-mock) and is just a thin wrapper over unittest.mock.
#   Without the plugin use either:
#     * monkeypatch.setattr(obj, "name", fake)      - simple replacement
#     * unittest.mock.patch("module.name")          - gives a Mock you can
#       inspect (call_count, assert_called_with, side_effect...)
# - GOLDEN RULE: patch the name WHERE IT IS LOOKED UP, not where it is defined.
#   `from app import fetch_price` copies the name into report.py, so patching
#   "app.fetch_price" does NOT affect report.fetch_price.
# - autospec=True makes the mock enforce the real function's signature, which
#   catches tests that call a mock in a way the real code never could.

print("\n# 13. Mocking")
proj = make_project("mock_proj", {
    "app.py": '''
        def fetch_price(item):
            raise RuntimeError("real network call - never in unit tests")

        def total_price(items):
            return sum(fetch_price(i) for i in items)
    ''',
    "report.py": '''
        from app import fetch_price          # name copied into THIS module

        def cost_with_tax(item):
            return fetch_price(item) * 2
    ''',
    "test_mock.py": '''
        from unittest import mock
        import app
        import report

        def test_patch_context_manager():
            with mock.patch("app.fetch_price", return_value=5) as fake:
                assert app.total_price(["a", "b"]) == 10
            assert fake.call_count == 2
            fake.assert_any_call("a")

        @mock.patch("app.fetch_price", side_effect=[1, 2, 3])
        def test_patch_decorator(fake):               # mock arrives as an arg
            assert app.total_price(["x", "y", "z"]) == 6

        def test_monkeypatch_version(monkeypatch):
            monkeypatch.setattr(app, "fetch_price", lambda item: 10)
            assert app.total_price(["a"]) == 10

        def test_autospec_catches_bad_calls():
            with mock.patch("app.fetch_price", autospec=True) as fake:
                try:
                    fake("a", "unexpected extra argument")
                except TypeError as exc:
                    assert "too many positional arguments" in str(exc)
                else:
                    raise AssertionError("autospec should have rejected this")

        def test_patch_where_it_is_USED():
            with mock.patch("report.fetch_price", return_value=4):
                assert report.cost_with_tax("a") == 8

        def test_patch_WRONG_place_still_hits_real_function():
            with mock.patch("app.fetch_price", return_value=4):
                assert report.cost_with_tax("a") == 8     # RuntimeError!
    ''',
})
pytest_run(proj, "--tb=line", "-q")
print("  # The last test fails with the REAL RuntimeError: the patch hit app.py,")
print("  # but report.py kept its own copy of the function name.")

# - A tiny direct look at what a Mock records (works in any script):
from unittest import mock

fake_client = mock.Mock()
fake_client.get.return_value = {"status": 200}
print("mock result        :", fake_client.get("/users", timeout=3))
print("call_args          :", fake_client.get.call_args)
print("call_count         :", fake_client.get.call_count)
fake_client.get.assert_called_once_with("/users", timeout=3)
print("assert_called_once_with passed (it raises AssertionError otherwise)")

# 14. Testing Exceptions, CLIs, Files, Time, Randomness
# ------------------------------------
# - EXCEPTIONS: pytest.raises with match=   (section 05)
# - CLI: make main(argv=None) accept an argv list, so tests call
#   main(["--flag"]) directly - no subprocess needed. argparse errors exit
#   via SystemExit(2) and write to stderr -> pytest.raises(SystemExit) + capsys.
# - FILE IO: take a path argument and test with tmp_path.
# - TIME: never call datetime.now() deep inside logic. INJECT the clock
#   (a parameter or a callable) and pass a fixed datetime in tests.
# - RANDOMNESS: take a random.Random instance (or seed) and use a fixed seed.
# - These are all the same idea: make the hidden input (argv, files, clock,
#   random) an explicit parameter, then tests control it.

print("\n# 14. Testing CLIs, Files, Time, Randomness")
proj = make_project("seams_proj", {
    "tools.py": '''
        import argparse
        import datetime as dt
        import random
        from pathlib import Path

        def main(argv=None):
            parser = argparse.ArgumentParser(prog="greet")
            parser.add_argument("name")
            parser.add_argument("--shout", action="store_true")
            args = parser.parse_args(argv)
            msg = f"hello {args.name}"
            print(msg.upper() if args.shout else msg)
            return 0

        def is_weekend(now=None):                 # injected clock
            now = now or dt.datetime.now()
            return now.weekday() >= 5

        def pick_winner(names, rng=random):       # injected randomness
            return rng.choice(names)

        def word_count(path):
            return len(Path(path).read_text().split())
    ''',
    "test_tools.py": '''
        import datetime as dt
        import random
        import pytest
        import tools

        def test_cli_output(capsys):
            assert tools.main(["bob", "--shout"]) == 0
            assert capsys.readouterr().out == "HELLO BOB\\n"

        def test_cli_missing_argument(capsys):
            with pytest.raises(SystemExit) as exc:
                tools.main([])
            assert exc.value.code == 2
            assert "required: name" in capsys.readouterr().err

        def test_time_is_injected():
            saturday = dt.datetime(2024, 1, 6, 12, 0)
            monday = dt.datetime(2024, 1, 8, 12, 0)
            assert tools.is_weekend(saturday) is True
            assert tools.is_weekend(monday) is False

        def test_randomness_is_seeded():
            names = ["asha", "ravi", "meena", "john"]
            first = tools.pick_winner(names, random.Random(42))
            again = tools.pick_winner(names, random.Random(42))
            assert first == again                 # same seed, same winner

        def test_file_io(tmp_path):
            f = tmp_path / "words.txt"
            f.write_text("one two three\\nfour")
            assert tools.word_count(f) == 4
    ''',
})
pytest_run(proj, "-v")
print("  # No sleeping, no real clock, no real files, no luck involved.")

# 15. Test Layout And Naming Rules
# ------------------------------------
# - Typical layout (src-layout is the modern recommendation):
#       myproject/
#           pyproject.toml          <- pytest config lives here
#           src/mypkg/__init__.py
#           src/mypkg/core.py
#           tests/
#               conftest.py         <- shared fixtures
#               test_core.py        <- mirrors src/mypkg/core.py
#               integration/test_db.py
# - Rules: files test_*.py / *_test.py; functions test_*; classes Test*
#   WITHOUT __init__. A class is just a namespace for grouping - no self state
#   is shared between methods (each test gets a NEW instance).
# - Change discovery in config: python_files = check_*.py  python_classes = Check*
# - Gotcha: a helper function named `check_x` or a class `TestHelper` with an
#   __init__ is silently/loudly NOT collected - tests you think exist may not.
#   ALWAYS look at the collected count (or --collect-only).

print("\n# 15. Test Layout And Naming Rules")
proj = make_project("layout_proj", {
    "test_layout.py": '''
        def test_collected():
            pass

        def check_not_collected():           # wrong prefix
            pass

        class TestGood:
            def test_method(self):
                pass

            def helper(self):                # not test_*
                pass

        class TestBad:
            def __init__(self):              # classes with __init__ are skipped
                self.x = 1

            def test_never_runs(self):
                pass
    ''',
})
pytest_run(proj, "--collect-only", "-q", max_lines=16)
print("  # Only 2 tests collected; TestBad produced a warning and was ignored.")

# 16. AAA Pattern And One Behavior Per Test
# ------------------------------------
# - AAA = Arrange (build inputs/fixtures), Act (call ONE thing), Assert
#   (check the outcome). Separate the three with blank lines.
# - Aim for ONE BEHAVIOR per test. That does not forbid two `assert`s if they
#   describe the same behavior (status code AND body of one response), but
#   it forbids testing "everything about the cart" in one function: when it
#   fails you cannot tell which promise broke.
# - Name tests like sentences: test_withdraw_more_than_balance_raises, not
#   test_withdraw2.
# - Test BEHAVIOR (inputs -> outputs), not implementation details; otherwise
#   every refactor breaks tests that were not wrong.
#
#   def test_discount_applies_to_orders_over_100():
#       cart = Cart(items=[Item("book", 120)])          # Arrange
#       total = cart.total(discount_code="SAVE10")      # Act
#       assert total == 108                             # Assert

print("\n# 16. AAA Pattern (see comments in the source)")

# 17. Test Doubles - Stub, Fake, Mock, Spy (and Dummy)
# ------------------------------------
# - Dummy : passed to satisfy a parameter; never actually used.
# - Stub  : returns canned answers ("always say the price is 5").
# - Fake  : a REAL but simplified working implementation (in-memory database).
# - Spy   : a real/stub object that RECORDS how it was called, you assert after.
# - Mock  : pre-programmed with expectations; verifies the interaction
#   itself (unittest.mock.Mock blurs spy and mock - it records calls and lets
#   you assert on them).
# - Preference order for maintainable tests: real object > fake > stub > mock.
#   Over-mocking ties tests to how code works instead of what it does.


class PriceStub:                       # Stub - canned answer
    def price(self, item):
        return 5


class InMemoryRepo:                    # Fake - works like a repo, lives in RAM
    def __init__(self):
        self._rows = {}

    def save(self, key, value):
        self._rows[key] = value

    def load(self, key):
        return self._rows[key]


class MailSpy:                         # Spy - records, we assert afterwards
    def __init__(self):
        self.sent = []

    def send(self, to, body):
        self.sent.append((to, body))


def checkout(items, pricer, mailer, user):
    total = sum(pricer.price(i) for i in items)
    mailer.send(user, f"order total {total}")
    return total


print("\n# 17. Test Doubles")
spy = MailSpy()
total = checkout(["a", "b"], PriceStub(), spy, "asha@example.com")
print("stub gave total      :", total)
print("spy recorded         :", spy.sent)
repo = InMemoryRepo()
repo.save("k", 1)
print("fake repo round trip :", repo.load("k"))
mock_mailer = mock.Mock()
checkout(["a"], PriceStub(), mock_mailer, "ravi@example.com")
mock_mailer.send.assert_called_once_with("ravi@example.com", "order total 5")
print("mock verified        : send() called once with expected args")
dummy = None  # a Dummy: checkout never touches it, so None is enough
print("dummy                :", dummy, "(only fills a parameter slot)")

# 18. What Makes Tests Flaky (and a live example)
# ------------------------------------
# - A flaky test passes and fails with no code change. Causes:
#     1. ORDER DEPENDENCE - tests share module-level/global state, so a test
#        passes only after another one ran first (shown below).
#     2. Real time / sleeps / timezone / "today" in assertions.
#     3. Randomness without a seed; dict/set ordering assumptions.
#     4. Network, external services, shared databases or files.
#     5. Concurrency: threads, async races, port clashes in parallel runs.
#     6. Leaked state: env vars, cwd, monkeypatches not undone, singletons.
# - Fixes: isolate (tmp_path, monkeypatch), inject clock/seed, mock the
#   network, fresh fixtures per test, wait on a CONDITION (poll with timeout)
#   instead of time.sleep(n). Do not just rerun until green - that hides bugs.
#   (pytest-randomly shuffles order to expose order dependence early;
#   pytest-xdist exposes shared-resource problems.)

print("\n# 18. Flaky Tests: order dependence")
proj = make_project("flaky_proj", {
    "test_flaky.py": '''
        CACHE = []                                   # shared global state

        def test_a_fills_cache():
            CACHE.append("filled")
            assert CACHE == ["filled"]

        def test_b_silently_depends_on_a():
            assert CACHE == ["filled"]               # only true if A ran first
    ''',
})
print("  whole file (A then B):")
pytest_run(proj, "-q", "--tb=no")
print("  just test B alone (e.g. selected with -k, or reordered/parallelised):")
pytest_run(proj, "-q", "--tb=line", "-k", "test_b")
print("  # Same code, different result: that is flakiness. Make tests independent.")

# 19. Coverage (commands only - `coverage` is not installed here)
# ------------------------------------
# - Coverage measures which lines (and with --branch, which if/else arms) your
#   tests EXECUTED. It finds untested code; it does NOT prove tests are good
#   (a test with no asserts still gives coverage). Aim for meaningful tests,
#   treat the percentage as a smoke alarm, not a goal.

print("\n# 19. Coverage commands")
for cmd in [
    "pip install pytest-cov",
    "pytest --cov=mypkg --cov-report=term-missing   # which lines are missing",
    "pytest --cov=mypkg --cov-branch --cov-fail-under=80",
    "pytest --cov=mypkg --cov-report=html           # open htmlcov/index.html",
    "# without the plugin:  coverage run -m pytest && coverage report -m",
]:
    print("  $", cmd)

# 20. Plugin Ecosystem (reference)
# ------------------------------------
print("\n# 20. Plugins (reference)")
for name, what in [
    ("pytest-cov", "coverage reports, --cov-fail-under gates in CI"),
    ("pytest-xdist", "run in parallel: pytest -n auto (needs independent tests)"),
    ("hypothesis", "property-based testing: generates inputs, shrinks failures"),
    ("pytest-mock", "the `mocker` fixture (wrapper over unittest.mock)"),
    ("pytest-randomly", "shuffle test order + reseed random to expose coupling"),
    ("pytest-asyncio", "async def tests; or anyio's pytest plugin"),
    ("pytest-timeout", "fail a test that hangs: --timeout=10"),
    ("pytest-django / pytest-flask", "framework fixtures (client, db)"),
    ("freezegun / time-machine", "freeze time without changing code"),
]:
    print(f"  {name:<28} {what}")

# 21. Running pytest Programmatically
# ------------------------------------
# - pytest.main([...args]) runs pytest inside the current process and returns
#   an exit code. It imports test modules into YOUR process and changes
#   logging/warnings/sys.path/modules state - so run it in a subprocess (as
#   done here) unless you really need in-process access.
# - Pass plugins=[obj] to receive hooks such as pytest_runtest_logreport and
#   collect your own results.
# - pytest.ExitCode is an IntEnum: OK, TESTS_FAILED, INTERRUPTED,
#   INTERNAL_ERROR, USAGE_ERROR, NO_TESTS_COLLECTED.

print("\n# 21. pytest.main() In A Subprocess")
proj = BASE / "calc_proj"  # the project from section 03
driver = '''
import sys, pytest

class Collector:
    def __init__(self):
        self.outcomes = {}
    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.outcomes[report.nodeid] = report.outcome

c = Collector()
rc = pytest.main(["-q", "-p", "no:cacheprovider", "test_calc.py"], plugins=[c])
print("exit code:", int(rc), pytest.ExitCode(rc).name)
for nodeid, outcome in sorted(c.outcomes.items()):
    print(" ", nodeid, "->", outcome)
'''
r = subprocess.run([sys.executable, "-c", driver], capture_output=True, text=True,
                   cwd=proj, env=ENV, timeout=60)
for ln in scrub(r.stdout, proj).splitlines():
    print("  |", ln)

# 22. A Practical Workflow And Recap
# ------------------------------------
# - Daily loop:  pytest -x -q  (fast fail)  ->  --lf  ->  -k name  ->  full run.
# - When a test fails: read the `E` lines, add `-vv` for full diff, `-s` to see
#   prints, `--pdb` to drop into the debugger at the failure (see
#   02-Debugging-With-Pdb.py), `--tb=long` for full context.
# - Keep unit tests fast (milliseconds); mark slow/integration tests and
#   select with -m "not slow" locally, run everything in CI.
# - Put config in pyproject.toml / pytest.ini: testpaths = ["tests"],
#   addopts = "-ra --strict-markers", markers = [...]. Commit it.
# - Existing unittest.TestCase tests run under pytest unchanged - migrate
#   gradually, new tests as plain functions.

print("\n# 22. Recap")
print("plain assert + fixtures + parametrize + marks + monkeypatch = pytest")

_TMP.cleanup()
