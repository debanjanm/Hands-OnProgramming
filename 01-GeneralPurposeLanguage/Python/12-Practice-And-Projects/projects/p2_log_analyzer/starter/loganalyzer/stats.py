"""Statistics computed in a single pass over the records."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from .parser import LogRecord


def percentile(values: list[float], pct: float) -> float | None:
    """Nearest-rank percentile (``pct`` from 0 to 100). ``None`` for an empty list.

    Milestone 3: stats. Sort, then take the value at rank ``ceil(pct/100 * n)``
    (at least rank 1). Example: p50 of [5, 12, 40, 80, 200] is 40.
    """
    # TODO (Milestone 3: stats. Sort, then take the value at rank ``ceil(pct/100 * n)``): implement this, then run the tests.
    raise NotImplementedError


@dataclass
class Stats:
    """Everything the report needs."""

    total: int = 0
    by_status: Counter = field(default_factory=Counter)
    by_endpoint: Counter = field(default_factory=Counter)
    by_hour: Counter = field(default_factory=Counter)
    by_ip: Counter = field(default_factory=Counter)
    errors: int = 0  # responses with status >= 500
    latencies: list[float] = field(default_factory=list)
    top_n: int = 5

    @property
    def error_rate(self) -> float:
        """errors / total, or 0.0 when there are no requests.

        Milestone 3: stats.
        """
        # TODO (Milestone 3: stats): implement this, then run the tests.
        raise NotImplementedError

    @property
    def p50(self) -> float | None:
        """Median latency in ms (None when no latencies).

        Milestone 3: stats.
        """
        # TODO (Milestone 3: stats): implement this, then run the tests.
        raise NotImplementedError

    @property
    def p95(self) -> float | None:
        """95th percentile latency in ms (None when no latencies).

        Milestone 3: stats.
        """
        # TODO (Milestone 3: stats): implement this, then run the tests.
        raise NotImplementedError

    @property
    def top_ips(self) -> list[tuple[str, int]]:
        """The ``top_n`` busiest IPs as ``(ip, count)``, busiest first.

        Milestone 3: stats. ``Counter.most_common`` does the work.
        """
        # TODO (Milestone 3: stats. ``Counter.most_common`` does the work): implement this, then run the tests.
        raise NotImplementedError

    def to_dict(self) -> dict:
        """JSON-friendly summary. Milestone 5: report."""
        # TODO : implement this, then run the tests.
        raise NotImplementedError


def compute_stats(records: Iterable[LogRecord], top_n: int = 5) -> Stats:
    """Consume ``records`` once and fill in a Stats.

    Milestone 3: stats. Do not keep the records themselves, only the counters
    and the latency numbers.
    """
    # TODO (Milestone 3: stats. Do not keep the records themselves, only the counters): implement this, then run the tests.
    raise NotImplementedError
