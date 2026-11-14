import bdb
import bisect
import contextlib
import inspect
import io
import logging
import os
import pdb
import pprint
import re
import subprocess
import sys
import tempfile
import textwrap
import traceback
import warnings
from collections import Counter
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True  # keep the demo from leaving __pycache__ behind

# 01. Debugging With pdb - Introduction
# ------------------------------------
# - Debugging is not "staring at code until it confesses". It is a loop:
#       REPRODUCE -> ISOLATE -> HYPOTHESIZE -> VERIFY -> FIX -> GUARD
#   and a debugger (pdb) is just one instrument for the VERIFY step: it lets
#   you stop a running program and ask it questions instead of guessing.
# - pdb is the debugger in the standard library - always available, even on a
#   remote server with no IDE. Learn its handful of commands once and you can
#   debug anywhere.
# - This file runs real debugger sessions NON-interactively (commands fed from
#   a string) so you can read genuine transcripts. In real life you type the
#   commands at the `(Pdb)` prompt.

print("# 01. Debugging With pdb - Introduction")
print("# ------------------------------------")

# 02. Demo Helpers (plumbing for this file, not part of the lesson)
# ------------------------------------
_TMP = tempfile.TemporaryDirectory(prefix="dbg_demo_")
TMP = Path(_TMP.name)


def scrub(text):
    """Make output deterministic: drop temp paths and memory addresses."""
    for p in sorted({str(TMP), str(TMP.resolve())}, key=len, reverse=True):
        text = text.replace(p + os.sep, "").replace(p, "<tmp>")
    text = re.sub(r"0x[0-9a-fA-F]{5,}", "0x...", text)
    text = re.sub(r'File "[^"]*[/\\]([^/\\"]+)"', r'File "\1"', text)  # basename only
    text = re.sub(r"(?m)^(\s*)/.*/([^/\s()]+\.py)\(", r"\1\2(", text)  # pdb `w` lines
    return "\n".join(ln.rstrip() for ln in text.splitlines()).strip("\n")


_INTERNAL = re.compile(r"^\s*(?:/\S*/)?(?:bdb|pdb)\.py\(\d+\)\w+\(\)$|^\s*<string>\(1\)<module>\(\)$")


def drop_internal_frames(text):
    """Hide pdb/bdb's own frames from `w` output (they are noise for learners)."""
    out, skip_arrow = [], False
    for ln in text.splitlines():
        if _INTERNAL.match(ln):
            skip_arrow = True
            continue
        if skip_arrow and ln.startswith("->"):
            skip_arrow = False
            continue
        skip_arrow = False
        out.append(ln)
    return "\n".join(out)


def echo_transcript(raw, commands):
    """Pdb run on a pipe does not echo input. Rebuild '(Pdb) cmd' lines: the text
    after the i-th '(Pdb) ' prompt is the answer to the i-th command."""
    chunks = raw.split("(Pdb) ")
    out = [chunks[0].rstrip("\n")]
    for cmd, chunk in zip(commands, chunks[1:]):
        out.append(f"(Pdb) {cmd}")
        if chunk.strip():
            out.append(chunk.rstrip("\n"))
    return "\n".join(out)


def emit(text, indent="  | ", limit=40):
    lines = scrub(drop_internal_frames(text)).splitlines()
    for ln in lines[:limit]:
        print(f"{indent}{ln}")
    if len(lines) > limit:
        print(f"{indent}... ({len(lines) - limit} more lines trimmed)")


def run_py(*args, cwd=TMP, stdin_text=None, env=None):
    """Run `python <args>` in a child with a clean PYTHON* environment."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    e.update(PYTHONDONTWRITEBYTECODE="1", HOME=str(TMP), NO_COLOR="1")  # HOME: no ~/.pdbrc
    e.update(env or {})
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          cwd=cwd, env=e, input=stdin_text, timeout=60)


def write(name, body):
    (TMP / name).write_text(textwrap.dedent(body).lstrip("\n"))
    return TMP / name


print("\n# 02. Demo Helpers (temp dir + clean child environment)")

# 03. Reading A Traceback Bottom-Up
# ------------------------------------
# - A traceback lists the CALL CHAIN, oldest call at the TOP, the line that
#   actually raised at the BOTTOM. Read it from the bottom:
#     1. LAST LINE:  ExceptionType: message      <- WHAT went wrong
#     2. the frame just above it                 <- WHERE it blew up
#     3. frames further up                       <- HOW we got there
#   Each frame is two lines: `File "x.py", line N, in function_name` and then
#   the source line. Python 3.11+ adds ^^^^ markers under the exact expression.
# - The bug is often NOT in the last frame: the last frame is where bad data
#   was DETECTED, not where it was CREATED. Walk up until the data looks wrong.
# - "During handling of the above exception, another exception occurred" or
#   "The above exception was the direct cause of..." means CHAINED exceptions:
#   read the last one first, then scroll up to see the original cause.


def read_price(record):
    return float(record["price"])


def total(records):
    return sum(read_price(r) for r in records)


def report():
    return total([{"price": "1.5"}, {"cost": "2"}])  # 2nd record has no "price"


class ConfigError(Exception):
    pass


def load_config():
    try:
        return report()
    except KeyError as exc:
        raise ConfigError("order data is malformed") from exc  # explicit chaining


print("\n# 03. Reading A Traceback Bottom-Up")
try:
    load_config()
except ConfigError:
    emit(traceback.format_exc(), limit=30)
print("  # Reading it: (1) bottom line = ConfigError, the final symptom.")
print("  # (2) Scroll UP past 'direct cause' to the ORIGINAL error: KeyError: 'price'.")
print("  # (3) Its frames (bottom-up): read_price blew up, called from the generator")
print("  #     inside total(), called from report() -> the data in report() is wrong.")

# 04. The Debugging Loop: Reproduce -> Isolate -> Hypothesize -> Verify
# ------------------------------------
# - REPRODUCE : get a failing run you can trigger on demand. No reproduction
#   = you cannot know whether you fixed it. Capture the exact input.
# - ISOLATE   : shrink the failing case until removing anything makes it pass.
#   The smaller the case, the fewer suspects.
# - HYPOTHESIZE: say a specific, TESTABLE sentence: "median is wrong for
#   even-length lists". Not "something is off with median".
# - VERIFY    : design an experiment that can prove the hypothesis WRONG.
#   Change one thing at a time. If the experiment surprises you, your mental
#   model is wrong - good, that is the bug-hunt working.
# - FIX + GUARD: fix the cause (not the symptom) and add a regression test.
# - Rubber-duck rule: explain the code line by line, aloud, to someone (or a
#   rubber duck). You usually spot the false assumption before finishing.


def median(xs):  # the buggy function under investigation
    xs = sorted(xs)
    return xs[len(xs) // 2]


def reference_median(xs):
    xs = sorted(xs)
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2


print("\n# 04. The Debugging Loop (worked example)")
cases = [[3], [1, 2, 3], [5, 1, 4, 2], [9, 7], [2, 2, 2], [4, 4], [1, 2, 3, 4, 5, 6]]
failing = [c for c in cases if median(c) != reference_median(c)]
print("1. REPRODUCE  failing inputs :", failing)

# ISOLATE: of everything that fails, keep the smallest (fewer suspects).
smallest = min(failing, key=len)
print("2. ISOLATE    smallest input  :", smallest,
      f"-> got {median(smallest)}, expected {reference_median(smallest)}")

print("3. HYPOTHESIZE: 'median is wrong for EVEN-length lists only'")
print("   lengths of failing inputs :", sorted({len(c) for c in failing}))
passing_even = [c for c in cases if len(c) % 2 == 0 and c not in failing]
print("   even-length case that passes anyway:", passing_even, "(equal values hide the bug)")
print("4. VERIFY     odd lengths all pass:",
      all(median(c) == reference_median(c) for c in cases if len(c) % 2))
print("   Cause: xs[len//2] picks ONE middle element; even lists need the mean of two.")
print("   Fix then add a regression test for [1, 2] -> 1.5 (see 01-Pytest-In-Depth.py).")

# 05. Print Debugging Done Well
# ------------------------------------
# - print() is a fine debugger when used with discipline:
#     * f"{x=}" prints name AND value: x=5   (3.8+, saves typing and mistakes)
#     * repr() / !r shows what a value REALLY is - invisible differences like
#       trailing spaces, '1' vs 1, None vs 'None', tabs, newlines
#     * pprint for nested dicts/lists so the structure is readable
#     * print to stderr (file=sys.stderr) so it does not mix with real output
#     * label every print; log BEFORE and AFTER the suspect line
# - Remove (or convert to logging) when done - a stray print breaks CLIs that
#   pipe stdout.

print("\n# 05. Print Debugging Done Well")
user_input = "admin "
stored = "admin"
print("naive   :", user_input, "==", stored, "->", user_input == stored)
print("with !r :", f"{user_input!r} vs {stored!r}", "<- the trailing space is now visible")
count = "3"
print(f"{count=}  {type(count)=}")
print(f"{count * 2=}", " <- '3'*2 is string repetition, not 6")
order = {"id": 7, "items": [{"sku": "A1", "qty": 2, "tags": ["new", "sale"]},
                            {"sku": "B2", "qty": 1, "tags": []}], "meta": {"source": "web"}}
print("plain  :", order)
print("pprint :")
pprint.pprint(order, width=50, sort_dicts=False)
print(f"{len(order['items'])=}  {order['items'][0]['qty']=}")
print("to stderr: print('debug...', file=sys.stderr)   # keeps stdout clean")

# 06. logging vs print For Debugging
# ------------------------------------
# - Use print for a 5-minute throwaway probe. Use logging when the output
#   should survive: you get levels, timestamps, function names, per-module
#   control, and you can turn DEBUG on/off WITHOUT editing code (see
#   06-Standard Library/07-Logging.py for the full tour).
# - logger.debug(...) lines can stay in the code forever at zero visible cost
#   (they are filtered out until you raise verbosity).
# - logger.exception("msg") inside `except` logs the message AND the traceback
#   - the right replacement for `except: pass`.
# - Use lazy %-style args: logger.debug("x=%s", x) - formatting only happens
#   if the record is actually emitted.

print("\n# 06. logging vs print")
log_buffer = io.StringIO()
logger = logging.getLogger("demo.checkout")
logger.setLevel(logging.DEBUG)
logger.propagate = False
handler = logging.StreamHandler(log_buffer)
handler.setFormatter(logging.Formatter("%(levelname)-7s %(funcName)s: %(message)s"))
logger.addHandler(handler)


def apply_coupon(price, code):
    logger.debug("start price=%r code=%r", price, code)
    try:
        rate = {"SAVE10": 0.10}[code]
    except KeyError:
        logger.exception("unknown coupon %r", code)  # message + traceback
        return price
    logger.info("coupon accepted rate=%s", rate)
    return price * (1 - rate)


apply_coupon(100, "SAVE10")
apply_coupon(100, "OOPS")
for ln in log_buffer.getvalue().splitlines():
    if not ln.startswith("  ") and "Traceback" not in ln:
        print("  |", ln)
print("  | ... (logger.exception also appended the full Traceback, trimmed here)")
logger.removeHandler(handler)

# 07. assert As Executable Documentation (and -O)
# ------------------------------------
# - `assert condition, "message"` states something that MUST be true at this
#   point: a precondition, an invariant, "this branch cannot happen". When
#   it is false you get an AssertionError at the FIRST wrong place instead of
#   a confusing failure ten calls later. It documents AND enforces.
# - Gotchas:
#     * `python -O` (and PYTHONOPTIMIZE) STRIPS every assert (and sets
#       __debug__ False). So NEVER use assert to validate user input, security
#       checks, or anything needed for correctness - raise real exceptions.
#     * assert side effects vanish under -O: `assert queue.pop()` loses the pop!
#     * `assert (cond, "msg")` asserts a non-empty TUPLE - always true.
#       Python warns about it (SyntaxWarning) - never write it.

print("\n# 07. assert And python -O")
script = write("assert_demo.py", '''
    print("__debug__ =", __debug__)
    assert 1 + 1 == 3, "arithmetic broke"
    print("reached the line after the assert")
''')
for flags in ([], ["-O"]):
    r = run_py(*flags, str(script))
    label = "python " + " ".join(flags + ["assert_demo.py"])
    print(f"  $ {label}   -> exit code {r.returncode}")
    emit(r.stdout + r.stderr, limit=8)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    compile("assert (False, 'never fires')", "<demo>", "exec")
print("assert on a tuple ->", caught[0].category.__name__ + ":", caught[0].message)

# 08. breakpoint() And PYTHONBREAKPOINT
# ------------------------------------
# - `breakpoint()` (3.7+) drops you into the debugger at that line. It calls
#   sys.breakpointhook(), which by default honours the env var
#   PYTHONBREAKPOINT:
#       unset                 -> import pdb; pdb.set_trace()
#       PYTHONBREAKPOINT=0    -> do NOTHING (disable every breakpoint() at once)
#       PYTHONBREAKPOINT=pdb.set_trace  -> same as default, explicit
#       PYTHONBREAKPOINT=pkg.mod.func   -> call YOUR function (e.g. ipdb.set_trace,
#                                          a remote debugger, a logger)
# - Real-world: set PYTHONBREAKPOINT=0 in CI/production so a forgotten
#   breakpoint() cannot hang a job waiting for keyboard input. Linters (ruff
#   T100, flake8-debugger) also flag it before commit.
# - We drive these with a child process: stdin is a string, so nothing hangs.

print("\n# 08. breakpoint() and PYTHONBREAKPOINT")
bp_script = write("bp_demo.py", '''
    value = 21
    print("before breakpoint")
    breakpoint()
    print("after breakpoint, value*2 =", value * 2)
''')
write("myhooks.py", '''
    def hook(*args, **kwargs):
        print(f"custom hook called with args={args} kwargs={kwargs}")
''')
print("  a) PYTHONBREAKPOINT=0 -> breakpoint() is a no-op:")
r = run_py(str(bp_script), env={"PYTHONBREAKPOINT": "0"})
emit(r.stdout + r.stderr, limit=6)
print("  b) default -> pdb opens; we feed commands 'p value' and 'c' (continue):")
r = run_py(str(bp_script), stdin_text="p value\nc\n")
emit(echo_transcript(r.stdout, ["p value", "c"]), limit=10)
print("  c) PYTHONBREAKPOINT=pdb.set_trace is the same as the default:")
r = run_py(str(bp_script), stdin_text="c\n", env={"PYTHONBREAKPOINT": "pdb.set_trace"})
emit(echo_transcript(r.stdout, ["c"]), limit=10)
print("  d) PYTHONBREAKPOINT=myhooks.hook -> your own function is called:")
r = run_py(str(bp_script), env={"PYTHONBREAKPOINT": "myhooks.hook"})
emit(r.stdout + r.stderr, limit=6)
print("  e) arguments pass through, and hooks can be swapped in code:")
r = run_py("-c", "import sys; sys.breakpointhook = lambda *a, **k: print('hooked', a, k); "
                 "breakpoint(1, 2, why='demo'); print('done')")
emit(r.stdout + r.stderr, limit=4)

# 09. Driving pdb Non-Interactively (the demo engine)
# ------------------------------------
# - pdb.Pdb(stdin=..., stdout=...) takes streams, so a string of commands can
#   play the role of a human. Pdb does not ECHO commands it reads from a
#   non-terminal, so EchoPdb below prints each command after the prompt,
#   producing a readable transcript. (readrc=False: ignore ~/.pdbrc so the
#   transcript is reproducible.)
# - Entry points you will use in real life:
#       breakpoint()                  stop here (inside your code)
#       python -m pdb script.py       start under the debugger, stop at line 1
#       python -m pdb -c continue s.py run until a crash, then post-mortem
#       pytest --pdb                  drop into pdb on each test failure
#       pdb.post_mortem(tb) / pdb.pm()  inspect AFTER an exception happened


class EchoPdb(pdb.Pdb):
    def precmd(self, line):
        if line != "EOF" and not line.startswith("_pdbcmd"):  # skip internal plumbing
            self.stdout.write(line + "\n")  # show the "typed" command
        return super().precmd(line)


SHOP = write("shop.py", '''
    def apply_discount(price, percent):
        discount = price * percent / 100
        return price - discount

    def checkout(items):
        total = 0
        for i, (name, price) in enumerate(items):
            label = name.upper()
            total += apply_discount(price, 10)
        tax = total * 0.2
        return round(total + tax, 2)

    def parse_order(line):
        name, qty, price = line.split(",")
        return name, int(qty), float(price)

    def load_orders(lines):
        orders = []
        for n, line in enumerate(lines, 1):
            orders.append(parse_order(line))
        return orders
''')
sys.path.insert(0, str(TMP))
import shop  # noqa: E402  (imported from the temp project)

ITEMS = [("pen", 10.0), ("book", 50.0), ("bag", 100.0)]


def lineno(snippet):
    """Line number of the first line in shop.py containing snippet."""
    for n, text in enumerate(SHOP.read_text().splitlines(), 1):
        if snippet in text:
            return n
    raise ValueError(snippet)


def session(title, func, args, commands):
    """Run func(*args) under EchoPdb fed with `commands`; print the transcript."""
    buf = io.StringIO()
    bdb.Breakpoint.clearBreakpoints()  # fresh breakpoint numbering per session
    dbg = EchoPdb(stdin=io.StringIO("\n".join(commands) + "\n"), stdout=buf,
                  nosigint=True, readrc=False)
    with contextlib.redirect_stdout(buf):  # program output joins the transcript
        result = dbg.runcall(func, *args)
    print(f"\n  >>> {title}")
    emit(buf.getvalue(), limit=80)
    return result


print("\n# 09. Driving pdb Non-Interactively")
print("Sample program: shop.py with apply_discount(), checkout(), parse_order(), load_orders()")

# 10. Core Commands: l, n, s, p, pp, a, w, u, d, r, c
# ------------------------------------
# - h / h cmd   help (list of commands / help for one)
# - l           list 11 lines around the current line ( -> marks the NEXT line
#               to run). `l` again continues; `ll` lists the whole function.
# - n (next)    run the current line, STEP OVER function calls.
# - s (step)    run the current line, STEP INTO a call if there is one.
# - r (return)  keep running until the current function returns.
# - c (continue) run until the next breakpoint (or the end).
# - p expr / pp expr  print / pretty-print any expression (repr()).
# - a           args of the current function.
# - w (where)   the call stack; `>` marks the frame you are inspecting.
# - u / d       move UP / DOWN the stack to inspect callers' variables.
# - q           quit the debugger (kills the program).
# - Pressing ENTER repeats the last command (handy for `n`).
# - Gotcha: a variable named like a command (n, c, s, l, p...) would be run as
#   that command - prefix expressions with `!` or use `p n`.

print("\n# 10. Core Commands")
session("l, n, s, a, w, u, d, r, c on checkout()", shop.checkout, (ITEMS,), [
    "l",                    # where am I?
    "n", "n",               # run `total = 0`, then enter the loop
    "n",                    # run `label = ...`
    "p name, price",        # inspect variables
    "pp items",
    "s",                    # step INTO apply_discount
    "a",                    # its arguments
    "ll",                   # long list: the whole current function
    "p price * percent / 100",
    "w",                    # call stack (checkout -> apply_discount)
    "u",                    # up one frame: now we are inside checkout
    "p total",
    "d",                    # back down
    "r",                    # run until apply_discount returns
    "c",                    # let the program finish
])

# 11. Breakpoints: b, cl, tbreak, conditions, commands
# ------------------------------------
# - b func / b file.py:LINE / b LINE   set a breakpoint
# - b                                  list them (hit counts included)
# - b LINE, expr                       CONDITIONAL breakpoint: stop only when
#                                      expr is true - the loop-with-1000-items
#                                      problem solved ("stop when i == 700")
# - condition N expr                   add/replace the condition of bp N
# - tbreak ...                         temporary: deleted after the first hit
# - cl N  / cl                         clear one / all breakpoints
# - disable N / enable N               keep it but switch it off
# - ignore N count                     skip the next `count` hits
# - commands N ... end                 run commands automatically when bp N
#                                      is hit; `silent` hides the stop message,
#                                      `c` as the last command = a "logpoint"
#                                      (print something and keep going).

print("\n# 11. Breakpoints")
LOOP_BODY = lineno("label = name.upper()")
ACCUMULATE = lineno("total += apply_discount")
TAX = lineno("tax = total")
session("b func, b file:line, list, clear, continue", shop.checkout, (ITEMS,), [
    "b apply_discount",
    f"b shop.py:{TAX}",
    "b",                    # list: note numbers 1 and 2
    "c",                    # stops at apply_discount (bp 1)
    "cl 1",                 # clear bp 1
    "c",                    # next stop: the tax line (bp 2)
    "p total",
    "c",
])
session("conditional breakpoint: stop in the loop only when i == 2",
        shop.checkout, (ITEMS,), [
            f"b shop.py:{LOOP_BODY}, i == 2",
            "c",
            "p i, name",    # we are on the 3rd item
            "c",
        ])
session("condition command + tbreak (temporary breakpoint)",
        shop.checkout, (ITEMS,), [
            f"b shop.py:{LOOP_BODY}",
            "condition 1 name == 'book'",   # add a condition afterwards
            f"tbreak shop.py:{TAX}",         # temporary: deleted after one hit
            "c",
            "p name",
            "c",            # 'bag' does not match, so the tbreak fires next
            "b",            # the tbreak is gone; bp 1 (with its condition) remains
            "c",
        ])
session("commands: a logpoint that prints and keeps going",
        shop.checkout, (ITEMS,), [
            f"b shop.py:{ACCUMULATE}",
            "commands 1",
            "silent",
            "print(f'  [logpoint] i={i} name={name!r} total={total}')",
            "c",
            "c",
        ])

# 12. Evaluating, Display, until, jump
# ------------------------------------
# - !statement      run ANY Python statement in the current frame, including
#                   assignments: `!total = 999` changes the live program.
#                   (Great for testing a fix without editing the file.)
# - display expr    re-print expr every time execution stops (and it changed);
#                   undisplay N removes it. A cheap "watch expression".
# - until           like `n`, but at the bottom of a loop it does NOT jump
#                   back: it runs until the loop is finished. `until LINE`
#                   runs until that line.
# - j LINE (jump)   change which line runs next (only in the innermost frame).
#                   Skip a line, or re-run one after patching a variable.
# - interact        open a full Python REPL with the current frame's variables.
# - whatis expr     type of the expression; retval shows the last return value;
#                   source obj prints the source code of any object.
# - restart / run   restart the program under the debugger.

print("\n# 12. Evaluate, display, until, jump")
session("display, !assignment, until", shop.checkout, (ITEMS,), [
    "n",                    # run `total = 0` so that `total` exists
    "display total",        # shown now, and again whenever it changes
    f"tbreak shop.py:{ACCUMULATE}",
    "c",
    "!total = 1000",        # modify live state (no ! needed here, but safe)
    "n",
    "n",
    f"until {TAX}",         # finish the loop in one go
    "p total",
    "whatis total",
    "undisplay total",
    "c",
])
session("jump: go BACK, patch a variable, re-run a line", shop.checkout, (ITEMS,), [
    f"tbreak shop.py:{TAX}",
    "c",
    "n",                    # run the tax line; now on the `return` line
    "p total, tax",
    f"j {TAX}",             # jump back to the tax line...
    "!total = 200.0",       # ...patch the input (assign AFTER the jump)...
    "n",                    # ...and run the line again
    "p total, tax",
    "c",
])

# 13. Post-Mortem Debugging
# ------------------------------------
# - Post-mortem = inspect the program AFTER it crashed, with all frames and
#   variables still alive in the traceback. No need to guess where to put a
#   breakpoint beforehand.
#       try: ... except Exception: pdb.post_mortem()     in code
#       python -m pdb -c continue script.py              crash -> post-mortem
#       pytest --pdb                                     on test failure
#       python -i script.py   then  >>> import pdb; pdb.pm()
#         (sys.last_traceback / sys.last_exc holds the last uncaught error
#         in an INTERACTIVE session only - scripts do not set it)
# - Inside post-mortem: `w` to see the stack, `u` to climb to the caller whose
#   data is wrong, `p var` to inspect. You cannot "continue" a dead program.

print("\n# 13. Post-Mortem Debugging")
bad_lines = ["pen,2,1.5", "book,x,9.0", "bag,1,30"]
try:
    shop.load_orders(bad_lines)
except ValueError as exc:
    tb = exc.__traceback__
    buf = io.StringIO()
    dbg = EchoPdb(stdin=io.StringIO("w\np line\nu\np line\np n\nq\n"), stdout=buf,
                  nosigint=True, readrc=False)
    dbg.reset()
    dbg.interaction(None, tb)  # exactly what pdb.post_mortem(tb) does
    print("  >>> in-process post-mortem on:", repr(exc))
    emit(buf.getvalue(), limit=30)
print("  # Top frame = parse_order (split ok, int('x') failed). `u` climbs to")
print("  # load_orders: n tells us it was line 2 of the input -> bad DATA at line 2.")

crash = write("crash.py", '''
    import shop
    print("starting")
    shop.load_orders(["pen,2,1.5", "book,x,9.0"])
''')
pm_cmds = ["w", "u", "p line", "q"]
r = run_py("-m", "pdb", "-c", "continue", str(crash), stdin_text="\n".join(pm_cmds) + "\n")
out = r.stdout[:r.stdout.find("will be restarted") + len("will be restarted")]
print("\n  >>> python -m pdb -c continue crash.py")
emit(echo_transcript(drop_internal_frames(out), pm_cmds), limit=24)
print("  # `python -m pdb` entered post-mortem automatically at the uncaught error.")

# pdb.pm() = post_mortem(sys.last_traceback). The interactive REPL fills that in
# after an uncaught error; we fill it in by hand to show the same effect.
try:
    shop.load_orders(["book,x,9.0"])
except ValueError as exc:
    sys.last_traceback, sys.last_exc = exc.__traceback__, exc
pm_out = io.StringIO()
with mock.patch.dict(os.environ, {"HOME": str(TMP)}), \
        mock.patch.object(sys, "stdin", io.StringIO("p line\nq\n")), \
        contextlib.redirect_stdout(pm_out):
    pdb.pm()
del sys.last_traceback, sys.last_exc
print("\n  >>> pdb.pm() after an error in the REPL (commands sent: p line, q)")
emit(echo_transcript(pm_out.getvalue(), ["p line", "q"]), limit=10)

# 14. The traceback Module: print_exc, format_exc, extract_tb
# ------------------------------------
# - traceback.print_exc()   print the CURRENT exception's traceback (default to
#   stderr; pass file=sys.stdout to redirect). Use inside `except`.
# - traceback.format_exc()  same but RETURNS a string - put it in logs,
#   emails, error-tracking payloads, test failure messages.
# - traceback.format_exception(exc)  format a given exception (3.10+ takes just
#   the exception object); TracebackException is the object-oriented version.
# - traceback.extract_tb(tb) -> list of FrameSummary(filename, lineno, name,
#   line): inspect the stack programmatically (find the deepest frame in YOUR
#   code, group errors by location...).
# - traceback.print_stack() prints the CURRENT call stack (no exception
#   needed): "how did I get here?".
# - exc.add_note("...") (3.11+) attaches context that shows in the traceback.
# - `raise NewError(...) from exc` keeps the cause; `from None` hides it.

print("\n# 14. The traceback Module")
try:
    shop.load_orders(["book,x,9.0"])
except ValueError as exc:
    exc.add_note("while loading orders.csv")
    frames = traceback.extract_tb(exc.__traceback__)
    print("extract_tb ->", [(f.name, f.line) for f in frames])
    print("deepest frame    :", frames[-1].name, "line", frames[-1].lineno)
    last = "".join(traceback.format_exception_only(exc))
    print("format_exception_only:", last.strip().replace("\n", " | "))
    buf = io.StringIO()
    traceback.print_exc(file=buf, limit=1)  # limit=1: only the newest frame
    emit(buf.getvalue(), limit=8)


def where_am_i():
    return [f.name for f in traceback.extract_stack()[-3:]]  # no exception needed


def feature_y():
    return where_am_i()


print("extract_stack    :", feature_y(), "(oldest -> newest call)")

# 15. faulthandler: Crashes And Hangs
# ------------------------------------
# - Normal tracebacks need Python to be alive. If the interpreter DIES (segfault
#   in a C extension, abort, fatal error) or HANGS (deadlock, infinite loop),
#   you get nothing - faulthandler fixes that.
# - faulthandler.enable()          on fatal signals (SIGSEGV, SIGFPE, SIGABRT,
#                                  SIGBUS, SIGILL) dump every thread's Python
#                                  stack to stderr before dying:
#                                    Fatal Python error: Segmentation fault
#                                    Current thread 0x... (most recent call first):
#                                      File "app.py", line 9 in crunch
#   Turn it on without code changes: `python -X faulthandler app.py` or
#   PYTHONFAULTHANDLER=1 (also on automatically in -X dev mode and pytest).
# - faulthandler.dump_traceback()  print all thread stacks NOW (works on a
#   live process: "where is every thread right now?").
# - faulthandler.dump_traceback_later(timeout, repeat=False, exit=False)
#   a WATCHDOG: if the program is still running after `timeout` seconds, dump
#   stacks (exit=True also kills it). Cancel with cancel_dump_traceback_later()
#   when the risky section finishes - the classic way to find a hang.
# - faulthandler.register(signal.SIGUSR1) (Unix): `kill -USR1 <pid>` makes a
#   stuck production process print its stacks.
# - (A real segfault demo is omitted on purpose: it makes the OS write a crash
#   report outside this folder.)

print("\n# 15. faulthandler")
hang = write("hang_demo.py", '''
    import faulthandler, os, signal, sys, time

    def slow_step():
        time.sleep(0.6)               # pretend this is a stuck call

    def pipeline():
        slow_step()

    faulthandler.dump_traceback_later(0.2, exit=False, file=sys.stdout)
    pipeline()
    faulthandler.cancel_dump_traceback_later()
    print("pipeline finished; watchdog cancelled")

    if hasattr(faulthandler, "register"):                 # Unix only
        faulthandler.register(signal.SIGUSR1, file=sys.stdout)
        print("--- on-demand dump via SIGUSR1 ---")
        os.kill(os.getpid(), signal.SIGUSR1)
        time.sleep(0.1)
    print("is_enabled:", faulthandler.is_enabled())
''')
r = run_py("-u", str(hang))  # -u: unbuffered, so prints and dumps interleave in order
emit(r.stdout + r.stderr, limit=24)
r = run_py("-X", "faulthandler", "-c", "import faulthandler; print('-X faulthandler ->', faulthandler.is_enabled())")
emit(r.stdout, limit=3)
r = run_py("-c", "import faulthandler; print('PYTHONFAULTHANDLER=1 ->', faulthandler.is_enabled())",
           env={"PYTHONFAULTHANDLER": "1"})
emit(r.stdout, limit=3)

# 16. sys.settrace And sys.setprofile: A Tiny Tracer
# ------------------------------------
# - sys.settrace(fn) installs a function Python calls on every `call`,
#   `line`, `return` and `exception` event. THIS is how pdb, coverage.py and
#   many profilers work. Your trace function receives (frame, event, arg) and
#   returns itself (or another function) to keep tracing that frame.
# - sys.setprofile(fn) is lighter: only call/return events (plus C calls) -
#   perfect for "which functions ran, how often".
# - Python 3.12 adds sys.monitoring (PEP 669), a much lower-overhead API used
#   by modern debuggers/coverage - mentioned for reference only.
# - Always sys.settrace(None) in a finally block, and filter by file/function:
#   tracing everything is slow and noisy.


def square(x):
    return x * x


def sum_of_squares(n):
    result = 0
    for i in range(n):
        result += square(i)
    return result


print("\n# 16. sys.settrace and sys.setprofile")
depth = 0
trace_lines = []
WATCH = {"sum_of_squares", "square"}


def tracer(frame, event, arg):
    global depth
    if frame.f_code.co_name not in WATCH or frame.f_code.co_filename != __file__:
        return None
    if event == "call":
        trace_lines.append("  " * depth + f"CALL   {frame.f_code.co_name}({frame.f_locals})")
        depth += 1
    elif event == "line":
        src = inspect.getsourcelines(frame.f_code)[0][frame.f_lineno - frame.f_code.co_firstlineno]
        trace_lines.append("  " * depth + f"line   {src.strip()}")
    elif event == "return":
        depth -= 1
        trace_lines.append("  " * depth + f"RETURN {frame.f_code.co_name} -> {arg!r}")
    return tracer


sys.settrace(tracer)
try:
    sum_of_squares(2)
finally:
    sys.settrace(None)
for ln in trace_lines[:14]:
    print("  |", ln)
print(f"  | ... ({len(trace_lines)} trace events total)")

calls = Counter()


def profiler(frame, event, arg):
    if event == "call" and frame.f_code.co_filename == __file__:
        calls[frame.f_code.co_name] += 1


sys.setprofile(profiler)
try:
    sum_of_squares(5)
finally:
    sys.setprofile(None)
print("setprofile call counts:", dict(calls))

# 17. inspect.stack(): Who Called Me?
# ------------------------------------
# - inspect.stack() returns FrameInfo records for the whole call stack;
#   [0] is the current function, [1] its caller, and so on. Useful for logging
#   helpers, deprecation warnings, "this was called from X" diagnostics.
# - It is SLOW (it reads source files for each frame). For hot paths use
#   inspect.stack(0) (no source context) or sys._getframe(1) (cheap, but
#   CPython-specific) / inspect.currentframe().f_back.
# - logging already does this for you: use %(funcName)s %(lineno)d in the
#   format string (see 07-Logging.py).
# - Never keep frame objects around: they hold references to every local
#   variable and cause memory leaks/cycles.


def whoami():
    me = inspect.stack(0)[0]
    caller = inspect.stack(1)[1]  # 1 line of source context
    return me.function, caller.function, caller.code_context[0].strip()


def feature_x():
    return whoami()


print("\n# 17. inspect.stack()")
print("whoami() called from feature_x ->", feature_x())
print("sys._getframe(0).f_code.co_name ->", sys._getframe(0).f_code.co_name, "(module level)")
f = inspect.currentframe()
print("inspect.getframeinfo(f).function ->", inspect.getframeinfo(f).function)
del f  # do not hold frames

# 18. Interpreter Flags: -W error, -X dev, -X importtime
# ------------------------------------
# - Warnings are bugs waiting to happen (deprecated API, unclosed files,
#   suspicious comparisons) that scroll past unnoticed.
#   -W error                 turn EVERY warning into an exception: you get a
#                            traceback at the exact line that warned.
#   -W error::DeprecationWarning   only that category.
#   PYTHONWARNINGS=error     same via env; pytest -W error also works.
# - -X dev (Development Mode) turns on extra checks: ResourceWarning (unclosed
#   files/sockets) + DeprecationWarning shown, faulthandler enabled, asyncio
#   debug mode, more memory-allocator checks, stricter str/bytes errors.
#   Slower - use it in tests and while debugging, not in production.
# - -X importtime  prints how long every import took to stderr (find a slow
#   startup; output is long, so only referenced here): python -X importtime app.py
# - -X tracemalloc / PYTHONTRACEMALLOC  record where memory was allocated.
# - -X utf8, -v (verbose imports: see which file an import really loaded).

print("\n# 18. Interpreter Flags")
warn_code = ("import warnings; warnings.warn('old_api() is deprecated', DeprecationWarning); "
             "print('continued normally')")
print("  a) normal run (warning goes to stderr, program continues):")
r = run_py("-c", warn_code)
emit(r.stdout + r.stderr, limit=4)
print("  b) -W error: the warning becomes an exception:")
r = run_py("-W", "error", "-c", warn_code)
print(f"     exit code {r.returncode}")
emit(r.stderr, limit=6)
leak = write("leak.py", '''
    f = open("leak.py")
    del f                       # file never closed explicitly
    print("done")
''')
print("  c) -X dev reveals an unclosed file (silent in a normal run):")
r = run_py(str(leak))
print("     normal run stderr is empty:", r.stderr == "")
r = run_py("-X", "dev", str(leak))
lines = [ln for ln in scrub(r.stderr).splitlines() if "ResourceWarning" in ln]
for ln in lines[:1]:
    print("    |", ln)
print("    | (dev mode also adds 'Object allocated at...' showing WHERE it was opened)")
r = run_py("-X", "dev", "-c", "import sys; print('dev_mode:', sys.flags.dev_mode)")
emit(r.stdout, limit=2)

# 19. IDE Debuggers (reference: VS Code and PyCharm)
# ------------------------------------
# - Same ideas as pdb, with a UI. Learn these features, they save hours:
#     * Breakpoint            click the gutter, F5/Shift+F9 to run/debug.
#     * Conditional breakpoint  right-click -> expression (i == 700) or
#                             hit count (stop on the 50th hit).
#     * Logpoint (VS Code)    prints "x={x}" WITHOUT stopping or editing code
#                             (PyCharm: "Evaluate and log" on a breakpoint).
#     * Watch expressions     keep an expression visible and re-evaluated at
#                             every stop (like pdb `display`).
#     * Call stack panel      click a frame to inspect its locals (pdb u/d).
#     * Debug Console / Evaluate  run code in the paused frame (pdb !stmt).
#     * Step Over / Into / Out = n / s / r.
#     * Exception breakpoints "Break on raised/uncaught exceptions": stops at
#                             the line that raised, even if caught later.
#     * "Just My Code"        skips library frames when stepping.
#     * Attach to process / remote debugging (debugpy) for servers, Docker.
# - VS Code launch.json minimal entry:
#       {"name": "Debug file", "type": "debugpy", "request": "launch",
#        "program": "${file}", "console": "integratedTerminal"}

print("\n# 19. IDE Debuggers (reference)")
for ide_feature, pdb_equiv in [
    ("Gutter breakpoint", "b file:line"),
    ("Conditional breakpoint", "b file:line, expr"),
    ("Logpoint", "b + commands (print ... c)"),
    ("Watch expression", "display expr"),
    ("Call stack panel", "w, u, d"),
    ("Debug console", "!stmt, p expr, interact"),
    ("Step over/into/out", "n / s / r"),
    ("Break on exception", "post-mortem: python -m pdb -c continue"),
]:
    print(f"  {ide_feature:<24} <-> {pdb_equiv}")

# 20. A Catalogue Of Classic Bugs (reproduction + diagnosis)
# ------------------------------------
# - Most bugs are old friends. Recognising the symptom shortens the hunt.

print("\n# 20. Classic Bug Catalogue")

# 20a. Mutable default argument -------------------------------------------
print("\n-- a) Mutable default argument")


def add_tag(tag, tags=[]):  # the default list is created ONCE, at def time
    tags.append(tag)
    return tags


print("add_tag('a') ->", add_tag("a"))
print("add_tag('b') ->", add_tag("b"), "  <- 'a' is still there!")
print("diagnose: add_tag.__defaults__ ->", add_tag.__defaults__, "(the shared list)")
print("fix: def add_tag(tag, tags=None): tags = [] if tags is None else tags")

# 20b. Late-binding closure ---------------------------------------------------
print("\n-- b) Late-binding closure in a loop")
makers = [lambda: i for i in range(3)]
print("[f() for f in makers] ->", [f() for f in makers], "  <- expected [0, 1, 2]")
print("diagnose: every lambda shares ONE cell ->", makers[0].__closure__[0].cell_contents,
      "(the final i, looked up at CALL time)")
fixed = [lambda i=i: i for i in range(3)]
print("fix: bind now with a default arg (lambda i=i: i) ->", [f() for f in fixed])

# 20c. Off-by-one --------------------------------------------------------------
print("\n-- c) Off-by-one (fencepost)")
data = [10, 20, 30, 40]
print("sum via range(1, len(data)) ->", sum(data[i] for i in range(1, len(data))),
      "<- skipped index 0; expected", sum(data))
print("data[:2] ->", data[:2], "(end index excluded)  | data[1:3] ->", data[1:3])
print("range(5) has", len(range(5)), "items, last is", range(5)[-1], "| range(1, 5) has", len(range(1, 5)))
print("diagnose: test the BOUNDARIES: empty, 1 item, first, last, n+1.")

# 20d. Shadowed builtin ----------------------------------------------------------
print("\n-- d) Shadowed builtin")


def shadow_demo():
    list = [1, 2]  # noqa: A001 - rebinding the builtin name inside this scope
    try:
        return list("abc")
    except TypeError as exc:
        return f"TypeError: {exc}  (type of 'list' here: {type(list).__name__})"


print(shadow_demo())
print("diagnose: print(type(name)); `del name` restores the builtin;")
print("          linters flag it (ruff A001/A002). Common victims: list, dict, id, type, input, max, sum, file, str.")

# 20e. Modifying a list while iterating -----------------------------------------
print("\n-- e) Modifying a list while iterating")
nums = [1, 2, 2, 3, 4, 4, 5]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)  # shifts indexes; the iterator skips the next element
print("remove evens in-place ->", nums, "  <- a 2 and a 4 survived")
print("fix: build a new list ->", [n for n in [1, 2, 2, 3, 4, 4, 5] if n % 2], "(or iterate over a copy: nums[:])")

# 20f. is vs == ---------------------------------------------------------------------
print("\n-- f) `is` vs `==`")
a, b = int("1000"), int("1000")
print("a == b ->", a == b, "| a is b ->", a is b, " (same value, different objects)")
print("small ints cached: int('7') is int('7') ->", int("7") is int("7"), "(implementation detail! never rely on it)")
print("[] == [] ->", [] == [], "| [] is [] ->", [] is [])
print("rule: `is` only for singletons: `x is None`, `x is True`; everything else `==`.")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    compile("x = 5\nif x is 5: pass", "<demo>", "exec")
print("compile-time hint ->", caught[0].category.__name__ + ":", caught[0].message)

# 20g. Integer division and rounding -------------------------------------------
print("\n-- g) Division and rounding surprises")
print("7 / 2 =", 7 / 2, "| 7 // 2 =", 7 // 2, "| -7 // 2 =", -7 // 2, "(floors toward -inf)",
      "| int(-7 / 2) =", int(-7 / 2), "(truncates)")
print("round(2.5) =", round(2.5), "| round(3.5) =", round(3.5), "(banker's rounding: ties go to even)")
print("0.1 + 0.2 =", 0.1 + 0.2, "<- use math.isclose / decimal for comparisons and money")

# 20h. Swallowed exception ----------------------------------------------------------
print("\n-- h) Swallowed exception")


def parse_age(text):
    try:
        return int(text)
    except Exception:  # too broad, and silent
        return 0


print("parse_age('42') ->", parse_age("42"), "| parse_age('forty') ->", parse_age("forty"),
      "| parse_age(None) ->", parse_age(None), " <- three different failures look like 'age 0'")
print("diagnose: grep for `except:` / `except Exception: pass`; temporarily replace the")
print("          handler body with `raise` to surface the real traceback.")
print("fix: catch the NARROW type (ValueError), log with logger.exception(), or re-raise.")

# 20i. Wrong cwd / relative path ----------------------------------------------------
print("\n-- i) Relative path depends on the CURRENT DIRECTORY, not the script location")
(TMP / "data.txt").write_text("42\n")
write("reader_bad.py", 'print(open("data.txt").read().strip())\n')
write("reader_good.py", '''
    from pathlib import Path
    print((Path(__file__).resolve().parent / "data.txt").read_text().strip())
''')
other = TMP / "elsewhere"
other.mkdir()
for script_name in ("reader_bad.py", "reader_good.py"):
    for where, cwd in (("same dir", TMP), ("other dir", other)):
        r = run_py(str(TMP / script_name), cwd=cwd)
        out = (r.stdout.strip() or r.stderr.strip().splitlines()[-1])
        print(f"  {script_name:<15} run from {where:<9} -> {scrub(out)}")
print("diagnose: print(os.getcwd()) at the failing line; fix: anchor paths to __file__.")

# 20j. Circular import -----------------------------------------------------------------
print("\n-- j) Circular import")
write("circ_a.py", "from circ_b import beta\nalpha = 'A'\n")
write("circ_b.py", "from circ_a import alpha\nbeta = 'B'\n")
r = run_py("-c", "import circ_a")
emit(r.stderr.splitlines()[-1], limit=3)
print("diagnose: read the chain in the traceback: a imports b imports a (before a finished).")
print("fix: move shared code to a third module, import the MODULE not the name and use it")
print("     later (`import circ_a` then circ_a.alpha at call time), or import inside the function.")

# 21. Binary Search The Bug (bisection)
# ------------------------------------
# - When something WORKED in the past and is broken now, you do not need to
#   read every change: if "good ... good BAD BAD BAD" is a clean split,
#   halving finds the first bad one in log2(N) steps (1000 versions -> 10).
# - The idea applies everywhere:
#     * versions/commits  -> `git bisect`
#     * input data        -> halve the failing file/list until minimal
#     * code              -> comment out half the function/pipeline
#     * config / plugins  -> disable half, retest
# - Requirement: a reliable yes/no test (a script, a pytest command) and a
#   known-good plus known-bad starting point.
#       git bisect start
#       git bisect bad                      # current commit is broken
#       git bisect good v1.4.0              # this tag worked
#       git bisect run pytest -x tests/test_orders.py   # automate the checks
#       git bisect reset                    # return to where you were

print("\n# 21. Binary Search The Bug")
versions = [f"v1.{n}" for n in range(40)]
FIRST_BAD = "v1.27"
probes = []


def is_bad(version):
    probes.append(version)  # stands in for: check out, build, run the test
    return versions.index(version) >= versions.index(FIRST_BAD)


lo, hi = 0, len(versions) - 1  # invariant: versions[hi] is bad, answer is in [lo, hi]
while lo < hi:
    mid = (lo + hi) // 2
    if is_bad(versions[mid]):
        hi = mid
    else:
        lo = mid + 1
print(f"{len(versions)} versions, first bad = {versions[lo]} found in {len(probes)} probes")
print("probe order:", probes)

probes.clear()
idx = bisect.bisect_left(range(len(versions)), True, key=lambda i: is_bad(versions[i]))
print(f"stdlib bisect_left(key=...) -> {versions[idx]} in {len(probes)} probes "
      f"(linear scan would take up to {len(versions)})")

# Same trick on DATA: find the one poison record in a file that makes a parser crash.
records = [f"id={n}" for n in range(1, 101)]
records[63] = "id=???"  # the poison record


def parse_all(chunk):
    for r in chunk:
        int(r.split("=")[1])  # raises ValueError on the bad one


def fails(chunk):
    try:
        parse_all(chunk)
        return False
    except ValueError:
        return True


chunk, steps = records, 0
while len(chunk) > 1:
    half = len(chunk) // 2
    chunk = chunk[:half] if fails(chunk[:half]) else chunk[half:]
    steps += 1
print(f"poison record found by halving the data: {chunk[0]!r} in {steps} rounds (of 100 records)")

# 22. A Debugging Checklist And Recap
# ------------------------------------
# - 1. Read the error message and the LAST frame of the traceback, then walk up.
# - 2. Reproduce reliably; shrink the input; write it down as a failing test.
# - 3. State a hypothesis you can falsify; change ONE thing per experiment.
# - 4. Cheapest tool first: f"{x=}" / assert -> logging -> breakpoint() / pdb ->
#      post-mortem -> faulthandler (crash/hang) -> settrace (who runs what).
# - 5. Suspect your assumptions before the library: print types and reprs.
# - 6. Check recent changes: git diff, git bisect.
# - 7. After the fix: add a regression test, remove debug prints/breakpoints,
#      and ask "where else could this same mistake hide?"
# - Take a break: a fresh mind finds in 5 minutes what a tired one misses for an hour.

print("\n# 22. Recap")
print("reproduce -> isolate -> hypothesize -> verify -> fix -> add a regression test")

sys.path.remove(str(TMP))
_TMP.cleanup()
