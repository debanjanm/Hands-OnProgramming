"""Puts starter/ (your work) or reference/ (--solutions) on sys.path for these tests."""
import pathlib
import sys

import pytest

PROJECT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = "taskman"


@pytest.fixture(scope="session", autouse=True)
def _project_on_path(request):
    folder = "reference" if request.config.getoption("--solutions") else "starter"
    path = str(PROJECT / folder)
    sys.path.insert(0, path)
    yield
    sys.path.remove(path)
    for name in [n for n in sys.modules if n == PACKAGE or n.startswith(PACKAGE + ".")]:
        del sys.modules[name]


@pytest.fixture
def dates():
    import taskman.dates as m
    return m


@pytest.fixture
def store_mod():
    import taskman.store as m
    return m


@pytest.fixture
def export_mod():
    import taskman.export as m
    return m


@pytest.fixture
def cli():
    import taskman.cli as m
    return m


@pytest.fixture
def store(tmp_path, store_mod):
    with store_mod.TaskStore(str(tmp_path / "t.db")) as s:
        yield s


@pytest.fixture
def run(cli, tmp_path, capsys):
    """run("add", "x") -> (exit_code, stdout, stderr), using a temp DB and a frozen date."""
    from datetime import date
    db = str(tmp_path / "cli.db")

    def _run(*argv, today=date(2025, 6, 15)):
        code = cli.main(["--db", db, *argv], today=today)
        out = capsys.readouterr()
        return code, out.out, out.err

    return _run
