from contextlib import contextmanager

# 01. Context Managers - Introduction
# ------------------------------------
# - A context manager sets up a resource, hands control to a block of code,
#   then guarantees cleanup afterwards - even if an exception occurs.
# - Used via the `with` statement.

print("# 01. Context Managers - Introduction")
print("# ------------------------------------")

# 02. The `with` Statement (built-in example: file handling)
# ------------------------------------
with open("temp_demo.txt", "w") as f:
    f.write("Hello, context managers!")
print("\n# 02. The `with` Statement")
print("file written and automatically closed")
print("file closed?", f.closed)  # True - closed automatically, even on error

# 03. Why Context Managers? (vs manual try/finally)
# ------------------------------------
print("\n# 03. Why Context Managers?")
file = open("temp_demo.txt", "r")
try:
    content = file.read()
    print("content:", content)
finally:
    file.close()
print("# - `with` does this automatically and is less error-prone.")

# 04. Writing a Class-Based Context Manager
# ------------------------------------
# - Implement __enter__ (setup, returns resource) and __exit__ (cleanup).
class ManagedFile:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Closing {self.filename}")
        self.file.close()
        return False  # False -> don't suppress exceptions

print("\n# 04. Writing a Class-Based Context Manager")
with ManagedFile("temp_demo.txt", "r") as f:
    print("read:", f.read())

# 05. Handling Exceptions Inside __exit__
# ------------------------------------
class SuppressError:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ZeroDivisionError:
            print(f"Suppressed: {exc_value}")
            return True  # True -> exception is suppressed, code continues
        return False

print("\n# 05. Handling Exceptions Inside __exit__")
with SuppressError():
    result = 10 / 0
print("continues normally after suppressed exception")

# 06. Function-Based Context Manager (contextlib.contextmanager)
# ------------------------------------
@contextmanager
def managed_resource(name):
    print(f"Acquiring resource: {name}")
    try:
        yield name  # value returned to the `as` variable
    finally:
        print(f"Releasing resource: {name}")

print("\n# 06. Function-Based Context Manager")
with managed_resource("Database Connection") as res:
    print(f"Using {res}")

# 07. Multiple Context Managers in One `with`
# ------------------------------------
print("\n# 07. Multiple Context Managers in One `with`")
with open("temp_demo.txt", "r") as f1, open("temp_demo.txt", "r") as f2:
    print("both files open:", not f1.closed and not f2.closed)

# 09. contextlib.ExitStack - a Variable Number of Context Managers
# ------------------------------------
# - Section 07 works when you know the exact managers ahead of time.
#   ExitStack handles a number decided AT RUNTIME (e.g. one file per item
#   in a list) - each is entered via stack.enter_context() and all get
#   exited in reverse order when the `with` block ends, even on error.
from contextlib import ExitStack

print("\n# 09. contextlib.ExitStack for a Variable Number of Managers")
filenames = ["temp_a.txt", "temp_b.txt", "temp_c.txt"]
for name in filenames:
    with open(name, "w") as f:
        f.write(f"content of {name}")

with ExitStack() as stack:
    open_files = [stack.enter_context(open(name, "r")) for name in filenames]
    print("all opened at once, count:", len(open_files))
    print("contents:", [f.read() for f in open_files])
print("all files closed automatically when ExitStack's `with` block ends")

# 10. Reentrant vs Reusable Context Managers
# ------------------------------------
# - Reusable: the SAME instance can be used in separate `with` blocks,
#   one after another (not nested).
# - Reentrant: the same instance can be used in NESTED `with` blocks too.
# - Most @contextmanager-based generators are only reusable, NOT reentrant -
#   entering a second time before the first `with` exits reuses the same
#   exhausted generator and raises an error.
print("\n# 10. Reentrant vs Reusable Context Managers")
resource = managed_resource("Reusable Demo")
with resource as r1:
    print("first use:", r1)
# using it again AFTER the first block closed - this is fine (reusable)
resource2 = managed_resource("Reusable Demo 2")
with resource2 as r2:
    print("second, separate use:", r2)

try:
    reentrant_attempt = managed_resource("Reentrant Attempt")
    with reentrant_attempt as outer:
        with reentrant_attempt as inner:  # nesting the SAME instance
            print("this line won't be reached")
except Exception as e:
    print(f"nesting the same @contextmanager instance fails: {type(e).__name__}: {e}")

# 11. contextlib.suppress (cross-reference)
# ------------------------------------
# - contextlib.suppress(SomeError) is itself a context manager that turns
#   a specific exception into a no-op - a cleaner alternative to
#   try/except/pass. Full depth is in 03-Error-And-Exception-Handling.py.
from contextlib import suppress

print("\n# 11. contextlib.suppress (cross-ref to Error Handling file)")
with suppress(FileNotFoundError):
    open("does_not_exist.txt", "r")
print("missing-file error suppressed, execution continues")

# 12. Async Context Managers (brief mention)
# ------------------------------------
# - `async with` uses __aenter__/__aexit__ instead of __enter__/__exit__ -
#   both are coroutines, awaited during entry/exit (e.g. for an async DB
#   connection). Full depth, including a runnable example, is in
#   10-Async-Await.py.
print("\n# 12. Async Context Managers (brief, see 10-Async-Await.py)")
print("# class AsyncResource:")
print("#     async def __aenter__(self): ...")
print("#     async def __aexit__(self, exc_type, exc_value, tb): ...")
print("# used as: async with AsyncResource() as res: ...")

# 13. Cleanup
# ------------------------------------
import os
os.remove("temp_demo.txt")
for name in filenames:
    os.remove(name)
print("\n# 13. Cleanup")
print("temp files removed")
