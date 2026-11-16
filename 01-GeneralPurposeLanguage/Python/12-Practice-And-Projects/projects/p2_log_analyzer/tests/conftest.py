"""Puts starter/ (your work) or reference/ (--solutions) on sys.path, and builds sample logs."""
import pathlib
import random
import sys
from datetime import datetime, timedelta, timezone

import pytest

PROJECT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = "loganalyzer"


@pytest.fixture(scope="session", autouse=True)
def _project_on_path(request):
    folder = "reference" if request.config.getoption("--solutions") else "starter"
    path = str(PROJECT / folder)
    sys.path.insert(0, path)
    yield
    sys.path.remove(path)
    for name in [n for n in sys.modules if n == PACKAGE or n.startswith(PACKAGE + ".")]:
        del sys.modules[name]


def _mod(name):
    import importlib
    return importlib.import_module(f"{PACKAGE}.{name}")


@pytest.fixture
def parser_mod():
    return _mod("parser")


@pytest.fixture
def pipeline():
    return _mod("pipeline")


@pytest.fixture
def stats_mod():
    return _mod("stats")


@pytest.fixture
def anomalies():
    return _mod("anomalies")


@pytest.fixture
def report():
    return _mod("report")


@pytest.fixture
def cli():
    return _mod("cli")


# A tiny hand-made log with answers we can check by hand.
SMALL_LINES = [
    '10.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 12ms',
    '10.0.0.1 - bob [10/Oct/2023:13:56:00 +0000] "GET /api/items?id=3 HTTP/1.1" 200 512 40ms',
    '10.0.0.2 - - [10/Oct/2023:14:01:00 +0000] "POST /api/items HTTP/1.1" 201 - 80ms',
    '10.0.0.3 - - [10/Oct/2023:14:02:00 +0000] "GET /missing HTTP/1.1" 404 150 5ms',
    '10.0.0.2 - - [10/Oct/2023:14:03:00 +0000] "GET /api/items HTTP/1.1" 500 0 200ms',
    "this is not a log line",
    '10.0.0.1 - - [10/Oct/2023:15:00:00 +0000] "GET /index.html HTTP/1.1" 200 2326',
]


@pytest.fixture
def small_lines():
    return list(SMALL_LINES)


@pytest.fixture
def small_log(tmp_path):
    path = tmp_path / "small.log"
    path.write_text("\n".join(SMALL_LINES) + "\n")
    return str(path)


@pytest.fixture
def make_log(tmp_path):
    """make_log(n=300, seed=1, hours=6, spike_hour=None, malformed=0) -> path of a synthetic log.

    Same arguments always give the same file. ``spike_hour`` adds 10x extra
    traffic in that hour (0-based). All times are 2023-10-10 UTC.
    """
    counter = [0]

    def _make(n=300, seed=1, hours=6, spike_hour=None, malformed=0):
        rng = random.Random(seed)
        start = datetime(2023, 10, 10, tzinfo=timezone.utc)
        ips = [f"192.168.0.{i}" for i in range(1, 11)]
        paths = ["/", "/login", "/api/items", "/api/items?page=2", "/static/app.js", "/about"]
        statuses = [200] * 80 + [301] * 5 + [404] * 10 + [500] * 5
        stamps = [start + timedelta(seconds=rng.randrange(hours * 3600)) for _ in range(n)]
        if spike_hour is not None:
            stamps += [start + timedelta(hours=spike_hour, seconds=rng.randrange(3600)) for _ in range(n * 2)]
        lines = []
        for ts in sorted(stamps):
            lines.append(
                f'{rng.choice(ips[:3] * 3 + ips)} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
                f'"{rng.choice(["GET", "GET", "POST"])} {rng.choice(paths)} HTTP/1.1" '
                f"{rng.choice(statuses)} {rng.randrange(100, 5000)} {rng.randrange(1, 300)}ms"
            )
        for i in range(malformed):
            lines.insert(rng.randrange(len(lines)), f"### broken line {i}")
        counter[0] += 1
        path = tmp_path / f"gen{counter[0]}.log"
        path.write_text("\n".join(lines) + "\n")
        return str(path)

    return _make
