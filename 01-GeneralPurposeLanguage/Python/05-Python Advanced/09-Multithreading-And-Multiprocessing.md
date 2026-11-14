# Multithreading and Multiprocessing — Notes

## What this covers
Running work concurrently in Python: threads (good for I/O-bound work) vs processes (good for CPU-bound work), synchronization, and safe communication between them.

## Key points
- **Threading**: multiple threads share the same process/memory — good for I/O-bound tasks (network, file, DB) since a thread waiting on I/O lets others run.
- **Multiprocessing**: separate processes, each with its own memory — good for CPU-bound tasks since it bypasses the GIL for true parallelism.
- **The GIL**: only one thread executes Python bytecode at a time in CPython, so threads don't give real CPU parallelism for pure Python code — but the GIL is released during I/O, so threading still helps for I/O-bound work.
- `threading.Thread(target=fn, args=...)`, then `.start()` and `.join()` (wait for it to finish).
- `threading.Lock()` prevents race conditions when multiple threads modify shared state — use it via `with lock:`.
- `ThreadPoolExecutor`/`ProcessPoolExecutor` (from `concurrent.futures`) are managed pools — `.map(func, iterable)` is the easy path, used as a context manager.
- `queue.Queue` is thread-safe out of the box (unlike a plain list) — the standard way for threads to hand off work (producer/consumer pattern, with `None` as a common "stop" sentinel).
- `multiprocessing.Queue` and `multiprocessing.Pipe` are the process equivalents — since processes don't share memory, data crossing the boundary is pickled.
- `os.cpu_count()` is the standard way to size a CPU-bound pool's `max_workers` — more workers than cores rarely helps.

## Gotchas (the part worth revising twice)
- **Deadlock**: happens when two threads each hold a lock the other needs, so both wait forever — classic cause is acquiring two locks in inconsistent order across threads. Fix: always acquire locks in the same order everywhere.
- **Picklability**: arguments/results sent to a separate process must be pickled to cross the process boundary. Lambdas and closures can't be pickled — a common source of confusing multiprocessing errors.
- On macOS/Windows (default "spawn" start method), multiprocessing **re-imports the whole file** in each child process. Any function used as a `Process` target must be defined at **module level**, not nested inside `if __name__ == "__main__":` or another function, or the child process won't be able to find it.
- That's also why multiprocessing code needs the `if __name__ == "__main__":` guard at all — without it, the re-import would recursively spawn more processes.

## When it matters
Use threading (or asyncio) for I/O-bound work — network calls, file access, waiting on external services. Use multiprocessing for CPU-bound work — heavy computation that needs to actually use multiple cores.

## One-line recap example
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(lambda n: n * n, [1, 2, 3, 4]))  # [1, 4, 9, 16]
```
