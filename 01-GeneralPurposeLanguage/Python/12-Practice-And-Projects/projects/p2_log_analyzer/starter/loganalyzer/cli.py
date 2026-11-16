"""Command line: ``python3 -m loganalyzer access.log --status 5xx --json``."""
from __future__ import annotations

import argparse
import sys

from .anomalies import detect_spikes
from .parser import parse_lines
from .pipeline import filter_since, filter_status, parse_since, read_lines
from .report import json_report, text_report
from .stats import compute_stats


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Milestone 7: CLI. Positional ``logfile``; options ``--status``,
    ``--since``, ``--top N`` (default 5), ``--spike-factor F`` (default 2.0),
    ``--json``.
    """
    # TODO (Milestone 7: CLI. Positional ``logfile``; options ``--status``,): implement this, then run the tests.
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Run the analyzer; returns 0 on success, 2 for bad input or a missing file.

    Milestone 7: CLI. Chain: read_lines -> parse_lines -> filters -> compute_stats.
    Errors are printed to stderr as ``error: ...``.
    """
    # TODO (Milestone 7: CLI. Chain: read_lines -> parse_lines -> filters -> compute_stats): implement this, then run the tests.
    raise NotImplementedError
