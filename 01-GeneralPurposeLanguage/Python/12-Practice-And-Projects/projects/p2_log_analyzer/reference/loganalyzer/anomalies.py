"""Very simple spike detection."""
from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Spike:
    """An hour with unusually many requests."""

    hour: str
    count: int
    baseline: float  # the median hourly count


def detect_spikes(by_hour: dict[str, int], factor: float = 2.0, min_buckets: int = 3) -> list[Spike]:
    """Hours whose count is more than ``factor`` times the median hourly count.

    Milestone 6: anomalies. With fewer than ``min_buckets`` hours there is no
    meaningful baseline, so return ``[]``. Results are sorted by hour.
    """
    if len(by_hour) < min_buckets:
        return []
    baseline = statistics.median(by_hour.values())
    return [Spike(h, c, baseline) for h, c in sorted(by_hour.items()) if c > factor * baseline]
