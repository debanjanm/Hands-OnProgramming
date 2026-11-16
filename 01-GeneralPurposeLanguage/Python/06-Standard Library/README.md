# 06 - Standard Library

| File | Covers |
|---|---|
| [01-Collections-Module](01-Collections-Module.ipynb) | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict`, `ChainMap` |
| [02-Datetime-Module](02-Datetime-Module.ipynb) | `date`/`time`/`datetime`/`timedelta`, `strftime`/`strptime`, timezones with `zoneinfo` |
| [03-Os-And-Sys](03-Os-And-Sys.ipynb) | `os.path`, environment variables, `subprocess.run`, `sys.argv`/`sys.path`, `platform` |
| [04-Json-And-Csv](04-Json-And-Csv.ipynb) | `json.dumps`/`loads`, custom encoders, `csv.reader`/`DictWriter`, dialects, `csv.Sniffer` |
| [05-Pathlib-Module](05-Pathlib-Module.ipynb) | `Path` object, joining, globbing, `stat()`, `with_suffix`/`with_name` |
| [06-Typing-And-Type-Hints](06-Typing-And-Type-Hints.ipynb) | `List`/`Dict`/`Optional`/`Union`, `TypeVar`, `Protocol`, `TypedDict`, `Literal`, `Final`, `@overload` |
| [07-Logging](07-Logging.ipynb) | Log levels, `basicConfig`, named loggers, handlers, formatters, log rotation |
| [08-Enum](08-Enum.ipynb) | `Enum`, `auto()`, `IntEnum`, `Flag`/`IntFlag`, `@unique`, `StrEnum` |
| [09-Unittest-Basics](09-Unittest-Basics.ipynb) | `unittest.TestCase`, assertions, `setUp`/`tearDown`, `unittest.mock` |
| [10-Argparse](10-Argparse.ipynb) | `ArgumentParser`, positional/optional args, flags, subcommands, mutually exclusive groups |
| [11-Math-And-Numeric-Modules](11-Math-And-Numeric-Modules.ipynb) | `math`, `cmath`, `decimal`, `fractions`, `statistics`, `numbers`, float vs Decimal vs Fraction |
| [12-Random-And-Secrets](12-Random-And-Secrets.ipynb) | `random` seeding/sampling/distributions, `secrets`, which one is safe for security |
| [13-Time-Module](13-Time-Module.ipynb) | `time` clocks (`monotonic` vs `perf_counter`), `struct_time`, stopwatch, backoff, rate limiting, `timeit` |
| [14-Heapq-Bisect-Array-Queue](14-Heapq-Bisect-Array-Queue.ipynb) | `heapq` priority queues, `bisect`, `array`, thread-safe `queue`, which structure for which job |
| [15-Hashing-And-Encoding](15-Hashing-And-Encoding.ipynb) | `hashlib`, password hashing, `hmac`, `base64`, `uuid`, hashing vs encoding vs encryption |
| [16-Serialization-And-Config](16-Serialization-And-Config.ipynb) | `pickle` (and its security risk), `shelve`, `configparser`, `tomllib`, layered config |
| [17-Sqlite3](17-Sqlite3.ipynb) | `sqlite3`: parameters vs SQL injection, transactions, row factories, adapters, custom functions |
| [18-Text-Utilities](18-Text-Utilities.ipynb) | `textwrap`, `string.Template`, `difflib`, `pprint`, `unicodedata` normalization, `shlex`, `html` |
| [19-File-Utils-And-Archives](19-File-Utils-And-Archives.ipynb) | `shutil`, `tempfile`, `glob`, `scandir`, atomic writes, `filecmp`, `zipfile`/`tarfile` safety, compression |
| [20-Subprocess-And-Signals](20-Subprocess-And-Signals.ipynb) | `subprocess` in depth, pipes and deadlocks, shell injection, `signal`, `atexit`, exit codes |
| [21-Inspect-AST-And-Dis](21-Inspect-AST-And-Dis.ipynb) | `inspect`, `types`, function internals, `dis` bytecode, `ast` parse/visit/unparse, `literal_eval` |
| [22-Networking-Basics](22-Networking-Basics.ipynb) | Localhost-only `socket` TCP/UDP, message framing, `http.server`, `urllib`, `http.client`, URL parsing |
| [23-Ctypes-And-Memory-Mapped-Files](23-Ctypes-And-Memory-Mapped-Files.ipynb) | `ctypes` (calling C libraries, structures, callbacks), `mmap`, `struct`, safety gotchas |
| [24-Graphlib-Codecs-And-Misc-Modules](24-Graphlib-Codecs-And-Misc-Modules.ipynb) | `graphlib.TopologicalSorter`, `codecs`, `mimetypes`, `colorsys`, `shlex`, `fileinput`, `importlib.resources`, `tokenize`, `platform`/`sysconfig`, GUI modules explained |
| [25-Modern-Python-Features-3.10-To-3.13](25-Modern-Python-Features-3.10-To-3.13.ipynb) | `match`, `except*`, PEP 695 generics and `type`, `override`/`TypeGuard`/`TypeIs`, f-string 3.12, `itertools.batched`, free-threading and JIT, removals |
