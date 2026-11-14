# 06 - Standard Library

| File | Covers |
|---|---|
| [01-Collections-Module.py](01-Collections-Module.py) · [notes](01-Collections-Module.md) | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict`, `ChainMap` |
| [02-Datetime-Module.py](02-Datetime-Module.py) · [notes](02-Datetime-Module.md) | `date`/`time`/`datetime`/`timedelta`, `strftime`/`strptime`, timezones with `zoneinfo` |
| [03-Os-And-Sys.py](03-Os-And-Sys.py) · [notes](03-Os-And-Sys.md) | `os.path`, environment variables, `subprocess.run`, `sys.argv`/`sys.path`, `platform` |
| [04-Json-And-Csv.py](04-Json-And-Csv.py) · [notes](04-Json-And-Csv.md) | `json.dumps`/`loads`, custom encoders, `csv.reader`/`DictWriter`, dialects, `csv.Sniffer` |
| [05-Pathlib-Module.py](05-Pathlib-Module.py) · [notes](05-Pathlib-Module.md) | `Path` object, joining, globbing, `stat()`, `with_suffix`/`with_name` |
| [06-Typing-And-Type-Hints.py](06-Typing-And-Type-Hints.py) · [notes](06-Typing-And-Type-Hints.md) | `List`/`Dict`/`Optional`/`Union`, `TypeVar`, `Protocol`, `TypedDict`, `Literal`, `Final`, `@overload` |
| [07-Logging.py](07-Logging.py) · [notes](07-Logging.md) | Log levels, `basicConfig`, named loggers, handlers, formatters, log rotation |
| [08-Enum.py](08-Enum.py) · [notes](08-Enum.md) | `Enum`, `auto()`, `IntEnum`, `Flag`/`IntFlag`, `@unique`, `StrEnum` |
| [09-Unittest-Basics.py](09-Unittest-Basics.py) · [notes](09-Unittest-Basics.md) | `unittest.TestCase`, assertions, `setUp`/`tearDown`, `unittest.mock` |
| [10-Argparse.py](10-Argparse.py) · [notes](10-Argparse.md) | `ArgumentParser`, positional/optional args, flags, subcommands, mutually exclusive groups |
| [11-Math-And-Numeric-Modules.py](11-Math-And-Numeric-Modules.py) · [notes](11-Math-And-Numeric-Modules.md) | `math`, `cmath`, `decimal`, `fractions`, `statistics`, `numbers`, float vs Decimal vs Fraction |
| [12-Random-And-Secrets.py](12-Random-And-Secrets.py) · [notes](12-Random-And-Secrets.md) | `random` seeding/sampling/distributions, `secrets`, which one is safe for security |
| [13-Time-Module.py](13-Time-Module.py) · [notes](13-Time-Module.md) | `time` clocks (`monotonic` vs `perf_counter`), `struct_time`, stopwatch, backoff, rate limiting, `timeit` |
| [14-Heapq-Bisect-Array-Queue.py](14-Heapq-Bisect-Array-Queue.py) · [notes](14-Heapq-Bisect-Array-Queue.md) | `heapq` priority queues, `bisect`, `array`, thread-safe `queue`, which structure for which job |
| [15-Hashing-And-Encoding.py](15-Hashing-And-Encoding.py) · [notes](15-Hashing-And-Encoding.md) | `hashlib`, password hashing, `hmac`, `base64`, `uuid`, hashing vs encoding vs encryption |
| [16-Serialization-And-Config.py](16-Serialization-And-Config.py) · [notes](16-Serialization-And-Config.md) | `pickle` (and its security risk), `shelve`, `configparser`, `tomllib`, layered config |
| [17-Sqlite3.py](17-Sqlite3.py) · [notes](17-Sqlite3.md) | `sqlite3`: parameters vs SQL injection, transactions, row factories, adapters, custom functions |
| [18-Text-Utilities.py](18-Text-Utilities.py) · [notes](18-Text-Utilities.md) | `textwrap`, `string.Template`, `difflib`, `pprint`, `unicodedata` normalization, `shlex`, `html` |
| [19-File-Utils-And-Archives.py](19-File-Utils-And-Archives.py) · [notes](19-File-Utils-And-Archives.md) | `shutil`, `tempfile`, `glob`, `scandir`, atomic writes, `filecmp`, `zipfile`/`tarfile` safety, compression |
| [20-Subprocess-And-Signals.py](20-Subprocess-And-Signals.py) · [notes](20-Subprocess-And-Signals.md) | `subprocess` in depth, pipes and deadlocks, shell injection, `signal`, `atexit`, exit codes |
| [21-Inspect-AST-And-Dis.py](21-Inspect-AST-And-Dis.py) · [notes](21-Inspect-AST-And-Dis.md) | `inspect`, `types`, function internals, `dis` bytecode, `ast` parse/visit/unparse, `literal_eval` |
| [22-Networking-Basics.py](22-Networking-Basics.py) · [notes](22-Networking-Basics.md) | Localhost-only `socket` TCP/UDP, message framing, `http.server`, `urllib`, `http.client`, URL parsing |
