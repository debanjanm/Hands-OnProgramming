"""Small generator stages that you chain together: read -> parse -> filter."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Iterator

from .parser import LogRecord


def read_lines(path: str) -> Iterator[str]:
    """Yield the lines of a file one at a time (the file is closed at the end).

    Milestone 2: pipeline.
    """
    # TODO (Milestone 2: pipeline): implement this, then run the tests.
    raise NotImplementedError


def filter_status(records: Iterable[LogRecord], spec: str) -> Iterator[LogRecord]:
    """Keep records whose status matches ``spec``: ``"404"`` or a class like ``"5xx"``.

    Milestone 4: filters. Raise ``ValueError`` for anything else (checked
    when the generator is first advanced is fine, but checking up front is nicer).
    """
    # TODO (Milestone 4: filters. Raise ``ValueError`` for anything else (checked): implement this, then run the tests.
    raise NotImplementedError


def parse_since(text: str) -> datetime:
    """Parse ``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM[:SS]``; no zone means UTC.

    Milestone 4: filters. Raise ``ValueError`` on bad input.
    """
    # TODO (Milestone 4: filters. Raise ``ValueError`` on bad input): implement this, then run the tests.
    raise NotImplementedError


def filter_since(records: Iterable[LogRecord], since: datetime) -> Iterator[LogRecord]:
    """Keep records at or after ``since``.

    Milestone 4: filters.
    """
    # TODO (Milestone 4: filters): implement this, then run the tests.
    raise NotImplementedError
