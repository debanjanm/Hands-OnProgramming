# 05 - Python Advanced

| File | Covers |
|---|---|
| [01-Iterators](01-Iterators.ipynb) | Iterator protocol (`__iter__`/`__next__`), `StopIteration`, custom iterators, `itertools.tee` |
| [02-Generators](02-Generators.ipynb) | `yield`, generator expressions, `send`/`throw`/`close`, `yield from`, lazy pipelines |
| [03-Error-And-Exception-Handling](03-Error-And-Exception-Handling.ipynb) | try/except/else/finally, custom exceptions, exception chaining, `except*` (3.11+), `contextlib.suppress` |
| [04-File-Handling](04-File-Handling.ipynb) | Open modes, read/write, `with`, encoding, buffering, `tempfile`, `shutil` |
| [05-Modules-And-Packages](05-Modules-And-Packages.ipynb) | Import forms, `__name__ == "__main__"`, packages, `__all__`, `importlib`, `sys.modules` caching |
| [06-Context-Managers](06-Context-Managers.ipynb) | `with` statement, custom context managers, `contextlib.contextmanager`, `ExitStack` |
| [07-Regular-Expressions](07-Regular-Expressions.ipynb) | `re` module, groups, lookahead/lookbehind, backreferences, `re.VERBOSE` |
| [08-Itertools-And-Functools](08-Itertools-And-Functools.ipynb) | `itertools`/`functools` toolbox — `chain`, `groupby`, `reduce`, `lru_cache`, `partial`, `singledispatch` |
| [09-Multithreading-And-Multiprocessing](09-Multithreading-And-Multiprocessing.ipynb) · [script](09-Multithreading-And-Multiprocessing.py) | `threading`, `multiprocessing`, the GIL, locks, deadlocks, `queue.Queue`, executors |
| [10-Async-Await](10-Async-Await.ipynb) | `asyncio`, coroutines, `gather`/`create_task`, async context managers, `asyncio.Lock`, cancellation |
| [11-Threading-Primitives](11-Threading-Primitives.ipynb) | Race conditions, `Lock`/`RLock`/`Event`/`Condition`/`Semaphore`/`Barrier`, futures in depth, deadlock detection |
| [12-Multiprocessing-Pool-And-Shared-State](12-Multiprocessing-Pool-And-Shared-State.ipynb) · [script](12-Multiprocessing-Pool-And-Shared-State.py) | Start methods, `Pool`, `Value`/`Array`/`shared_memory`/`Manager`, pickling limits, serial vs pool |
| [13-Asyncio-Advanced](13-Asyncio-Advanced.ipynb) | `TaskGroup`, `timeout`, `Semaphore`, cancellation, async mistakes, localhost streams, async subprocess, `contextvars` |
| `demo_package/` | Small helper package imported by the 05-Modules-And-Packages notebook — not a topic file itself |
