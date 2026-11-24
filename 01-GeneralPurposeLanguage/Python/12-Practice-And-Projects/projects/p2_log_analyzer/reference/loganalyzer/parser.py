"""Parse one access-log line into a LogRecord.

Format (Common Log Format plus an optional latency at the end)::

    127.0.0.1 - bob [10/Oct/2023:13:55:36 +0000] "GET /a?x=1 HTTP/1.1" 200 2326 45ms
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Iterable, Iterator

LINE_RE = re.compile(
    r'^(?P<ip>\S+) (?P<ident>\S+) (?P<user>\S+) '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<protocol>[^"\s]+)" '
    r'(?P<status>\d{3}) (?P<size>\d+|-)'
    r'(?: (?P<latency>\d+(?:\.\d+)?)ms)?$'
)
TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass(frozen=True)
class LogRecord:
    """One parsed request."""

    ip: str
    user: str
    time: datetime  # timezone-aware
    method: str
    path: str  # as logged, including any ?query
    protocol: str
    status: int
    size: int  # '-' in the log becomes 0
    latency_ms: float | None = None

    @property
    def endpoint(self) -> str:
        """The path without the query string: ``/a?x=1`` -> ``/a``.

        Milestone 1: parsing.
        """
        return self.path.split("?", 1)[0]

    @property
    def hour(self) -> str:
        """The UTC hour bucket as text, e.g. ``2023-10-10 13:00``.

        Milestone 3: stats.
        """
        return self.time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:00")


def parse_line(line: str) -> LogRecord:
    """Parse one line. Raises ``ValueError`` if it is not valid.

    Milestone 1: parsing. Use LINE_RE and TIME_FORMAT. A bad timestamp
    (e.g. month ``Foo``) is also a ``ValueError``.
    """
    m = LINE_RE.match(line.strip())
    if not m:
        raise ValueError(f"not a log line: {line[:60]!r}")
    return LogRecord(
        ip=m["ip"],
        user=m["user"],
        time=datetime.strptime(m["time"], TIME_FORMAT),
        method=m["method"],
        path=m["path"],
        protocol=m["protocol"],
        status=int(m["status"]),
        size=0 if m["size"] == "-" else int(m["size"]),
        latency_ms=float(m["latency"]) if m["latency"] else None,
    )


def parse_lines(lines: Iterable[str], bad: list[str] | None = None,
                *, on_bad: Callable[[str], None] | None = None) -> Iterator[LogRecord]:
    """Lazily yield a record for every valid line.

    Milestone 2: pipeline. Blank lines are skipped silently. Malformed lines
    are skipped too, and appended to ``bad`` when a list is given.
    ``on_bad`` receives each malformed line; use it for counting without retaining text.
    This must be a generator: never build a list of all the records.
    """
    for line in lines:
        if not line.strip():
            continue
        try:
            yield parse_line(line)
        except ValueError:
            if bad is not None:
                bad.append(line.rstrip("\n"))
            if on_bad is not None:
                on_bad(line.rstrip("\n"))
