import atexit
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time

# 01. subprocess and signal - Introduction
# ------------------------------------
# - A "process" is a running program. Your Python script is one. With the
#   subprocess module your script can START other programs (including another
#   Python), wait for them, feed them input and read what they print.
# - A "signal" is a tiny message the operating system (or another process)
#   sends to a process: "please stop", "the timer you asked for rang", etc.
# - Together they answer: how do I run something else safely, and how do I
#   shut down cleanly when someone tells me to stop?
# - 03-Os-And-Sys.py only shows a taste of subprocess.run(). This file goes deep.
# - Everything below only runs sys.executable (this very Python) or harmless
#   built-ins, so it is safe to run anywhere. No files are left behind.

print("# 01. subprocess and signal - Introduction")
print("# ------------------------------------")

PY = sys.executable  # path of the Python running us; the safest "other program"
IS_POSIX = os.name == "posix"  # signals like SIGALRM / kill semantics are POSIX only


def py(code):
    """Build the argument list to run a snippet of Python in a child process."""
    return [PY, "-c", code]


# 02. subprocess.run() - the One Function You Need 90% of the Time
# ------------------------------------
# - run() starts the program, WAITS until it finishes, and returns a
#   CompletedProcess object holding everything that happened.
# - capture_output=True -> collect stdout and stderr instead of letting them
#   spill into your own terminal.
# - text=True -> get str back instead of raw bytes (it decodes for you).
print("\n# 02. subprocess.run()")
result = subprocess.run(py("print('hello from the child')"), capture_output=True, text=True)
print("stdout     :", repr(result.stdout))
print("stderr     :", repr(result.stderr))
print("returncode :", result.returncode)
print("args       :", result.args[1:], "(first item is our Python path)")
print("type       :", type(result).__name__)

# 03. CompletedProcess Fields
# ------------------------------------
# - .args        -> the command you ran
# - .returncode  -> 0 means success by convention; anything else = failure
# - .stdout      -> captured output (None if you did not capture it)
# - .stderr      -> captured error output (None if you did not capture it)
# - .check_returncode() -> raises CalledProcessError if returncode != 0
print("\n# 03. CompletedProcess fields: a failing child")
result = subprocess.run(
    py("import sys; print('partial work'); print('bad thing', file=sys.stderr); sys.exit(3)"),
    capture_output=True,
    text=True,
)
print("returncode:", result.returncode)
print("stdout    :", repr(result.stdout))
print("stderr    :", repr(result.stderr))
print("NOTE: run() does NOT raise on failure by default - you must look at returncode.")

# 04. check=True - Turn Failure into an Exception
# ------------------------------------
# - Forgetting to check the return code is the most common subprocess bug:
#   the script carries on as if everything worked.
# - check=True raises CalledProcessError when the exit code is not 0, so
#   failures cannot be silently ignored.
print("\n# 04. check=True and CalledProcessError")
try:
    subprocess.run(py("import sys; print('oops', file=sys.stderr); sys.exit(7)"),
                   capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as err:
    print("caught CalledProcessError")
    print("  returncode:", err.returncode)
    print("  stderr    :", repr(err.stderr))  # needs capture_output to be filled in
    print("  cmd[0]    :", err.cmd[0] == PY)

# 05. timeout= and TimeoutExpired
# ------------------------------------
# - Without a timeout a hung child hangs YOU forever. In real programs, ALWAYS
#   set one when the child is not 100% under your control.
# - On timeout, run() kills the child for you and raises TimeoutExpired.
print("\n# 05. timeout= and TimeoutExpired")
start = time.monotonic()
try:
    subprocess.run(py("import time; time.sleep(30)"), timeout=0.5)
except subprocess.TimeoutExpired as err:
    print("caught TimeoutExpired after ~%.1fs (limit was %.1fs)" % (time.monotonic() - start, err.timeout))
    print("the child was killed by run() - we did not wait 30 seconds")

# 06. input= - Feed Text to the Child's stdin
# ------------------------------------
# - Programs that read from stdin (like `sort`, or input()) can be driven
#   without a terminal: pass the data as input=.
print("\n# 06. input= (feeding stdin)")
result = subprocess.run(
    py("import sys; data = sys.stdin.read().split(); print(sorted(data))"),
    input="pear apple fig banana",
    capture_output=True,
    text=True,
)
print("child sorted our words:", result.stdout.strip())

# 07. cwd= and env= - Where to Run and With Which Variables
# ------------------------------------
# - cwd=  the directory the child starts in (does NOT change YOUR directory).
# - env=  a dict of environment variables for the child. If you pass env=
#   it REPLACES the whole environment - the usual pattern is to copy ours
#   and add to it.
print("\n# 07. cwd= and env=")
our_cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmp:
    out = subprocess.run(py("import os; print(os.path.basename(os.getcwd()))"),
                         capture_output=True, text=True, cwd=tmp)
    print("child cwd leaf matches our temp dir:", out.stdout.strip() == os.path.basename(tmp))
print("our own cwd unchanged:", os.getcwd() == our_cwd)

child_env = {**os.environ, "GREETING": "namaste"}  # copy + add, never mutate os.environ
out = subprocess.run(py("import os; print(os.environ.get('GREETING', 'unset'))"),
                     capture_output=True, text=True, env=child_env)
print("GREETING seen by child:", out.stdout.strip())
print("GREETING in our own env:", os.environ.get("GREETING", "unset"), "(unchanged)")

# GOTCHA: env={"GREETING": "x"} alone drops PATH, HOME, ... Some programs break.
bare = subprocess.run(py("import os; print(len(os.environ) <= 5)"),
                      capture_output=True, text=True, env={"GREETING": "x"})
print("child given ONLY our dict has a tiny environment:", bare.stdout.strip())

# 08. Running Python in a Child: -c and -m
# ------------------------------------
# - [sys.executable, "-c", "code"] runs a snippet. Use sys.executable, not the
#   string "python": "python" might be a different version (or missing) on
#   another machine or inside a virtualenv.
# - [sys.executable, "-m", "module"] runs a module as a script, e.g. -m json.tool
#   (pretty-prints JSON), -m timeit, -m http.server.
print("\n# 08. Python child with -c and -m")
out = subprocess.run([PY, "-c", "import sys; print(sys.version_info[:2])"], capture_output=True, text=True)
print("child Python version:", out.stdout.strip())
out = subprocess.run([PY, "-m", "json.tool"], input='{"b": 1, "a": [1, 2]}', capture_output=True, text=True)
print("python -m json.tool output:")
print(out.stdout.rstrip())

# 09. List Arguments vs shell=True - and Shell Injection
# ------------------------------------
# - LIST form: ["prog", "arg1", "arg2"]. Python hands each item to the program
#   exactly as is. No shell involved. Spaces, quotes, ; & | in an argument are
#   just characters. SAFE.
# - shell=True with a string: Python hands the whole string to /bin/sh, which
#   interprets it - so `;`, `&&`, `|`, `$(...)` all have special meaning.
#   If any part of that string came from a user, an attacker can add commands.
#   This is "shell injection" - a classic, serious vulnerability.
print("\n# 09. List args vs shell=True (injection demo, harmless payload)")
user_input = "hello; echo INJECTED-COMMAND-RAN"  # pretend a user typed this as a "name"

# BAD: string built with an f-string and run by a shell
if IS_POSIX:
    bad = subprocess.run(f"echo {user_input}", shell=True, capture_output=True, text=True)
    print("shell=True, unquoted  ->", bad.stdout.splitlines())
    print("  two lines of output = the 'name' ended the echo and a SECOND command ran!")

    # Better, if you really need a shell: quote untrusted pieces with shlex.quote
    good_shell = subprocess.run(f"echo {shlex.quote(user_input)}", shell=True, capture_output=True, text=True)
    print("shell=True, quoted    ->", good_shell.stdout.splitlines())

# BEST: no shell at all - arguments cannot be reinterpreted
best = subprocess.run([PY, "-c", "import sys; print(sys.argv[1])", user_input], capture_output=True, text=True)
print("list args, no shell   ->", best.stdout.splitlines())
print("RULE: prefer list args. Use shell=True only for trusted constant strings.")

# 10. shlex - split, quote, join
# ------------------------------------
# - shlex.split("...")  turns a command STRING into a safe list, honouring quotes
#   (a plain .split() would break "my file.txt" into two pieces).
# - shlex.quote(s)      makes one string safe to paste into a shell command.
# - shlex.join(list)    the reverse of split: list -> shell-safe string (3.8+).
print("\n# 10. shlex.split / quote / join")
cmd_string = 'grep -r "hello world" \'my folder\' --include=*.py'
print("str.split():", cmd_string.split())
print("shlex.split:", shlex.split(cmd_string))
print("shlex.quote:", shlex.quote("file name; rm -rf /"))
print("shlex.join :", shlex.join(["echo", "it's", "a test"]))

# 11. os.system vs subprocess - Why Not os.system
# ------------------------------------
# - os.system("cmd") always uses a shell (injection risk), cannot capture the
#   output, cannot set a timeout, and gives back an awkward status number.
# - subprocess.run gives you output, return code, timeout, no shell by default.
print("\n# 11. os.system vs subprocess")
status = os.system(f'"{PY}" -c "pass"')  # works, but you learn almost nothing from it
print("os.system returned only a number:", status)
print("subprocess.run gave us stdout/stderr/returncode/timeout. Use that instead.")

# 12. Popen - Starting a Process WITHOUT Waiting
# ------------------------------------
# - run() = start + wait + collect. Popen = just START it and give you a handle.
# - You then decide: poll() (is it done?), wait(), communicate(), terminate().
# - Use Popen for: streaming output, pipes between programs, long-running
#   helpers you control, anything run() cannot express.
print("\n# 12. Popen basics")
proc = subprocess.Popen(py("import time; time.sleep(0.3); print('child done')"),
                        stdout=subprocess.PIPE, text=True)
print("right after start, poll():", proc.poll(), "(None = still running)")
out, _ = proc.communicate()  # waits and gathers output
print("after communicate, poll():", proc.poll(), "| output:", out.strip())

# 13. Piping Two Processes Together (like `a | b` in a shell)
# ------------------------------------
# - Connect the first process's stdout to the second's stdin.
# - IMPORTANT: close OUR copy of p1.stdout after handing it to p2 so p1 gets
#   SIGPIPE/EOF properly if p2 exits early.
print("\n# 13. Pipe: producer | consumer")
producer = subprocess.Popen(py("for i in range(5): print(i)"), stdout=subprocess.PIPE, text=True)
consumer = subprocess.Popen(py("import sys; print(sum(int(l) for l in sys.stdin))"),
                            stdin=producer.stdout, stdout=subprocess.PIPE, text=True)
producer.stdout.close()  # let the producer know only the consumer reads it
total, _ = consumer.communicate(timeout=10)
producer.wait(timeout=10)
print("sum of 0..4 computed by the second process:", total.strip())

# 14. communicate() vs Reading stdout by Hand - the DEADLOCK Gotcha
# ------------------------------------
# - A pipe is a small buffer (often ~64 KB). If the child writes more than the
#   buffer holds, it BLOCKS until somebody reads.
# - Deadlock recipe: you call proc.wait() (waits for exit) while the child is
#   blocked waiting for you to read. Neither side moves. Hang forever.
#       proc = Popen(cmd, stdout=PIPE)
#       proc.wait()                # DANGER with big output - never do this
#       data = proc.stdout.read()
# - Same trap with two pipes (stdout AND stderr): reading one fully while the
#   other fills up can also block.
# - SAFE: communicate() reads both pipes concurrently until EOF, then waits.
#   run(capture_output=True) uses communicate() internally, so it is safe too.
print("\n# 14. Big output: the safe way (communicate)")
big = py("import sys; sys.stdout.write('x' * 500000); sys.stderr.write('e' * 500000)")
proc = subprocess.Popen(big, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out, err = proc.communicate(timeout=10)  # drains BOTH pipes without deadlocking
print("received stdout chars:", len(out), "| stderr chars:", len(err), "| code:", proc.returncode)
print("(the deadlock version is intentionally NOT run - it would hang the script)")

# Another safe option: send big output to a file instead of a pipe.
with tempfile.TemporaryFile("w+") as tmpfile:
    subprocess.run(py("print('line ' * 5)"), stdout=tmpfile)
    tmpfile.seek(0)
    print("output sent straight to a file:", tmpfile.read().strip())

# 15. Streaming Output Line by Line
# ------------------------------------
# - To react while the child is still running (progress bars, live logs),
#   iterate over proc.stdout. Reading line by line keeps the pipe drained.
# - Child must flush its output (python -u or flush=True) else it sits in
#   the child's own buffer until the end.
print("\n# 15. Streaming a child's output line by line")
code = "import time\nfor i in range(3):\n    print('tick', i, flush=True)\n    time.sleep(0.1)"
with subprocess.Popen(py(code), stdout=subprocess.PIPE, text=True) as proc:
    for line in proc.stdout:
        print("  got line while running:", line.rstrip())
print("exit code after the with-block:", proc.returncode)

# 16. stderr=STDOUT - Merge Error Output into Normal Output
# ------------------------------------
# - stderr=subprocess.STDOUT sends the child's errors down the same pipe as
#   its normal output, in the order they happened. Handy for logging one
#   combined stream. You lose the ability to tell them apart.
# - GOTCHA: a child's stdout is block-buffered when it is a pipe but stderr is
#   not, so without flush=True the order can look scrambled (errors first).
print("\n# 16. stderr=STDOUT")
mixed = subprocess.run(
    py("import sys; print('normal 1', flush=True); print('error 1', file=sys.stderr, flush=True); print('normal 2')"),
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
)
print("combined:", mixed.stdout.splitlines())
print("result.stderr is", mixed.stderr, "(it was merged)")

# 17. Return Codes and Negative Return Codes (Signals)
# ------------------------------------
# - returncode 0           -> success.
# - positive (1, 2, 127..) -> the program chose to exit with that number.
# - NEGATIVE (-15, -9 ...) -> on POSIX, the child was KILLED by a signal;
#   -N means signal number N. So -15 = SIGTERM, -9 = SIGKILL.
print("\n# 17. Return codes")
print("exit code 0 :", subprocess.run(py("pass")).returncode)
print("exit code 5 :", subprocess.run(py("import sys; sys.exit(5)")).returncode)
if IS_POSIX:
    sleeper = subprocess.Popen(py("import time; time.sleep(30)"))
    sleeper.terminate()  # sends SIGTERM (ask nicely)
    sleeper.wait(timeout=10)
    print("terminated child returncode:", sleeper.returncode, "->", signal.Signals(-sleeper.returncode).name)
    # Python itself reports an uncaught Exception as exit code 1:
    print("uncaught exception -> code:", subprocess.run(py("raise ValueError('x')"), capture_output=True).returncode)
else:
    print("(negative return codes are POSIX only - skipped on this platform)")

# 18. Graceful Stop: terminate() then kill()
# ------------------------------------
# - terminate() = SIGTERM: "please exit" - the child CAN catch it and clean up.
# - kill()      = SIGKILL: cannot be caught or ignored. Last resort.
# - Pattern: terminate, wait a short while, then kill if still alive.
print("\n# 18. terminate -> wait -> kill")
stubborn = subprocess.Popen(py("import time; time.sleep(30)"))
stubborn.terminate()
try:
    stubborn.wait(timeout=2)
    print("child exited after terminate(), code:", stubborn.returncode)
except subprocess.TimeoutExpired:
    stubborn.kill()
    stubborn.wait()
    print("had to kill()")

# 19. Handling "Program Not Found"
# ------------------------------------
# - If the program does not exist, you get FileNotFoundError BEFORE any child
#   exists (so there is no return code to check).
print("\n# 19. FileNotFoundError for a missing program")
try:
    subprocess.run(["definitely-not-a-real-program-xyz"], capture_output=True)
except FileNotFoundError as err:
    print("caught FileNotFoundError:", err.filename)

# 20. Worked Example: run_with_timeout_and_retries
# ------------------------------------
# - Real scripts call flaky things: a build tool, a CLI that talks to a server.
#   They fail sometimes for transient reasons. A tidy helper wraps:
#   timeout per attempt + retry with growing wait (backoff) + clear final error.
print("\n# 20. run_with_timeout_and_retries helper")


class CommandFailed(Exception):
    """Raised when every attempt failed. Carries the last result for debugging."""


def run_with_timeout_and_retries(cmd, *, timeout=5.0, retries=3, backoff=0.1, retry_on=(1,)):
    """Run cmd; retry on timeout or on exit codes in retry_on.

    - Exit codes NOT in retry_on (e.g. 2 = bad usage) fail immediately: retrying a
      permanent error only wastes time.
    - Waits backoff, 2*backoff, 4*backoff ... between attempts.
    """
    last_problem = None
    for attempt in range(1, retries + 1):
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            last_problem = f"timed out after {timeout}s"
        else:
            if done.returncode == 0:
                print(f"  attempt {attempt}: success")
                return done
            last_problem = f"exit code {done.returncode}: {done.stderr.strip()}"
            if done.returncode not in retry_on:
                raise CommandFailed(f"permanent failure, not retrying - {last_problem}")
        print(f"  attempt {attempt}: {last_problem}")
        if attempt < retries:
            time.sleep(backoff * 2 ** (attempt - 1))
    raise CommandFailed(f"gave up after {retries} attempts - {last_problem}")


with tempfile.TemporaryDirectory() as tmp:
    marker = os.path.join(tmp, "count.txt")
    # A child that fails twice (using a counter file), then succeeds.
    flaky = (
        "import sys, os\n"
        f"p = {marker!r}\n"
        "n = int(open(p).read()) if os.path.exists(p) else 0\n"
        "open(p, 'w').write(str(n + 1))\n"
        "if n < 2:\n"
        "    print('transient error', file=sys.stderr); sys.exit(1)\n"
        "print('finally worked')"
    )
    print("flaky command (fails twice, then works):")
    done = run_with_timeout_and_retries(py(flaky), backoff=0.05)
    print("  result:", done.stdout.strip())

print("always timing out:")
try:
    run_with_timeout_and_retries(py("import time; time.sleep(5)"), timeout=0.2, retries=2, backoff=0.05)
except CommandFailed as err:
    print("  CommandFailed:", err)

print("permanent error (exit 2), no retry:")
try:
    run_with_timeout_and_retries(py("import sys; sys.exit(2)"), retries=3)
except CommandFailed as err:
    print("  CommandFailed:", err)

# ====================================================================
# SIGNALS
# ====================================================================

# 21. What Signals Are and the signal.Signals Enum
# ------------------------------------
# - SIGINT  (2)  Ctrl+C in the terminal -> Python turns it into KeyboardInterrupt.
# - SIGTERM (15) polite "please terminate" (what `kill PID` and Docker/Kubernetes send).
# - SIGKILL (9)  cannot be caught or handled. Instant death.
# - SIGHUP  (1)  terminal closed; daemons often use it as "reload config".
# - SIGALRM (14) fired by signal.alarm(); used for timeouts (POSIX only).
# - SIGUSR1/2    free for your own use.
print("\n# 21. signal.Signals enum")
wanted = ["SIGINT", "SIGTERM", "SIGKILL", "SIGHUP", "SIGALRM", "SIGUSR1"]
for name in wanted:
    sig = getattr(signal, name, None)
    if sig is None:
        print(f"  {name:8} not available on this platform")
    else:
        print(f"  {name:8} = {int(sig):2}  ({signal.strsignal(sig)})")
print("total signals defined here:", len(list(signal.Signals)))
print("signal.Signals(2) ->", signal.Signals(2).name)

# 22. SIGINT -> KeyboardInterrupt (Ctrl+C)
# ------------------------------------
# - By default Python installs a SIGINT handler that raises KeyboardInterrupt.
#   That is why try/except KeyboardInterrupt catches Ctrl+C.
# - We can simulate Ctrl+C by sending the signal to ourselves.
print("\n# 22. SIGINT becomes KeyboardInterrupt")
if IS_POSIX:
    try:
        os.kill(os.getpid(), signal.SIGINT)  # same as the user pressing Ctrl+C
        time.sleep(1)  # the signal handler runs between bytecodes; the sleep just gives it a moment
        print("not reached")
    except KeyboardInterrupt:
        print("caught KeyboardInterrupt raised by the default SIGINT handler")
else:
    print("(skipped: sending SIGINT to ourselves is POSIX only here)")

# 23. Custom Handlers with signal.signal()
# ------------------------------------
# - signal.signal(sig, handler) installs handler(signum, frame).
# - Handlers run in the MAIN THREAD only, between two Python instructions.
#   Keep them tiny: set a flag, then let normal code do the real work.
#   (Doing heavy work or taking locks inside a handler is a classic bug.)
# - signal.SIG_IGN ignores a signal, signal.SIG_DFL restores the default.
print("\n# 23. signal.signal() handler")
received = []


def on_usr1(signum, frame):
    received.append(signal.Signals(signum).name)


if hasattr(signal, "SIGUSR1"):
    old = signal.signal(signal.SIGUSR1, on_usr1)  # returns the previous handler
    os.kill(os.getpid(), signal.SIGUSR1)
    time.sleep(0.05)
    print("handler recorded:", received)
    signal.signal(signal.SIGUSR1, old)  # always restore what we replaced
else:
    print("(SIGUSR1 not available - skipped)")

# 24. SIGTERM Handler for Graceful Shutdown
# ------------------------------------
# - Servers and workers get SIGTERM when deployed/stopped. The pattern:
#     1. handler only sets a "stop requested" flag
#     2. main loop checks the flag, finishes the current unit of work, cleans up
#   so you never leave a half-written file or a dropped job.
# - We demonstrate it in a CHILD process so this script is not disturbed.
print("\n# 24. Graceful SIGTERM shutdown (in a child)")
worker = r"""
import signal, sys, time
stop = False
def handle(signum, frame):
    global stop
    stop = True                      # only set a flag here
signal.signal(signal.SIGTERM, handle)
print("worker ready", flush=True)
while not stop:
    time.sleep(0.05)                 # pretend to process jobs
print("finishing current job and cleaning up", flush=True)
sys.exit(0)
"""
if IS_POSIX:
    w = subprocess.Popen(py(worker), stdout=subprocess.PIPE, text=True)
    print("child says:", w.stdout.readline().strip())  # wait until handler installed
    w.terminate()  # SIGTERM
    rest, _ = w.communicate(timeout=10)
    print("child says:", rest.strip())
    print("exit code:", w.returncode, "(0 = clean exit, NOT -15, because it handled the signal)")
else:
    print("(skipped: POSIX signal delivery demo)")

# 25. signal.alarm() Timeout Pattern (POSIX only)
# ------------------------------------
# - signal.alarm(n) asks the OS to send SIGALRM after n seconds. The handler
#   can raise an exception, which pops out of whatever code is running -
#   a way to put a time limit on ANY blocking call in your own process.
# - Limits: whole seconds only, main thread only, one alarm at a time, no
#   Windows. signal.setitimer allows fractions of a second.
# - For subprocesses prefer run(timeout=...). For threads/async use their own timeouts.
print("\n# 25. signal.alarm() timeout")


class Timeout(Exception):
    pass


def _raise_timeout(signum, frame):
    raise Timeout("took too long")


if hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer"):
    old = signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, 0.3)  # fire in 0.3 seconds
    try:
        time.sleep(5)  # would block 5s...
    except Timeout as err:
        print("alarm interrupted the sleep:", err)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)  # cancel any pending timer
        signal.signal(signal.SIGALRM, old)
    signal.alarm(0)
    print("pending alarm after cancel:", signal.alarm(0))
else:
    print("(SIGALRM not available on this platform - skipped)")

# 26. Signal Handlers Only Run in the Main Thread
# ------------------------------------
# - signal.signal() itself RAISES ValueError if called from another thread.
# - And when a signal arrives, Python runs the handler in the main thread,
#   even if a worker thread was busy. So: main thread owns signals; workers
#   should watch a threading.Event the main thread sets from the handler.
print("\n# 26. signal.signal only works in the main thread")
thread_result = []


def try_in_thread():
    try:
        signal.signal(signal.SIGINT, signal.default_int_handler)
        thread_result.append("installed")
    except ValueError as err:
        thread_result.append(f"ValueError: {err}")


t = threading.Thread(target=try_in_thread)
t.start()
t.join(timeout=5)
print("from a worker thread:", thread_result[0])

# 27. atexit - Cleanup When the Interpreter Exits
# ------------------------------------
# - atexit.register(func, *args) runs func when Python exits normally
#   (end of script, sys.exit(), unhandled exception, or SIGINT turned into
#   KeyboardInterrupt).
# - Order: LAST registered runs FIRST (LIFO, like unwinding a stack).
# - NOT run on: os._exit(), a fatal signal with no handler (SIGKILL, default SIGTERM),
#   or a hard crash of the interpreter. For SIGTERM install a handler that calls
#   sys.exit() so atexit still runs.
# - Shown in a child process, so we can observe it from outside.
print("\n# 27. atexit order and when it does NOT run")
atexit_child = (
    "import atexit, sys\n"
    "atexit.register(print, 'cleanup A (registered first, runs last)')\n"
    "atexit.register(print, 'cleanup B')\n"
    "atexit.register(print, 'cleanup C (registered last, runs first)')\n"
    "print('main body done')\n"
)
r = subprocess.run(py(atexit_child), capture_output=True, text=True)
print("normal exit :", r.stdout.splitlines())
hard_child = (
    "import atexit, os\n"
    "atexit.register(print, 'you will never see this')\n"
    "print('about to os._exit', flush=True)\n"
    "os._exit(0)\n"
)
r = subprocess.run(py(hard_child), capture_output=True, text=True)
print("os._exit    :", r.stdout.splitlines())
if IS_POSIX:
    sigterm_child = (
        "import atexit, os, signal\n"
        "atexit.register(print, 'cleanup ran', flush=True)\n"
        "def raise_exit(signum, frame):\n"
        "    raise SystemExit(0)\n"
        "signal.signal(signal.SIGTERM, raise_exit)\n"
        "print('ready', flush=True)\n"
        "signal.pause()\n"
    )
    p = subprocess.Popen(py(sigterm_child), stdout=subprocess.PIPE, text=True)
    p.stdout.readline()  # 'ready'
    p.terminate()
    rest, _ = p.communicate(timeout=10)
    print("SIGTERM + handler calling SystemExit:", rest.splitlines(), "code", p.returncode)


# Register something in OUR process too; it prints at the very end of this script.
def goodbye():
    print("\n[atexit] goodbye from the main script - runs at interpreter shutdown")


atexit.register(goodbye)

# 28. Exit Codes Convention and a Tiny CLI
# ------------------------------------
# - 0 = success. Non-zero = failure. Shells, CI, cron, make, Docker all read it.
# - Common convention: 1 = general error, 2 = bad command-line usage,
#   130 = killed by Ctrl+C (128 + signal 2), 143 = SIGTERM (128 + 15).
# - sys.exit(0) / sys.exit() = success. sys.exit("message") prints the message to
#   stderr and exits with code 1. sys.exit(n) exits with n.
# - Keep stdout for RESULTS and stderr for DIAGNOSTICS so output can be piped.
print("\n# 28. A tiny CLI that returns proper exit codes")
tiny_cli = r"""
import sys

def main(argv):
    if len(argv) != 2:
        print("usage: cli.py <non-negative integer>", file=sys.stderr)
        return 2                                 # misuse of the command line
    try:
        n = int(argv[1])
    except ValueError:
        print(f"error: {argv[1]!r} is not an integer", file=sys.stderr)
        return 1                                 # runtime error
    if n < 0:
        print("error: negative number", file=sys.stderr)
        return 1
    print(n * n)                                 # result on stdout
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))                     # the ONE place that exits
"""
for args in ([], ["7"], ["abc"], ["-4"]):
    r = subprocess.run([PY, "-c", tiny_cli, *args],
                       capture_output=True, text=True)
    # note: with -c, argv[0] is "-c" and __name__ is "__main__", so the CLI sees ["-c", *args]
    print(f"  args={args!s:9} -> code {r.returncode} | stdout={r.stdout.strip()!r} | stderr={r.stderr.strip()!r}")
print("DESIGN TIP: main() RETURNS a code; only the bottom of the file calls sys.exit(main()).")
print("That keeps main() testable - a test can just assert main([...]) == 2.")

# 29. Summary and Real-World Use
# ------------------------------------
# - Wrap git/ffmpeg/docker/pip/compilers from automation scripts: run(list, check=True, timeout=...).
# - CI scripts and deploy tools rely on exit codes - get them right.
# - Services handle SIGTERM for zero-downtime restarts; Ctrl+C handlers save work.
# - Rules of thumb: list args, no shell; always timeout; always check returncode;
#   capture or redirect output (never leave a pipe unread); restore signal handlers.
print("\n# 29. Summary")
print("run(list_args, capture_output=True, text=True, timeout=N, check=True)  <- the default recipe")
print("Popen + communicate()  <- when you need pipes or streaming")
print("signal handler = set a flag; atexit = cleanup; sys.exit(code) = report outcome")
