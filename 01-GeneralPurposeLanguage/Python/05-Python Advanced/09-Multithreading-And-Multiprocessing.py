import threading
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 01. Concurrency vs Parallelism - Introduction
# ------------------------------------
# - Threading: multiple threads share the same process/memory. Good for
#   I/O-bound tasks (network, file, DB) since threads wait on I/O.
# - Multiprocessing: multiple separate processes, each with own memory.
#   Good for CPU-bound tasks since it bypasses the GIL.

print("# 01. Concurrency vs Parallelism - Introduction")
print("# ------------------------------------")

# 02. The GIL (Global Interpreter Lock) - Why It Matters
# ------------------------------------
print("\n# 02. The GIL")
print("# - Only one thread executes Python bytecode at a time (CPython).")
print("# - Threads don't give true CPU parallelism for pure Python code.")
print("# - I/O-bound work still benefits from threads (GIL released during I/O).")

# 03. Basic Threading with threading.Thread
# ------------------------------------
def print_numbers():
    for i in range(3):
        print(f"thread: {i}")
        time.sleep(0.1)

print("\n# 03. Basic Threading")
t = threading.Thread(target=print_numbers)
t.start()
t.join()  # wait for thread to finish

# 04. Running Multiple Threads
# ------------------------------------
def worker(name):
    print(f"Worker {name} starting")
    time.sleep(0.2)
    print(f"Worker {name} done")

print("\n# 04. Running Multiple Threads")
threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 05. Thread Synchronization with Lock
# ------------------------------------
# - Prevents race conditions when multiple threads modify shared state.
counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

print("\n# 05. Thread Synchronization with Lock")
threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("final counter (with lock, always correct):", counter)

# 06. ThreadPoolExecutor - Managed Thread Pool
# ------------------------------------
def square(n):
    return n * n

print("\n# 06. ThreadPoolExecutor")
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(square, [1, 2, 3, 4, 5]))
print("results:", results)

# 07. Basic Multiprocessing with multiprocessing.Process
# ------------------------------------
def cpu_task(n):
    total = sum(i * i for i in range(n))
    print(f"process computed total for n={n}: {total}")

# NOTE: multiprocessing (with the default "spawn" start method, used on
# macOS/Windows) re-IMPORTS this file in each child process. Any function
# used as a Process target must therefore be defined at MODULE level (like
# cpu_task above), not nested inside `if __name__ == "__main__":` or another
# function - a nested function isn't reachable when the child re-imports.
def producer_process(mp_queue):
    for item in range(3):
        mp_queue.put(item ** 2)
    mp_queue.put(None)

def pipe_sender(conn):
    conn.send("hello from the other process")
    conn.close()

if __name__ == "__main__":
    print("\n# 07. Basic Multiprocessing")
    p = multiprocessing.Process(target=cpu_task, args=(1_000_000,))
    p.start()
    p.join()

    # 08. ProcessPoolExecutor - Managed Process Pool (true parallelism)
    # ------------------------------------
    print("\n# 08. ProcessPoolExecutor")
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(square, [1, 2, 3, 4]))
    print("results:", results)

    # 09. When to Use What
    # ------------------------------------
    print("\n# 09. When to Use What")
    print("# - I/O-bound (network, file, DB): threading or asyncio")
    print("# - CPU-bound (heavy computation): multiprocessing")

    # 10. Deadlock Scenario and How to Avoid It
    # ------------------------------------
    # - A deadlock happens when two threads each hold a lock the OTHER one
    #   needs, so both wait forever. Classic cause: acquiring two locks in
    #   INCONSISTENT order across threads.
    # - This demo does NOT actually deadlock - it shows the risky pattern in
    #   comments, then the safe fix: always acquire locks in the SAME order.
    print("\n# 10. Deadlock Scenario and How to Avoid It")
    print("# RISKY (can deadlock):")
    print("#   thread A: with lock_1: with lock_2: ...")
    print("#   thread B: with lock_2: with lock_1: ...   <- opposite order!")
    print("# If A grabs lock_1 and B grabs lock_2 at the same moment,")
    print("# each then waits forever for the lock the other is holding.")

    lock_1 = threading.Lock()
    lock_2 = threading.Lock()

    def safe_worker(first, second, label):
        # SAFE: every thread acquires locks in the SAME order (lock_1 then lock_2)
        with first:
            with second:
                print(f"{label} acquired both locks safely")

    safe_threads = [
        threading.Thread(target=safe_worker, args=(lock_1, lock_2, "thread-A")),
        threading.Thread(target=safe_worker, args=(lock_1, lock_2, "thread-B")),
    ]
    for t in safe_threads:
        t.start()
    for t in safe_threads:
        t.join()
    print("both threads finished - no deadlock, because lock order was consistent")

    # 11. queue.Queue - Safe Thread Communication (producer/consumer)
    # ------------------------------------
    # - queue.Queue is thread-safe out of the box (unlike a plain list), so
    #   it's the standard way for threads to hand off work/results.
    import queue

    print("\n# 11. queue.Queue Producer/Consumer")
    work_queue = queue.Queue()
    results_list = []

    def producer():
        for item in range(5):
            work_queue.put(item)
        work_queue.put(None)  # sentinel: tells the consumer to stop

    def consumer():
        while True:
            item = work_queue.get()
            if item is None:
                break
            results_list.append(item * 10)

    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()
    consumer_thread.join()
    print("consumer processed:", results_list)

    # 12. multiprocessing.Queue and Pipe - Inter-Process Communication
    # ------------------------------------
    # - Threads share memory, so queue.Queue works directly. Separate
    #   PROCESSES don't share memory, so they need multiprocessing.Queue
    #   (many-to-many) or Pipe (fast two-endpoint channel) instead, which
    #   pickle data across the process boundary.
    print("\n# 12. multiprocessing.Queue and Pipe")

    mp_result_queue = multiprocessing.Queue()
    producer_proc = multiprocessing.Process(target=producer_process, args=(mp_result_queue,))
    producer_proc.start()
    mp_results = []
    while True:
        value = mp_result_queue.get()
        if value is None:
            break
        mp_results.append(value)
    producer_proc.join()
    print("received via multiprocessing.Queue:", mp_results)

    parent_conn, child_conn = multiprocessing.Pipe()
    pipe_proc = multiprocessing.Process(target=pipe_sender, args=(child_conn,))
    pipe_proc.start()
    print("received via Pipe:", parent_conn.recv())
    pipe_proc.join()

    # 13. Why Objects Must Be Picklable for Multiprocessing
    # ------------------------------------
    # - Arguments/results sent to a separate process are PICKLED (serialized)
    #   to cross the process boundary. Lambdas and closures can't be pickled,
    #   which is a common source of confusing multiprocessing errors.
    print("\n# 13. Why Objects Must Be Picklable")
    try:
        unpicklable_proc = multiprocessing.Process(target=lambda: print("never runs"))
        unpicklable_proc.start()
        unpicklable_proc.join()
    except Exception as e:
        print(f"caught {type(e).__name__} - lambdas can't be pickled for multiprocessing: {e}")

    # 14. os.cpu_count() - Sizing a Pool
    # ------------------------------------
    # - A CPU-bound pool rarely benefits from more workers than CPU cores -
    #   os.cpu_count() is the standard way to size max_workers sensibly.
    import os

    print("\n# 14. os.cpu_count() for Sizing a Pool")
    available_cores = os.cpu_count()
    print("CPU cores available:", available_cores)
    with ProcessPoolExecutor(max_workers=available_cores) as executor:
        results = list(executor.map(square, [1, 2, 3, 4]))
    print("pool sized to cpu_count(), results:", results)
