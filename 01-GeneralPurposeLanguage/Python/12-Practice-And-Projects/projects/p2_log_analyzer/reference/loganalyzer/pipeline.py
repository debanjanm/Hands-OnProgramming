"""Small generator stages that you chain together: read -> parse -> filter."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Iterator

from .parser import LogRecord


def read_lines(path: str) -> Iterator[str]:
    """Yield the lines of a file one at a time (the file is closed at the end).

    Milestone 2: pipeline.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        yield from fh


def filter_status(records: Iterable[LogRecord], spec: str) -> Iterator[LogRecord]:
    """Keep records whose status matches ``spec``: ``"404"`` or a class like ``"5xx"``.

    Milestone 4: filters. Raise ``ValueError`` for anything else (checked
    when the generator is first advanced is fine, but checking up front is nicer).
    """
    spec = spec.strip().lower()
    if len(spec) == 3 and spec.isdigit():
        return (r for r in records if r.status == int(spec))
    if len(spec) == 3 and spec[0] in "12345" and spec[1:] == "xx":
        low = int(spec[0]) * 100
        return (r for r in records if low <= r.status < low + 100)
    raise ValueError(f"invalid status filter {spec!r}: use e.g. 404 or 5xx")


def parse_since(text: str) -> datetime:
    """Parse ``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM[:SS]``; no zone means UTC.

    Milestone 4: filters. Raise ``ValueError`` on bad input.
    """
    try:
        when = datetime.fromisoformat(text.strip())
    except ValueError:
        raise ValueError(f"invalid --since value {text!r}: use YYYY-MM-DD or YYYY-MM-DDTHH:MM") from None
    return when if when.tzinfo else when.replace(tzinfo=timezone.utc)


def filter_since(records: Iterable[LogRecord], since: datetime) -> Iterator[LogRecord]:
    """Keep records at or after ``since``.

    Milestone 4: filters.
    """
    return (r for r in records if r.time >= since)
