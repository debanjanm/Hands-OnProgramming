# 01. Errors and Exceptions - Introduction
# ------------------------------------
# - Syntax errors: code is malformed, caught before the program even runs.
# - Exceptions: errors that occur during execution (e.g. dividing by zero).
# - Exception handling lets a program respond to errors instead of crashing.

print("# 01. Errors and Exceptions - Introduction")
print("# ------------------------------------")

# 02. Basic try/except
# ------------------------------------
print("\n# 02. Basic try/except")
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Caught: division by zero")

# 03. Catching Multiple Exception Types
# ------------------------------------
print("\n# 03. Catching Multiple Exception Types")
for value in ["10", "abc", 0]:
    try:
        print(100 / int(value))
    except ZeroDivisionError:
        print("Caught: cannot divide by zero")
    except ValueError:
        print(f"Caught: '{value}' is not a valid number")

# 04. Catching Multiple Exceptions in One Line
# ------------------------------------
print("\n# 04. Catching Multiple Exceptions in One Line")
try:
    int("not a number")
except (ValueError, TypeError) as e:
    print(f"Caught one of ValueError/TypeError: {e}")

# 05. else Clause - Runs Only if No Exception Occurred
# ------------------------------------
print("\n# 05. else Clause")
try:
    value = int("42")
except ValueError:
    print("conversion failed")
else:
    print("conversion succeeded, value:", value)

# 06. finally Clause - Always Runs (cleanup)
# ------------------------------------
print("\n# 06. finally Clause")
try:
    print("doing risky work")
    raise ValueError("something went wrong")
except ValueError as e:
    print("handled:", e)
finally:
    print("finally always runs (cleanup code goes here)")

# 07. Raising Exceptions Manually
# ------------------------------------
print("\n# 07. Raising Exceptions Manually")
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount

try:
    withdraw(100, 500)
except ValueError as e:
    print("Caught raised exception:", e)

# 08. Custom Exception Classes
# ------------------------------------
# - Inherit from Exception (or a more specific built-in) to create your
#   own meaningful exception types.
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw {amount}, balance is only {balance}")

def withdraw_v2(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount

print("\n# 08. Custom Exception Classes")
try:
    withdraw_v2(100, 500)
except InsufficientFundsError as e:
    print("Caught custom exception:", e)
    print("extra data on exception:", e.balance, e.amount)

# 09. Exception Chaining (raise ... from ...)
# ------------------------------------
print("\n# 09. Exception Chaining")
def load_config():
    try:
        int("not-a-number")
    except ValueError as original_error:
        raise RuntimeError("Failed to load config") from original_error

try:
    load_config()
except RuntimeError as e:
    print("Caught:", e)
    print("original cause:", e.__cause__)

# 10. Built-in Exception Hierarchy (common ones)
# ------------------------------------
print("\n# 10. Built-in Exception Hierarchy (reference)")
print("# BaseException")
print("#  -> Exception")
print("#      -> ValueError, TypeError, KeyError, IndexError")
print("#      -> ZeroDivisionError, ArithmeticError")
print("#      -> FileNotFoundError, OSError")
print("#      -> AttributeError, NameError, ImportError")
print("# Catching a base class (e.g. Exception) also catches its subclasses.")

try:
    [1, 2, 3][10]
except IndexError:
    print("caught IndexError")

try:
    {"a": 1}["missing"]
except KeyError:
    print("caught KeyError")

# 11. Context Managers as Exception-Safe Cleanup (recap)
# ------------------------------------
print("\n# 11. Context Managers as Exception-Safe Cleanup")
print("# - `with` statements (see 06-Context-Managers.py) guarantee cleanup")
print("#   even when an exception occurs, similar to try/finally.")

# 12. Exception Groups and except* (Python 3.11+)
# ------------------------------------
# - ExceptionGroup bundles multiple unrelated exceptions raised together
#   (common in concurrent code where several tasks can fail independently).
# - except* matches exceptions INSIDE the group by type, and can run more
#   than one except* clause if the group has a mix of types.
# - Skip gracefully on older Python since the syntax doesn't even parse there.
import sys

print("\n# 12. Exception Groups and except* (3.11+)")
if sys.version_info >= (3, 11):
    # Written as a string + exec so the file still IMPORTS/PARSES on < 3.11
    # (except* is new syntax, not just a new runtime feature).
    code = '''
try:
    raise ExceptionGroup(
        "multiple failures",
        [ValueError("bad value"), TypeError("bad type"), ValueError("another bad value")],
    )
except* ValueError as eg:
    print("handled ValueError(s):", [str(e) for e in eg.exceptions])
except* TypeError as eg:
    print("handled TypeError(s):", [str(e) for e in eg.exceptions])
'''
    exec(code)
else:
    print("skipped: except* requires Python 3.11+, this interpreter is", sys.version_info[:3])

# 13. Bare `raise` vs `raise e` Inside except
# ------------------------------------
# - Bare `raise` re-raises the CURRENT exception with its ORIGINAL traceback
#   intact, showing exactly where it first occurred.
# - `raise e` raises the SAME exception object, but Python adds a NEW frame
#   for that raise statement, making the traceback look like it started here.
# - Prefer bare `raise` when re-raising - it keeps debugging info accurate.
print("\n# 13. Bare `raise` vs `raise e`")
def reraise_bare():
    try:
        int("not-a-number")
    except ValueError:
        print("re-raising with bare `raise` (preserves original traceback)")
        raise

def reraise_with_e():
    try:
        int("not-a-number")
    except ValueError as e:
        print("re-raising with `raise e` (adds this frame to the traceback)")
        raise e

for fn in (reraise_bare, reraise_with_e):
    try:
        fn()
    except ValueError as e:
        print("caught at top level:", e)

# 14. contextlib.suppress() - Cleaner try/except/pass
# ------------------------------------
# - When you genuinely want to ignore a specific exception, suppress() reads
#   better than a try/except block whose body is just `pass`.
import contextlib

print("\n# 14. contextlib.suppress()")
data = {"a": 1}
with contextlib.suppress(KeyError):
    print(data["missing"])  # raises KeyError, silently ignored
print("execution continues normally after the suppressed block")

# 15. Custom Exception Hierarchy Design
# ------------------------------------
# - Define one base exception for your app/module, then specific subclasses
#   for each failure mode. Callers can catch the base to handle the whole
#   family, or a specific subclass to handle just one case.
class AppError(Exception):
    """Base exception for this application."""

class ValidationError(AppError):
    """Raised when input data fails validation."""

class NotFoundError(AppError):
    """Raised when a requested resource doesn't exist."""

def fetch_user(user_id):
    if user_id < 0:
        raise ValidationError(f"user_id cannot be negative: {user_id}")
    if user_id > 100:
        raise NotFoundError(f"no user with id {user_id}")
    return {"id": user_id, "name": "demo-user"}

print("\n# 15. Custom Exception Hierarchy Design")
for uid in (-1, 999, 5):
    try:
        print("fetched:", fetch_user(uid))
    except AppError as e:
        # catching the BASE class handles both ValidationError and NotFoundError
        print(f"caught {type(e).__name__} via base AppError:", e)

# 16. The traceback Module - Formatting/Logging Exceptions Manually
# ------------------------------------
# - traceback.format_exc() gives the full traceback as a string, useful for
#   logging to a file instead of just letting it print to stderr.
import traceback

print("\n# 16. traceback Module")
try:
    1 / 0
except ZeroDivisionError:
    formatted = traceback.format_exc()
    print("formatted traceback (first line only shown here):")
    print(formatted.strip().splitlines()[-1])

# 17. Implicit Exception Chaining - __context__
# ------------------------------------
# - If a NEW exception is raised while an `except` block is handling another
#   one, Python automatically remembers the first on `new.__context__`.
#   You did not ask for it - it just happens ("implicit chaining").
# - Compare with section 05's `raise X from Y`: that sets `__cause__`
#   ("explicit chaining") and means "Y is the direct reason for X".
# - `__suppress_context__` says whether the traceback should HIDE the context.
print("\n# 17. Implicit chaining: __context__")


def implicit_chain():
    try:
        int("abc")                      # ValueError
    except ValueError:
        {}["missing"]                   # a different bug while handling it -> KeyError


try:
    implicit_chain()
except KeyError as e:
    print("caught            :", repr(e))
    print("e.__context__     :", repr(e.__context__))      # the ValueError, kept for us
    print("e.__cause__       :", e.__cause__)              # None - nobody wrote `from`
    print("e.__suppress_context__:", e.__suppress_context__)  # False -> traceback shows context


def explicit_chain():
    try:
        int("abc")
    except ValueError as err:
        raise RuntimeError("config is invalid") from err


try:
    explicit_chain()
except RuntimeError as e:
    print("explicit: __cause__ =", repr(e.__cause__), "| __context__ =", repr(e.__context__),
          "| __suppress_context__ =", e.__suppress_context__)

# 18. What the Traceback Text Says About Chains
# ------------------------------------
# - The two chain types print DIFFERENT sentences between the tracebacks:
#     implicit (__context__): "During handling of the above exception, another exception occurred"
#     explicit (__cause__)  : "The above exception was the direct cause of the following exception"
# - Reading it: the FIRST traceback shown is the ORIGINAL problem; the last
#   one is what finally escaped. Start at the root cause, not the last line.
print("\n# 18. Traceback text for chains")
for label, fn in (("implicit", implicit_chain), ("explicit", explicit_chain)):
    try:
        fn()
    except Exception as e:
        text = "".join(traceback.format_exception(e))       # 3.10+ signature: pass the exception
        link = [ln for ln in text.splitlines()
                if ln.startswith(("During handling", "The above exception"))]
        print(f"{label}: {link[0]}")

# 19. `raise ... from None` - Hide the Context
# ------------------------------------
# - `from None` sets __suppress_context__ = True: the traceback no longer
#   prints the earlier exception (it is still stored on __context__).
# - Appropriate when the original is an INTERNAL detail the caller should not
#   see - e.g. a lookup failing in a private dict, and you translate it into
#   a clean public error. Do NOT use it to hide information you need for
#   debugging; if the original helps, prefer `from original`.
print("\n# 19. raise ... from None")


def get_setting(name):
    settings = {"debug": True}
    try:
        return settings[name]
    except KeyError:
        raise LookupError(f"unknown setting {name!r}") from None   # hide the dict KeyError


try:
    get_setting("colour")
except LookupError as e:
    print("caught:", e)
    print("__cause__:", e.__cause__, "| __suppress_context__:", e.__suppress_context__)
    print("context still stored (for debuggers):", repr(e.__context__))
    shown = "".join(traceback.format_exception(e))
    print("'During handling' printed in traceback?", "During handling" in shown)   # False - hidden
    print("last traceback line:", shown.strip().splitlines()[-1])

# 20. Nested try/except - Translate Errors Between Layers
# ------------------------------------
# - Inner code catches low-level errors and re-raises them as a meaningful
#   error of YOUR layer; the outer code only has to know about your layer.
# - Only catch what you can actually handle or translate; let the rest pass.
print("\n# 20. Nested try/except (translating errors)")


class ConfigError(Exception):
    pass


def parse_port(text):
    try:
        port = int(text)
    except ValueError as e:                              # inner handler: low-level error
        raise ConfigError(f"port must be a number, got {text!r}") from e
    if not 0 < port < 65536:
        raise ConfigError(f"port out of range: {port}")
    return port


for raw in ("8080", "http", "99999"):
    try:                                                 # outer handler: only knows ConfigError
        print("port:", parse_port(raw))
    except ConfigError as e:
        print("config problem:", e, "| root cause:", type(e.__cause__).__name__)

# 21. An Exception Inside `except` / `finally` REPLACES the Original
# ------------------------------------
# - If cleanup code in `finally` (or an `except` block) raises, the caller
#   sees the NEW exception. The original survives only on __context__, so
#   `except OriginalType` around the call will NOT catch it any more.
# - Fix: make cleanup safe - wrap it in its own try/except so the original
#   keeps propagating (and log/attach the cleanup failure instead).
print("\n# 21. Exception in finally replaces the original")


def risky_replaced():
    try:
        raise ValueError("the REAL problem")
    finally:
        raise RuntimeError("cleanup failed")             # overrides the ValueError


try:
    risky_replaced()
except ValueError:
    print("never printed: ValueError was replaced")
except RuntimeError as e:
    print("caller got RuntimeError; original only on __context__:", repr(e.__context__))


def risky_preserved():
    try:
        raise ValueError("the REAL problem")
    finally:
        try:
            raise RuntimeError("cleanup failed")         # same failure, now contained
        except RuntimeError as cleanup_err:
            print("   (logged cleanup failure:", cleanup_err, ")")


try:
    risky_preserved()
except ValueError as e:
    print("caller still gets the original:", e)

# 22. `else` vs Putting More Code in `try` (Keep `try` Narrow)
# ------------------------------------
# - A `try` block should contain ONLY the line(s) that can raise the error
#   you are catching. Everything else belongs in `else` (runs on success).
# - Why: a broad `try` can catch an exception from unrelated code and
#   report the wrong problem.
print("\n# 22. Narrow try blocks (bad vs good)")


def process(value):                                      # pretend this has a bug
    return value.nonexistent_method()


# BAD: `except ValueError` also wraps process(), so a ValueError raised
# INSIDE process() would be mistaken for "bad input".
def bad_version(text):
    try:
        number = int(text)
        return process(number)                           # unrelated code inside try
    except ValueError:
        return "bad input"                               # misleading if process() raised ValueError


# GOOD: only int() is guarded; process() runs in else, so ITS errors are
# not swallowed by the ValueError handler.
def good_version(text):
    try:
        number = int(text)
    except ValueError:
        return "bad input"
    else:
        return process(number)


print("bad  with 'abc':", bad_version("abc"))
for fn in (bad_version, good_version):
    try:
        fn("5")
    except AttributeError as e:
        print(f"{fn.__name__}('5') -> real bug surfaced: {e}")

# 23. Gotcha: `return` in `finally` Swallows Exceptions
# ------------------------------------
# - A `return` (or `break`/`continue`) inside `finally` cancels the exception
#   that is in flight - it silently disappears. Never do this.
# - Python 3.14 even warns about it (PEP 765). Use `finally` for cleanup only.
print("\n# 23. return in finally swallows the exception")


def swallow():
    try:
        raise ValueError("important error")
    finally:
        return "finally won"                             # exception is discarded!


print("swallow() ->", swallow(), "(no exception reached the caller)")


def safe_cleanup():
    try:
        raise ValueError("important error")
    finally:
        print("   cleaning up (no return here)")


try:
    safe_cleanup()
except ValueError as e:
    print("safe version still raises:", e)

# 24. try/except Inside a Loop - continue and break
# ------------------------------------
# - Put try/except INSIDE the loop to handle each item separately:
#   `continue` = skip the bad item, `break` = stop everything on a fatal one.
# - Putting the try OUTSIDE the loop stops at the first failure.
print("\n# 24. try/except in a loop with continue/break")
good = []
for item in ["1", "two", "3", "STOP", "5"]:
    try:
        if item == "STOP":
            raise KeyboardInterrupt                      # simulate a fatal signal
        good.append(int(item))
    except ValueError:
        print("   skipping bad item:", item)
        continue                                         # go on with the next item
    except KeyboardInterrupt:
        print("   fatal signal, stopping the loop")
        break                                            # leave the loop; '5' is never read
print("collected:", good)

# 25. BaseException vs Exception - Why Never a Bare `except:`
# ------------------------------------
# - `Exception` = errors your program can reasonably handle.
# - `BaseException` also includes control-flow signals: KeyboardInterrupt
#   (Ctrl+C), SystemExit (sys.exit()), GeneratorExit (generator closing).
#   They are deliberately NOT subclasses of Exception.
# - A bare `except:` (or `except BaseException:`) swallows them too, so the
#   user can no longer Ctrl+C your program and sys.exit() stops working.
print("\n# 25. BaseException vs Exception")
for cls in (KeyboardInterrupt, SystemExit, GeneratorExit, ValueError):
    print(f"{cls.__name__:18} subclass of Exception? {issubclass(cls, Exception)!s:5} "
          f"| of BaseException? {issubclass(cls, BaseException)}")


def bare_except_trap():
    try:
        sys.exit(1)
    except:                                              # noqa: E722 - the anti-pattern, on purpose
        print("   bare except swallowed sys.exit()! the program would carry on")


bare_except_trap()
try:
    sys.exit(2)
except Exception:
    print("not reached: `except Exception` does not catch SystemExit")
except SystemExit as e:
    print("SystemExit passes `except Exception`; caught explicitly, code =", e.code)

# 26. Exception.add_note() (Python 3.11+)
# ------------------------------------
# - Attach extra context to an exception WITHOUT changing its type/message;
#   notes are printed under the error in the traceback and live in `__notes__`.
print("\n# 26. add_note()")
if sys.version_info >= (3, 11):
    try:
        try:
            int("x1")
        except ValueError as e:
            e.add_note("while reading column 'age' of row 7")
            e.add_note("file: users.csv")
            raise
    except ValueError as e:
        print("message  :", e)
        print("__notes__:", e.__notes__)
        print("last lines of the traceback:", "".join(traceback.format_exception(e)).splitlines()[-2:])
else:
    print("skipped: add_note() needs Python 3.11+, this interpreter is", sys.version_info[:3])

# 27. sys.exc_info() - The Exception Being Handled Right Now
# ------------------------------------
# - Returns (type, value, traceback) of the exception currently handled, or
#   (None, None, None) outside an `except`. Older code used it; today you
#   normally just write `except X as e` (or `sys.exception()` on 3.11+).
print("\n# 27. sys.exc_info()")
print("outside any except:", sys.exc_info())
try:
    {}["k"]
except KeyError:
    etype, evalue, etb = sys.exc_info()
    print("inside except     :", etype.__name__, "|", evalue, "| traceback object:", type(etb).__name__)
print("after the except  :", sys.exc_info(), "(cleared again)")

# 28. warnings vs Exceptions
# ------------------------------------
# - An exception STOPS the normal flow. A warning only REPORTS a problem
#   (deprecated feature, risky usage) and the code keeps running.
# - warnings.warn(msg, Category) emits one; filters decide what happens:
#   "default"/"once" (print), "ignore" (hide), "error" (turn into an exception).
import warnings

print("\n# 28. warnings module")


def old_api():
    warnings.warn("old_api() is deprecated, use new_api()", DeprecationWarning, stacklevel=2)
    return "result"


with warnings.catch_warnings(record=True) as caught:     # record instead of printing to stderr
    warnings.simplefilter("always")
    print("returned:", old_api(), "- execution continued")
print("recorded :", [f"{w.category.__name__}: {w.message}" for w in caught])

with warnings.catch_warnings():
    warnings.simplefilter("error")                       # promote every warning to an exception
    try:
        old_api()
    except DeprecationWarning as e:
        print("as an error:", e)

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("ignore")
    old_api()
print("ignored  : warnings recorded =", len(caught))
print("# - Command line: `python -W error file.py` turns all warnings into errors (handy in CI).")

# 29. EAFP vs LBYL
# ------------------------------------
# - LBYL = "Look Before You Leap": check first, then act.
# - EAFP = "Easier to Ask Forgiveness than Permission": just act, handle failure.
# - Python prefers EAFP: no race between check and use (the file can vanish
#   after you checked), and the happy path stays short. LBYL is still right
#   when failure is common/cheap to test, or the action is not safely undoable.
import os
import tempfile

print("\n# 29. EAFP vs LBYL")
tmp_dir = tempfile.mkdtemp()
path = os.path.join(tmp_dir, "missing.txt")


def read_lbyl(p):
    if os.path.exists(p):                                # check...
        with open(p) as f:                               # ...but the file could be deleted right here (race)
            return f.read()
    return "<no file>"


def read_eafp(p):
    try:
        with open(p) as f:                               # just try it
            return f.read()
    except FileNotFoundError:
        return "<no file>"


print("LBYL:", read_lbyl(path))
print("EAFP:", read_eafp(path))

counts = {}
for word in ["a", "b", "a"]:
    try:
        counts[word] += 1                                # EAFP dict update
    except KeyError:
        counts[word] = 1
print("EAFP counting:", counts, "(dict.get / defaultdict / Counter are shorter still)")
os.rmdir(tmp_dir)
