"""Puts starter/ (default) or reference/ (--solutions) on sys.path so tests can `import inventory_api`."""
import pathlib
import sys

import pytest

PACKAGE = "inventory_api"


@pytest.fixture(scope="session", autouse=True)
def _project_on_path(request):
    sub = "reference" if request.config.getoption("--solutions") else "starter"
    path = str(pathlib.Path(__file__).resolve().parent.parent / sub)
    sys.path.insert(0, path)
    yield
    sys.path.remove(path)
    for name in [m for m in sys.modules if m == PACKAGE or m.startswith(PACKAGE + ".")]:
        del sys.modules[name]
