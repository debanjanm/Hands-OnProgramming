# Project 2: Log Analyzer (`loganalyzer`)

Read a web-server access log and tell the story: how many requests, which pages, which IPs, how slow, and when traffic spiked. The log may be huge, so you process it as a stream, one line at a time.

## What you will practise

Regular expressions, dataclasses, generators and lazy pipelines, `collections.Counter`, percentiles, `argparse`, `datetime` with time zones, and testing with generated data.

## Log format

Common Log Format, plus an optional latency at the end:

```
127.0.0.1 - bob [10/Oct/2023:13:55:36 +0000] "GET /a?x=1 HTTP/1.1" 200 2326 45ms
```

fields: ip, ident, user, `[time]`, `"METHOD path protocol"`, status, size (`-` means 0), optional `NNms`. Lines that do not match are *malformed*: count them, but never crash.

## Milestones

- [ ] **1. Parsing** (`parser.py`): `LogRecord` helpers and `parse_line` (raise `ValueError` if bad).
- [ ] **2. Pipeline** (`parser.parse_lines`, `pipeline.read_lines`): generators that never hold the whole file in memory.
- [ ] **3. Stats** (`stats.py`): `percentile`, `compute_stats` (per status / endpoint / hour, top IPs, error rate = share of 5xx, p50/p95).
- [ ] **4. Filters** (`pipeline.py`): `filter_status` (`404` or `5xx`), `parse_since`, `filter_since`.
- [ ] **5. Reports** (`report.py`, `Stats.to_dict`): text and JSON.
- [ ] **6. Anomalies** (`anomalies.py`): an hour is a spike when its count is above `factor` times the median hourly count.
- [ ] **7. CLI** (`cli.py`): wire it all together.

## Spec

```
loganalyzer LOGFILE [--status 404|5xx] [--since 2023-10-10[THH:MM[:SS]]] [--top N] [--spike-factor F] [--json]
```

Exit code 0 on success, 2 for a missing file, a bad filter value or bad usage (message `error: ...` on stderr). Times without a zone are UTC. Latency percentiles use the nearest-rank method and ignore lines with no latency.

Public API the tests use: `loganalyzer.parser.parse_line / parse_lines / LogRecord`, `loganalyzer.pipeline.*`, `loganalyzer.stats.compute_stats / percentile / Stats`, `loganalyzer.anomalies.detect_spikes / Spike`, `loganalyzer.report.text_report / json_report`, `loganalyzer.cli.main(argv) -> int`.

## Hints

- Named groups make the regex readable: `(?P<ip>\S+)`. The `LINE_RE` and `TIME_FORMAT` constants are already given.
- `datetime.strptime(text, "%d/%b/%Y:%H:%M:%S %z")` gives a timezone-aware time.
- A generator function uses `yield`; a generator expression is `(x for x in xs if ...)`.
- `Counter.most_common(n)` gives the top N.
- Nearest rank: sort, then take index `ceil(p/100 * n) - 1`.
- The tests build a synthetic log with a seeded random generator (see `tests/conftest.py`), so results are the same every run.

## Run and test

From `12-Practice-And-Projects/`:

```
python3 -m pytest projects/p2_log_analyzer -q              # your starter code
python3 -m pytest --solutions projects/p2_log_analyzer -q  # the reference solution
cd projects/p2_log_analyzer/reference && python3 -m loganalyzer path/to/access.log --status 5xx
```

At first tests fail with `NotImplementedError`. That is expected.

## Stretch goals

- `--group-by minute`.
- A z-score or moving-average spike detector.
- Parse the "combined" format (referer and user agent).
- Read from stdin when LOGFILE is `-`.
- Top N slowest endpoints by p95.
