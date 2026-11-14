# 05 - Python Advanced

| File | Covers |
|---|---|
| [01-Iterators.py](01-Iterators.py) · [notes](01-Iterators.md) | Iterator protocol (`__iter__`/`__next__`), `StopIteration`, custom iterators, `itertools.tee` |
| [02-Generators.py](02-Generators.py) · [notes](02-Generators.md) | `yield`, generator expressions, `send`/`throw`/`close`, `yield from`, lazy pipelines |
| [03-Error-And-Exception-Handling.py](03-Error-And-Exception-Handling.py) · [notes](03-Error-And-Exception-Handling.md) | try/except/else/finally, custom exceptions, exception chaining, `except*` (3.11+), `contextlib.suppress` |
| [04-File-Handling.py](04-File-Handling.py) · [notes](04-File-Handling.md) | Open modes, read/write, `with`, encoding, buffering, `tempfile`, `shutil` |
| [05-Modules-And-Packages.py](05-Modules-And-Packages.py) · [notes](05-Modules-And-Packages.md) | Import forms, `__name__ == "__main__"`, packages, `__all__`, `importlib`, `sys.modules` caching |
| [06-Context-Managers.py](06-Context-Managers.py) · [notes](06-Context-Managers.md) | `with` statement, custom context managers, `contextlib.contextmanager`, `ExitStack` |
| [07-Regular-Expressions.py](07-Regular-Expressions.py) · [notes](07-Regular-Expressions.md) | `re` module, groups, lookahead/lookbehind, backreferences, `re.VERBOSE` |
| [08-Itertools-And-Functools.py](08-Itertools-And-Functools.py) · [notes](08-Itertools-And-Functools.md) | `itertools`/`functools` toolbox — `chain`, `groupby`, `reduce`, `lru_cache`, `partial`, `singledispatch` |
| [09-Multithreading-And-Multiprocessing.py](09-Multithreading-And-Multiprocessing.py) · [notes](09-Multithreading-And-Multiprocessing.md) | `threading`, `multiprocessing`, the GIL, locks, deadlocks, `queue.Queue`, executors |
| [10-Async-Await.py](10-Async-Await.py) · [notes](10-Async-Await.md) | `asyncio`, coroutines, `gather`/`create_task`, async context managers, `asyncio.Lock`, cancellation |
| [11-Threading-Primitives.py](11-Threading-Primitives.py) · [notes](11-Threading-Primitives.md) | Race conditions, `Lock`/`RLock`/`Event`/`Condition`/`Semaphore`/`Barrier`, futures in depth, deadlock detection |
| [12-Multiprocessing-Pool-And-Shared-State.py](12-Multiprocessing-Pool-And-Shared-State.py) · [notes](12-Multiprocessing-Pool-And-Shared-State.md) | Start methods, `Pool`, `Value`/`Array`/`shared_memory`/`Manager`, pickling limits, serial vs pool |
| [13-Asyncio-Advanced.py](13-Asyncio-Advanced.py) · [notes](13-Asyncio-Advanced.md) | `TaskGroup`, `timeout`, `Semaphore`, cancellation, async mistakes, localhost streams, async subprocess, `contextvars` |
| `demo_package/` | Small helper package imported by 05-Modules-And-Packages.py — not a topic file itself |
