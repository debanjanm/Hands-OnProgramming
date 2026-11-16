import collections
import functools
import multiprocessing as mp
import operator
import os
import pickle
import queue
import random
import sys
import tempfile
import threading
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from multiprocessing import shared_memory
from multiprocessing.managers import SharedMemoryManager

# 01. Multiprocessing - Why Processes, And The Big Warning About This File
# ------------------------------------
# - 09-Multithreading-And-Multiprocessing.py introduced Process, Pool and
#   Queue. Here we go DEEPER: pools, shared state, start methods, costs.
# - Why processes? Threads share one GIL, so pure-Python CPU work cannot run
#   in parallel (see 11-Threading-Primitives.py, section 18). Each PROCESS has
#   its own interpreter, its own GIL and its own memory, so N processes can
#   really use N cores.
# - The price: (1) starting a process is slow (tens of ms, not microseconds),
#   (2) memory is NOT shared, so everything crossing the boundary is PICKLED
#   (copied), and (3) you need explicit tools (Queue, Value, SharedMemory,
#   Manager) to share anything.
#
# THE RULE THAT SHAPES THIS WHOLE FILE:
# - On macOS and Windows (and Python 3.14+ Linux uses forkserver) children
#   are started with "spawn": a brand-new interpreter that IMPORTS THIS FILE
#   again. Therefore:
#     * every function a child runs must be a MODULE-LEVEL function (that is
#       why all the helpers are defined up here, not inside main());
#     * module level must contain only definitions - side effects (prints,
#       starting processes) go under `if __name__ == "__main__":`, or every
#       child would repeat them (or spawn more children, forever).

# Module-level state, used later to show what a spawned child does (and does
# not) see. This line runs in the parent AND again inside every spawned child.
import_log = [f"module imported as {__name__!r} in pid {os.getpid()}"]
CONFIG = {"mode": "default"}
MEMORY_LIST = []


# ------------------------------------------------------------------
# Module-level helper functions (these are the process "targets")
# ------------------------------------------------------------------
def report_identity(q):
    q.put({
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "module_name": __name__,
        "import_log": list(import_log),
        "config_mode": CONFIG["mode"],
    })


def mutate_memory(q):
    MEMORY_LIST.append("written by child")
    q.put(len(MEMORY_LIST))


def exit_with(code):
    sys.exit(code)


def sleep_long():
    time.sleep(30)


def noop():
    pass


def square(n):
    return n * n


def slow_square(n):
    time.sleep(0.005 * (n % 3))      # uneven task durations
    return n * n


def add(a, b):
    return a + b


def whoami(_):
    return os.getpid()


def sleepy(seconds):
    time.sleep(seconds)
    return "finished sleeping"


def fail_on_three(n):
    if n == 3:
        raise ValueError("three is unlucky")
    return n


def tiny(n):
    return n + 1


def length_of(data):
    return len(data)


def length_of_range(n):
    return n


def bump_with_lock(v, times):
    for _ in range(times):
        with v.get_lock():           # read-modify-write is NOT atomic across processes
            v.value += 1


def bump_without_lock(v, times):
    for _ in range(times):
        v.value += 1


def fill_array(arr, start, count):
    for i in range(start, start + count):
        arr[i] = i * 1.5


def shm_double(name, count):
    shm = shared_memory.SharedMemory(name=name)    # ATTACH (create=False)
    view = shm.buf.cast("i")
    for i in range(count):
        view[i] *= 2
    view.release()                                  # release the view BEFORE close()
    shm.close()                                     # child only closes - never unlink


def manager_worker(d, lst, ns):
    d["from_child"] = os.getpid() != d["parent_pid"]
    lst.append("child item")
    ns.total = ns.total + 10


def nested_mutation(d):
    d["items"].append("lost!")        # mutates a COPY of the inner list
    d["counter"] = d["counter"] + 1   # top-level assignment goes through the proxy


def task_worker(task_q, result_q):
    while True:
        n = task_q.get()
        if n is None:                  # sentinel: no more work
            return
        result_q.put((n, n * n))


def joinable_worker(task_q, result_q):
    while True:
        n = task_q.get()
        result_q.put(n * 10)
        task_q.task_done()             # tell JoinableQueue: this item is processed


def pipe_echo(conn):
    while True:
        msg = conn.recv()
        if msg == "bye":
            conn.close()
            return
        conn.send(msg.upper())


def wait_for_event(ready, go, out_q):
    ready.set()                        # tell the parent: I'm up and waiting
    out_q.put(f"child woke up, event was set: {go.wait(5)}")


def limited_worker(sem, current, peak):
    with sem:
        with current.get_lock():
            current.value += 1
            peak.value = max(peak.value, current.value)
        time.sleep(0.02)
        with current.get_lock():
            current.value -= 1


def locked_sum(lock_arg):
    return "ok"


_worker_lock = None


def init_lock(lock):
    global _worker_lock
    _worker_lock = lock


def use_global_lock(n):
    with _worker_lock:
        return n


def init_seed(base):
    random.seed(base * 1_000_003 + os.getpid())    # distinct per worker process


def draw(_):
    return (os.getpid(), random.random())


def count_words(text):
    return collections.Counter(text.split())


def count_primes(bounds):
    lo, hi = bounds
    count = 0
    for n in range(max(lo, 2), hi):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count


def work_for_progress(n):
    return count_primes((2, 8000 + n * 2000))


def main():
    print("# 01. Multiprocessing - Why Processes, And The Big Warning About This File")
    print("# ------------------------------------")
    print("python:", sys.version.split()[0])

    # 02. Start Methods: spawn / fork / forkserver
    # ------------------------------------
    # - spawn      : start a FRESH interpreter, import the main module, run
    #                the target. Safe, slower, default on macOS/Windows.
    # - fork       : clone the parent process (copy-on-write). Fast, children
    #                inherit all memory - but copying a process that has
    #                THREADS is dangerous: only the forking thread survives, so
    #                a lock held by another thread stays locked forever in the
    #                child -> random deadlocks. Also unsafe with many macOS
    #                system libraries. (Linux default up to 3.13.)
    # - forkserver : a clean helper process forks children on request - fast
    #                like fork without inheriting your threads/state. Python
    #                3.14 makes it the Linux default (so fork-reliant code that
    #                "worked on Linux" can break - be explicit).
    # - set_start_method() may be called ONCE per program (in the main guard),
    #   libraries should use mp.get_context("spawn") instead of changing the
    #   global setting.
    print("\n# 02. Start Methods: spawn / fork / forkserver")
    print("available on this OS:", sorted(mp.get_all_start_methods()))
    print("method before anyone chose (allow_none):", mp.get_start_method(allow_none=True))
    mp.set_start_method("spawn")        # make the demo identical on every OS
    print("after set_start_method('spawn'):", mp.get_start_method())
    try:
        mp.set_start_method("spawn")
    except RuntimeError as exc:
        print("calling set_start_method twice -> RuntimeError:", exc)
    ctx = mp.get_context("spawn")       # contexts are independent of the global choice
    print("get_context('spawn') gives its own Process/Pool/Queue:", ctx.get_start_method())

    # 03. Process Lifecycle: start / join / is_alive / exitcode / terminate
    # ------------------------------------
    print("\n# 03. Process Lifecycle")
    p = mp.Process(target=noop, name="lifecycle-demo")
    print("before start: pid =", p.pid, "| is_alive =", p.is_alive(), "| exitcode =", p.exitcode)
    t0 = time.perf_counter()
    p.start()
    p.join()
    spawn_cost = time.perf_counter() - t0
    print("after join : is_alive =", p.is_alive(), "| exitcode =", p.exitcode)

    t0 = time.perf_counter()
    th = threading.Thread(target=noop)
    th.start(); th.join()
    thread_cost = time.perf_counter() - t0
    print("starting a process is much slower than a thread:", spawn_cost > thread_cost * 10)

    p = mp.Process(target=exit_with, args=(3,))
    p.start(); p.join()
    print("sys.exit(3) in child -> exitcode:", p.exitcode)

    p = mp.Process(target=sleep_long)
    p.start()
    print("child alive:", p.is_alive())
    p.terminate()                       # SIGTERM; no cleanup in the child, finally blocks do NOT run
    p.join()
    print("after terminate(): alive =", p.is_alive(), "| exitcode negative (killed by signal):", p.exitcode < 0)

    d = mp.Process(target=sleep_long, daemon=True)
    print("daemon process: daemon =", d.daemon, "(terminated automatically if the parent exits; may not spawn children)")
    # Gotcha: an UNCAUGHT exception in a child prints a traceback to stderr and
    # gives exitcode 1 - the parent only learns it by checking exitcode.
    # Pools/executors transport the exception for you (section 05, 06).

    # 04. Separate Memory + pids + Why The __main__ Guard
    # ------------------------------------
    print("\n# 04. Separate Memory, pids, and Why spawn Re-Imports This File")
    CONFIG["mode"] = "changed at runtime in the parent"
    q = mp.Queue()
    child = mp.Process(target=report_identity, args=(q,))
    child.start()
    info = q.get()
    child.join()
    print("parent pid == child's ppid:", os.getpid() == info["ppid"], "| child pid differs:", info["pid"] != os.getpid())
    print("parent's module name:", __name__)
    print("child's  module name:", info["module_name"], "  <- the child IMPORTED this file")
    print("child's import-time log:", [s.split(" in pid")[0] for s in info["import_log"]])
    print("parent changed CONFIG at runtime; child sees:", info["config_mode"])
    print("  -> under spawn the child re-runs the file from the top; runtime changes are NOT inherited")
    print("     (under fork it WOULD see them - another reason code behaves differently per OS)")

    q = mp.Queue()
    child = mp.Process(target=mutate_memory, args=(q,))
    child.start()
    print("child appended to MEMORY_LIST, its length there:", q.get())
    child.join()
    print("parent's MEMORY_LIST afterwards:", MEMORY_LIST, "<- separate memory, nothing shared")

    # 05. os.cpu_count() vs sched_getaffinity
    # ------------------------------------
    # - cpu_count() = CPUs in the machine. In containers/cgroups or with
    #   taskset, you may be ALLOWED fewer; sched_getaffinity(0) (Linux only,
    #   not on macOS/Windows) reports the CPUs this process may really use.
    print("\n# 05. cpu_count vs sched_getaffinity")
    print("os.cpu_count() is a positive int:", os.cpu_count() >= 1)
    if hasattr(os, "sched_getaffinity"):
        print("usable CPUs for this process:", len(os.sched_getaffinity(0)))
    else:
        print("os.sched_getaffinity not available on this OS (macOS/Windows) - use os.cpu_count()")
    workers = min(4, os.cpu_count() or 1)
    print("pool size used for CPU demos: min(4, cpu_count) =", workers, "| os.process_cpu_count() exists only in 3.13+:", hasattr(os, "process_cpu_count"))

    # 06. multiprocessing.Pool - map, imap, imap_unordered, starmap
    # ------------------------------------
    # - A Pool starts N worker processes ONCE and feeds them tasks, so you do
    #   not pay the startup cost per task.
    #     map            -> list, input order, waits for everything
    #     imap           -> lazy iterator, input order
    #     imap_unordered -> lazy iterator, whichever finishes first
    #     starmap        -> like map, but each item is an args tuple
    print("\n# 06. Pool: map / imap / imap_unordered / starmap")
    with mp.Pool(processes=2) as pool:
        print("map            :", pool.map(square, range(8)))
        print("imap           :", list(pool.imap(square, range(8))))
        print("imap_unordered :", sorted(pool.imap_unordered(slow_square, range(8))), "(sorted by us - arrival order varies)")
        print("starmap        :", pool.starmap(add, [(1, 2), (3, 4), (5, 6)]))

        # apply_async: submit ONE call, get an AsyncResult back immediately.
        collected = []
        result = pool.apply_async(square, (12,), callback=collected.append)
        print("apply_async get():", result.get(timeout=30), "| callback received:", collected)
        # callback runs in a helper thread of the PARENT; keep it tiny or it
        # blocks result delivery for the whole pool.
        errors = []
        bad = pool.apply_async(fail_on_three, (3,), error_callback=errors.append)
        bad.wait()
        print("error_callback received:", [repr(e) for e in errors], "| successful():", bad.successful())

    # 6b. get(timeout=) and the context-manager gotcha
    # - `with Pool() as pool` calls terminate() on exit - NOT close()+join().
    #   Anything still running is killed. Collect results INSIDE the block.
    with mp.Pool(processes=1) as pool:
        slow = pool.apply_async(sleepy, (30,))
        try:
            slow.get(timeout=0.05)
        except mp.TimeoutError:
            print("get(timeout=0.05) on a slow task -> multiprocessing.TimeoutError (task keeps running)")
    print("after leaving `with Pool`, the slow task was killed; ready() =", slow.ready())

    # 6c. Exceptions in workers travel back to the parent
    with mp.Pool(processes=2) as pool:
        try:
            pool.map(fail_on_three, range(6))
        except ValueError as exc:
            print("map re-raised in the parent:", repr(exc))
            print("original worker traceback attached as __cause__:", type(exc.__cause__).__name__)
            worker_lines = [ln for ln in exc.__cause__.tb.strip().splitlines() if ln != '"""']
            print("  last traceback line from the worker:", worker_lines[-1])

    # 6d. close / join / terminate (explicit lifecycle)
    pool = mp.Pool(processes=2)
    async_results = [pool.apply_async(square, (n,)) for n in range(5)]
    pool.close()                       # no NEW tasks accepted; queued ones still run
    pool.join()                        # wait for workers to exit (close() first!)
    print("close() + join() finished all work:", [r.get() for r in async_results])
    try:
        pool.apply_async(square, (1,))
    except ValueError as exc:
        print("submitting to a closed pool -> ValueError:", exc)
    # terminate() = stop right now and drop pending work. join() without a
    # prior close()/terminate() raises ValueError.

    # 07. chunksize and maxtasksperchild
    # ------------------------------------
    # - Every task sent to a worker costs a pickle + queue round trip. For
    #   tiny tasks that overhead dwarfs the work. `chunksize=k` sends k items
    #   at a time in ONE message. map()'s default is roughly
    #   ceil(len(items) / (4 * workers)); a bigger chunk = less overhead but
    #   coarser load balancing (one worker may get stuck with slow chunks).
    # - maxtasksperchild=k recycles a worker after k tasks: a cure for slow
    #   memory leaks in native libraries, at the cost of restart time.
    print("\n# 07. chunksize and maxtasksperchild")
    items = list(range(20000))
    default_chunk, extra = divmod(len(items), 4 * 2)
    default_chunk += bool(extra)
    print(f"default chunksize for 20000 items / 2 workers: {default_chunk}")
    with mp.Pool(processes=2) as pool:
        pool.map(tiny, range(100))     # warm up so startup is not measured
        t0 = time.perf_counter()
        r1 = pool.map(tiny, items, chunksize=1)
        slow_t = time.perf_counter() - t0
        t0 = time.perf_counter()
        r2 = pool.map(tiny, items, chunksize=500)
        fast_t = time.perf_counter() - t0
    print("same results either way:", r1 == r2)
    print(f"chunksize=500 is roughly {slow_t / fast_t:.0f}x faster than chunksize=1 for tiny tasks (varies by machine)")

    with mp.Pool(processes=2, maxtasksperchild=1) as pool:
        pids = pool.map(whoami, range(6), chunksize=1)
    print("maxtasksperchild=1, 6 tasks -> distinct worker pids:", len(set(pids)), "(each task got a fresh process)")

    # 08. ProcessPoolExecutor vs multiprocessing.Pool
    # ------------------------------------
    #   | feature            | multiprocessing.Pool        | ProcessPoolExecutor        |
    #   |--------------------|-----------------------------|----------------------------|
    #   | API style          | map/imap/apply_async        | submit/map -> Future       |
    #   | results            | AsyncResult                 | Future (same API as threads)|
    #   | swap for threads   | needs ThreadPool            | change the class name      |
    #   | unordered progress | imap_unordered              | as_completed / wait        |
    #   | worker dies hard   | can hang                    | raises BrokenProcessPool   |
    #   | recycle workers    | maxtasksperchild            | max_tasks_per_child (3.11+)|
    #   | chunking           | chunksize on all methods    | chunksize on map() only    |
    # - Default to ProcessPoolExecutor in new code (consistent API, safer
    #   failure mode); use Pool for imap_unordered / apply_async callbacks.
    print("\n# 08. ProcessPoolExecutor vs multiprocessing.Pool")
    with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as ex:
        fut = ex.submit(add, 20, 22)
        print("submit/result:", fut.result(), "| map:", list(ex.map(square, range(5))))
        bad = ex.submit(fail_on_three, 3)
        print("exception on the Future:", repr(bad.exception()))
        print("with the worker traceback as cause:", type(bad.exception().__cause__).__name__)
    with ProcessPoolExecutor(max_workers=1, mp_context=ctx) as ex:
        dying = ex.submit(os._exit, 1)       # the worker process dies without a trace
        try:
            dying.result(timeout=30)
        except BrokenProcessPool as exc:
            print("worker died hard -> BrokenProcessPool:", type(exc).__name__, "(the whole executor is unusable now)")

    # 09. What Can Be Pickled
    # ------------------------------------
    # - Tasks, arguments and results cross the process boundary via pickle.
    #   Pickle stores functions BY NAME (module + qualified name), so:
    #     OK  : module-level functions/classes, builtins, numbers, str, list,
    #           dict, tuple, dataclasses, functools.partial of a module-level fn
    #     FAIL: lambdas, nested (local) functions, open files, sockets, locks,
    #           threads, generators, database connections
    print("\n# 09. What Can Be Pickled")

    def nested_fn(x):
        return x

    with tempfile.TemporaryFile() as fh:       # auto-deleted - no scratch file left behind
        samples = {
            "lambda": lambda x: x,
            "nested function": nested_fn,
            "open file": fh,
            "threading.Lock": threading.Lock(),
            "generator": (i for i in range(3)),
        }
        for label, obj in samples.items():
            try:
                pickle.dumps(obj)
                print(f"  {label:<16} picklable")
            except Exception as exc:
                print(f"  {label:<16} FAILS -> {type(exc).__name__}: {str(exc)[:55]}")
    print("  module-level fn  picklable:", len(pickle.dumps(square)) > 0)
    print("  partial(module fn) picklable:", len(pickle.dumps(functools.partial(add, 1))) > 0)

    with mp.Pool(processes=1) as pool:
        try:
            pool.map(lambda x: x, [1, 2])
        except Exception as exc:
            print("Pool.map(lambda ...) ->", type(exc).__name__, "(error class differs by Python version)")
    # Fixes: use module-level functions; functools.partial to pre-fill
    # arguments; pass FILE NAMES not file objects and open inside the worker;
    # build unpicklable resources (DB connections) inside an `initializer`.

    # 10. Passing Data Has A Cost
    # ------------------------------------
    # - Arguments are COPIED to the worker, results COPIED back. A 1-million
    #   element list is serialised on every call. Prefer sending SMALL
    #   descriptions of the work ("process rows 0..1000", a file name) and
    #   let the worker load/generate the data itself.
    print("\n# 10. Passing Data Has A Cost")
    big = list(range(1_000_000))
    print(f"pickled size of a 1,000,000-int list: about {len(pickle.dumps(big)) / 1e6:.0f} MB")
    with mp.Pool(processes=1) as pool:
        pool.map(tiny, range(10))                       # warm-up
        t0 = time.perf_counter()
        pool.apply(length_of, (big,))
        copy_t = time.perf_counter() - t0
        t0 = time.perf_counter()
        pool.apply(length_of_range, (len(big),))
        small_t = time.perf_counter() - t0
    print("sending the data is slower than sending its size:", copy_t > small_t)
    print(f"  (copying was roughly {copy_t / small_t:.0f}x slower than passing one int - coarse, machine dependent)")

    # 11. Shared State - Value and Array
    # ------------------------------------
    # - Value/Array live in shared memory, visible to all processes. They
    #   come with a lock (`get_lock()`) because `v.value += 1` is read-modify-
    #   write, NOT atomic - the same race as in 11-Threading-Primitives.py.
    print("\n# 11. Shared State - Value and Array")
    total = ctx.Value("i", 0)                         # 'i' = C int
    procs = [ctx.Process(target=bump_with_lock, args=(total, 5000)) for _ in range(2)]
    for pr in procs: pr.start()
    for pr in procs: pr.join()
    print("Value with get_lock(), 2 processes x 5000 ->", total.value)

    racy = ctx.Value("i", 0, lock=False)              # raw value, no lock at all
    procs = [ctx.Process(target=bump_without_lock, args=(racy, 20000)) for _ in range(2)]
    for pr in procs: pr.start()
    for pr in procs: pr.join()
    print("Value WITHOUT a lock, 2 x 20000 -> never more than 40000:", racy.value <= 40000,
          "(usually less: lost updates)")

    arr = ctx.Array("d", 6)                           # 6 doubles, zero-initialised
    procs = [ctx.Process(target=fill_array, args=(arr, 0, 3)), ctx.Process(target=fill_array, args=(arr, 3, 3))]
    for pr in procs: pr.start()
    for pr in procs: pr.join()
    print("Array filled in parallel by 2 processes (disjoint slices, no lock needed):", list(arr))

    # 12. shared_memory.SharedMemory - Zero-Copy Sharing
    # ------------------------------------
    # - Value/Array hold simple C types. SharedMemory gives you a named block
    #   of raw bytes that any process can attach to BY NAME - no pickling, no
    #   copy. View it with memoryview (or array/NumPy).
    # - Lifecycle rules (the part everyone gets wrong):
    #     * every process calls close() on its own handle when done;
    #     * exactly ONE owner (usually the creator) calls unlink() to free the
    #       OS memory. Forget it and the block leaks until reboot, and the
    #       resource tracker prints "leaked shared_memory objects" warnings.
    #     * release memoryviews (view.release()) BEFORE close(), or you get
    #       BufferError: cannot close exported pointers exist.
    print("\n# 12. shared_memory.SharedMemory")
    count = 4
    shm = shared_memory.SharedMemory(create=True, size=count * 4)   # 4 ints x 4 bytes
    try:
        view = shm.buf.cast("i")
        for i in range(count):
            view[i] = i + 1
        print("parent wrote:", list(view[:count]), f"(OS rounded the block up to {shm.size} bytes - only use what you asked for)")
        worker = ctx.Process(target=shm_double, args=(shm.name, count))
        worker.start(); worker.join()
        print("child doubled in place, parent reads:", list(view[:count]), "(only the NAME was passed, not data)")
        try:
            shm.close()
        except BufferError as exc:
            print("close() while a view exists -> BufferError:", exc)
        view.release()
        shm.close()
    finally:
        shm.unlink()                                  # the owner frees it exactly once
    try:
        shared_memory.SharedMemory(name=shm.name)
    except FileNotFoundError:
        print("after unlink() the block is gone (attaching -> FileNotFoundError)")

    # SharedMemoryManager does close+unlink for you at the end of `with`.
    with SharedMemoryManager() as smm:
        block = smm.SharedMemory(size=8)
        block.buf[:5] = b"hello"
        print("SharedMemoryManager block holds:", bytes(block.buf[:5]), "- cleaned up automatically on exit")

    # 13. Manager - Shared Python Objects Via Proxies
    # ------------------------------------
    # - A Manager runs a SERVER process that owns real dicts/lists/Namespace
    #   objects; everyone else holds PROXIES that send each operation to it
    #   over a pipe. Super convenient (any picklable value, many types) but
    #   every access is an inter-process message - slow - and in-place
    #   mutation of nested objects is NOT seen by the server.
    print("\n# 13. Manager - Shared Objects Via Proxies")
    with ctx.Manager() as manager:
        shared_dict = manager.dict({"parent_pid": os.getpid()})
        shared_list = manager.list(["parent item"])
        ns = manager.Namespace()
        ns.total = 5
        child = ctx.Process(target=manager_worker, args=(shared_dict, shared_list, ns))
        child.start(); child.join()
        print("dict :", dict(shared_dict) | {"parent_pid": "<pid>"})
        print("list :", list(shared_list))
        print("namespace total (5 + 10):", ns.total)

        shared_dict["items"] = []
        shared_dict["counter"] = 0
        child = ctx.Process(target=nested_mutation, args=(shared_dict,))
        child.start(); child.join()
        print("gotcha - nested list append was lost:", shared_dict["items"], "| top-level assign worked:", shared_dict["counter"])
        print("  fix: reassign the whole value  d['items'] = d['items'] + ['x']  (or manager.list() inside)")

        local = {}
        t0 = time.perf_counter()
        for i in range(2000):
            local[i] = i
        local_t = time.perf_counter() - t0
        t0 = time.perf_counter()
        for i in range(2000):
            shared_dict[i] = i
        proxy_t = time.perf_counter() - t0
        print("2000 writes through a proxy are much slower than a local dict:", proxy_t > local_t * 10)

    # 14. Queue, JoinableQueue and Pipe - Message Passing Recap
    # ------------------------------------
    # - Often the cleanest design: share NOTHING, send messages. Each item is
    #   pickled. Patterns: task queue -> N workers -> result queue, with one
    #   sentinel (None) per worker so each knows when to exit.
    # - Collect results BEFORE joining the workers: a child that has put a lot
    #   of data on a queue will not exit until the data is consumed.
    print("\n# 14. Queue / JoinableQueue / Pipe")
    task_q, result_q = ctx.Queue(), ctx.Queue()
    pool_procs = [ctx.Process(target=task_worker, args=(task_q, result_q)) for _ in range(3)]
    for pr in pool_procs: pr.start()
    for n in range(10):
        task_q.put(n)
    for _ in pool_procs:
        task_q.put(None)                          # one sentinel per worker
    results = sorted(result_q.get() for _ in range(10))   # drain BEFORE join
    for pr in pool_procs: pr.join()
    print("worker pool with sentinels:", results[:5], "...", "| all exit codes 0:", all(pr.exitcode == 0 for pr in pool_procs))
    try:
        result_q.get(timeout=0.05)
    except queue.Empty:
        print("get(timeout) on an empty queue -> queue.Empty (q.empty() is unreliable - avoid it)")

    jq, out_q = ctx.JoinableQueue(), ctx.Queue()
    worker = ctx.Process(target=joinable_worker, args=(jq, out_q), daemon=True)
    worker.start()
    for n in range(5):
        jq.put(n)
    jq.join()                                     # blocks until task_done() for every put()
    print("JoinableQueue.join() returned; results:", sorted(out_q.get() for _ in range(5)))
    worker.terminate(); worker.join()             # worker loops forever: stop it

    parent_end, child_end = ctx.Pipe()             # duplex: both ends can send/recv
    echo = ctx.Process(target=pipe_echo, args=(child_end,))
    echo.start()
    parent_end.send("ping")
    print("Pipe round trip:", parent_end.recv())
    parent_end.send("bye")
    echo.join()
    print("(Pipe = fastest, exactly 2 endpoints; Queue = many producers/consumers, a bit slower)")

    # 15. Event, Lock and Semaphore Across Processes
    # ------------------------------------
    # - Same names/ideas as threading (see 11-Threading-Primitives.py) but
    #   they work between processes. They must be given to children at
    #   process creation (inheritance) - not sent later through a Pool.
    print("\n# 15. Event / Lock / Semaphore Across Processes")
    ready, go, out_q = ctx.Event(), ctx.Event(), ctx.Queue()
    child = ctx.Process(target=wait_for_event, args=(ready, go, out_q))
    child.start()
    ready.wait()
    go.set()                                       # release the child
    print(out_q.get())
    child.join()

    sem = ctx.Semaphore(2)
    current, peak = ctx.Value("i", 0), ctx.Value("i", 0)
    procs = [ctx.Process(target=limited_worker, args=(sem, current, peak)) for _ in range(5)]
    for pr in procs: pr.start()
    for pr in procs: pr.join()
    print("5 processes, Semaphore(2): peak concurrent <= 2:", peak.value <= 2, "| nobody left inside:", current.value == 0)

    shared_lock = ctx.Lock()
    with ctx.Pool(processes=1) as pool:
        try:
            pool.map(locked_sum, [shared_lock])
        except RuntimeError as exc:
            print("Lock passed as a Pool.map argument -> RuntimeError:", str(exc)[:60] + "...")
    with ctx.Pool(processes=2, initializer=init_lock, initargs=(shared_lock,)) as pool:
        print("fix: hand the lock to workers via initializer:", pool.map(use_global_lock, range(4)))

    # 16. initializer - Per-Worker Setup (e.g. Different RNG Seed Each)
    # ------------------------------------
    # - `initializer(*initargs)` runs ONCE in every worker when it starts.
    #   Use it for: seeding RNGs, opening DB connections, loading a model,
    #   installing a lock (section 15).
    # - Gotcha with FORK: children inherit the parent's random state, so every
    #   worker would produce the SAME "random" numbers unless re-seeded.
    print("\n# 16. initializer - Per-Worker Setup")
    with ctx.Pool(processes=3, initializer=init_seed, initargs=(7,)) as pool:
        draws = pool.map(draw, range(30), chunksize=1)
    by_pid = collections.defaultdict(list)
    for pid, value in draws:
        by_pid[pid].append(value)
    first_values = {v[0] for v in by_pid.values()}
    print("workers that took part:", len(by_pid) >= 1, "| every worker has its own random stream:", len(first_values) == len(by_pid))

    # 17. Map-Reduce Word Count
    # ------------------------------------
    # - MAP: split the input into chunks, each worker counts its own chunk
    #   (a small Counter comes back - cheap to pickle).
    # - REDUCE: merge the partial Counters in the parent. Counters add with +.
    print("\n# 17. Map-Reduce Word Count")
    sentence = "the quick brown fox jumps over the lazy dog while the dog sleeps"
    lines = [sentence + f" line{i % 3}" for i in range(2000)]
    chunks = [" ".join(lines[i:i + 500]) for i in range(0, len(lines), 500)]
    with ctx.Pool(processes=2) as pool:
        partials = pool.map(count_words, chunks)                    # MAP
    merged = functools.reduce(operator.add, partials, collections.Counter())   # REDUCE
    serial = count_words(" ".join(lines))
    print("partial counters:", len(partials), "| merged equals serial count:", merged == serial)
    print("top 3 words:", merged.most_common(3))

    # 18. CPU-Bound Benchmark - Serial vs Pool (prime counting)
    # ------------------------------------
    # - Pure Python CPU work: threads give ~1x, processes scale with cores.
    #   Split the range into many chunks and count primes in each.
    # - Speedup is printed coarsely, NEVER asserted: it depends on core
    #   count, other programs, and startup cost (small jobs may not win).
    print("\n# 18. CPU-Bound Benchmark - Serial vs Pool")
    LIMIT = 150_000
    step = LIMIT // 12
    ranges = [(i, min(i + step, LIMIT)) for i in range(0, LIMIT, step)]
    t0 = time.perf_counter()
    serial_total = sum(count_primes(r) for r in ranges)
    serial_t = time.perf_counter() - t0
    with ctx.Pool(processes=workers) as pool:
        pool.map(tiny, range(workers))                 # start workers before timing
        t0 = time.perf_counter()
        pool_total = sum(pool.map(count_primes, ranges, chunksize=1))
        pool_t = time.perf_counter() - t0
    print(f"primes below {LIMIT}: serial = {serial_total}, pool = {pool_total}, equal: {serial_total == pool_total}")
    print(f"pool with {workers} workers is roughly {serial_t / pool_t:.1f}x the speed of serial (varies; ~{workers}x at best)")

    # 19. ProcessPoolExecutor + as_completed - Progress Reporting
    # ------------------------------------
    print("\n# 19. ProcessPoolExecutor + as_completed Progress")
    with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as ex:
        futures = {ex.submit(work_for_progress, n): n for n in range(6)}
        done_count = 0
        collected = {}
        for fut in as_completed(futures):
            done_count += 1
            collected[futures[fut]] = fut.result()
            print(f"  progress: {done_count}/{len(futures)} tasks finished")
    print("results by task id (sorted):", dict(sorted(collected.items())))

    # 20. Which Tool? Threads vs Processes vs asyncio vs concurrent.futures
    # ------------------------------------
    #   | Situation                                   | Reach for                          |
    #   |---------------------------------------------|------------------------------------|
    #   | Many network/disk waits, simple code        | ThreadPoolExecutor                 |
    #   | Thousands of connections, one thread        | asyncio (13-Asyncio-Advanced.py)   |
    #   | Heavy pure-Python/number crunching          | ProcessPoolExecutor / mp.Pool      |
    #   | C extension that releases the GIL (NumPy..) | threads may already be enough      |
    #   | Blocking library inside async code          | asyncio.to_thread / run_in_executor|
    #   | Big shared read-only data, many workers     | SharedMemory (or fork + COW, risky)|
    #   | Many small tasks                            | chunksize / batch them             |
    #   | Need isolation (crash/leak safety)          | processes (+ maxtasksperchild)     |
    # - concurrent.futures gives the SAME Future API over threads or
    #   processes: start with ThreadPoolExecutor, swap the class when the
    #   profiler says CPU is the bottleneck.
    print("\n# 20. Which Tool?")
    print("# - waiting on I/O ......... threads or asyncio")
    print("# - burning CPU ............ processes")
    print("# - shared mutable data .... avoid; send messages, or SharedMemory/Manager if you must")
    print("# - always ................. module-level targets + `if __name__ == '__main__'`")


if __name__ == "__main__":
    mp.freeze_support()          # no-op except for frozen Windows executables
    main()
