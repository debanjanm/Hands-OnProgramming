#!/usr/bin/env python3
# 01. The main(argv) -> int Pattern
# 02. argparse Basics: Positionals, Options, Flags
# 03. Types, Choices, Defaults, nargs
# 04. Subcommands
# 05. Mutually Exclusive and Required Groups
# 06. Custom Action: Load Values from a File
# 07. Exit Codes and Error Handling
# 08. Help Text and Formatting
# 09. click via CliRunner
# 10. typer via CliRunner
# 11. Config Layering: defaults < file < env < CLI
# 12. logging: Levels and Basics
# 13. logging: Handlers and Formatters
# 14. logging: Config with dictConfig
# 15. Interactive Input: input and getpass (notes)
# 16. Hand-Rolled Text Tables
# 17. Shebang and __main__ Guard
# 18. Packaging Entry Points (notes)

import argparse
import io
import json
import logging
import logging.config
import os
import shlex
import tempfile
import tomllib
from pathlib import Path

try:
    import click
    from click.testing import CliRunner as ClickRunner
except ImportError:
    click = None

try:
    import typer
    from typer.testing import CliRunner as TyperRunner
except ImportError:
    typer = None

# 01. The main(argv) -> int Pattern
# ----------------------------
# - Write main(argv=None) -> int: parse the list you are GIVEN, return an exit code.
# - argparse's parse_args(None) reads sys.argv, which in a notebook or test belongs
#   to the notebook/test runner. So in this file we ALWAYS pass an explicit list.
# - The bottom of a script does: raise SystemExit(main()) so the code becomes the exit status.

def build_parser():
    p = argparse.ArgumentParser(prog="greet", description="Say hello.")
    p.add_argument("name")
    p.add_argument("-n", "--times", type=int, default=1)
    p.add_argument("-v", "--verbose", action="store_true")
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    for _ in range(args.times):
        print(("Hello, " if not args.verbose else "Hello there, ") + args.name)
    return 0

print("exit code:", main(["Asha", "-n", "2"]))
print("exit code:", main(["Bo", "--verbose"]))

# 02. argparse Basics: Positionals, Options, Flags
# ----------------------------
# - Positional: required, order matters. Option: starts with - or --, optional by default.
# - action="store_true" makes a boolean flag; action="count" counts -vvv; action="append" collects repeats.
# - Names with dashes become attributes with underscores: --dry-run -> args.dry_run.

p = argparse.ArgumentParser(prog="demo")
p.add_argument("src")
p.add_argument("--dry-run", action="store_true")
p.add_argument("-v", action="count", default=0)
p.add_argument("--tag", action="append", default=[])
ns = p.parse_args(["file.txt", "--dry-run", "-vv", "--tag", "a", "--tag", "b"])
print(ns)
print(ns.dry_run, ns.v, ns.tag)
print(vars(ns))

# 03. Types, Choices, Defaults, nargs
# ----------------------------
# - type=int / float / Path converts the string; a failing conversion is a clean usage error.
# - type= can be YOUR function: raise argparse.ArgumentTypeError("message") for a custom message.
# - choices=[...] restricts values. nargs="+" one or more, "*" zero or more, "?" optional.

print()

def port(text):
    n = int(text)
    if not 1 <= n <= 65535:
        raise argparse.ArgumentTypeError(f"{n} is not a valid port (1-65535)")
    return n

p = argparse.ArgumentParser(prog="srv", exit_on_error=False)
p.add_argument("--port", type=port, default=8000)
p.add_argument("--level", choices=["low", "high"], default="low")
p.add_argument("files", nargs="*")
p.add_argument("--rate", type=float)
print(p.parse_args(["--port", "9000", "a", "b", "--rate", "1.5"]))
for bad in (["--port", "70000"], ["--level", "mid"], ["--rate", "fast"]):
    try:
        p.parse_args(bad)
    except argparse.ArgumentError as e:
        print("error:", e)
# Gotcha: default values that are strings are passed through type=; others are used as is.

# 04. Subcommands
# ----------------------------
# - add_subparsers(dest="command") gives git-style commands (git add, git commit).
# - Each subparser has its own arguments. set_defaults(func=...) lets you dispatch without if/elif.
# - required=True on subparsers, otherwise running with no command is silently allowed.

print()

def cmd_add(a):
    print("add", a.items)
    return 0

def cmd_rm(a):
    print("remove", a.name, "force" if a.force else "")
    return 0

def cli(argv):
    p = argparse.ArgumentParser(prog="tool")
    sub = p.add_subparsers(dest="command", required=True)
    pa = sub.add_parser("add", help="add items")
    pa.add_argument("items", nargs="+")
    pa.set_defaults(func=cmd_add)
    pr = sub.add_parser("rm", help="remove an item")
    pr.add_argument("name")
    pr.add_argument("-f", "--force", action="store_true")
    pr.set_defaults(func=cmd_rm)
    a = p.parse_args(argv)
    return a.func(a)

print(cli(["add", "x", "y"]))
print(cli(["rm", "z", "-f"]))

# 05. Mutually Exclusive and Required Groups
# ----------------------------
# - add_mutually_exclusive_group(): at most one of the options may be given.
# - required=True on the group: exactly one is needed.
# - argparse "errors" call sys.exit(2) after printing to stderr - catch SystemExit to test.

print()

def run_quiet(parser, argv):
    """Parse; on error capture stderr text and return the exit status."""
    err = io.StringIO()
    import contextlib
    with contextlib.redirect_stderr(err):
        try:
            return parser.parse_args(argv), 0, ""
        except SystemExit as e:
            return None, e.code, err.getvalue().strip().splitlines()[-1]

p = argparse.ArgumentParser(prog="out")
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json", action="store_true")
g.add_argument("--csv", action="store_true")
print(run_quiet(p, ["--json"]))
print(run_quiet(p, ["--json", "--csv"]))
print(run_quiet(p, []))

# 06. Custom Action: Load Values from a File
# ----------------------------
# - Subclass argparse.Action, implement __call__(parser, namespace, values, option_string).
# - Typical use: "--args-file f" expands to extra settings (like @file / fromfile_prefix_chars).
# - Built in alternative: ArgumentParser(fromfile_prefix_chars="@") reads one arg per line.

print()

class FromFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        text = Path(values).read_text()
        for key, val in json.loads(text).items():
            setattr(namespace, key, val)

with tempfile.TemporaryDirectory() as tmp:
    f = Path(tmp) / "preset.json"
    f.write_text('{"width": 80, "mode": "wide"}')
    p = argparse.ArgumentParser(prog="fmt")
    p.add_argument("--width", type=int, default=40)
    p.add_argument("--mode", default="narrow")
    p.add_argument("--preset", action=FromFileAction)
    print(p.parse_args([]))
    print(p.parse_args(["--preset", str(f)]))
    at = Path(tmp) / "args.txt"
    at.write_text("--width\n99\n")
    p2 = argparse.ArgumentParser(prog="fmt", fromfile_prefix_chars="@")
    p2.add_argument("--width", type=int)
    print(p2.parse_args(["@" + str(at)]))
# Gotcha: actions run in command-line order, so a later option overrides the file.

# 07. Exit Codes and Error Handling
# ----------------------------
# - 0 = success, 1 = general failure, 2 = usage error (argparse uses this).
# - Pick a few documented codes for your tool; do not return random numbers.
# - Catch EXPECTED errors in main, print a short message to stderr, return nonzero.
#   Let unexpected bugs raise (they give a traceback, which you want).
# - Never write sys.exit(main) - call it: raise SystemExit(main()).

print()

EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2

def risky_main(argv):
    p = argparse.ArgumentParser(prog="rm-tool")
    p.add_argument("path")
    a = p.parse_args(argv)
    try:
        Path(a.path).read_text()
    except FileNotFoundError:
        print("rm-tool: no such file: <path>", file=io.StringIO())  # would go to stderr
        return EXIT_FAIL
    return EXIT_OK

with tempfile.TemporaryDirectory() as tmp:
    print("missing file ->", risky_main([str(Path(tmp) / "nope.txt")]))
    (Path(tmp) / "ok.txt").write_text("x")
    print("existing file ->", risky_main([str(Path(tmp) / "ok.txt")]))
print("usage error ->", run_quiet(argparse.ArgumentParser(prog="x"), ["--bogus"])[1])
try:
    raise SystemExit(3)
except SystemExit as e:
    print("SystemExit code:", e.code)

# 08. Help Text and Formatting
# ----------------------------
# - help="..." on every argument; metavar changes the placeholder; %(default)s shows defaults.
# - RawDescriptionHelpFormatter keeps your newlines in description/epilog.
# - ArgumentDefaultsHelpFormatter auto-appends (default: ...).
# - parser.format_help() returns the text (instead of printing and exiting like --help does).

print()

p = argparse.ArgumentParser(
    prog="conv",
    description="Convert files.\nSecond line kept.",
    epilog="Example: conv in.txt -f json",
    formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, width=70),
)
p.add_argument("input", help="file to read")
p.add_argument("-f", "--format", choices=["json", "csv"], default="json", metavar="FMT", help="output (default: %(default)s)")
print(p.format_usage(), end="")
print(p.format_help())

# 09. click via CliRunner
# ----------------------------
# - click uses decorators: @click.command, @click.option, @click.argument, @click.group.
# - CliRunner().invoke(cmd, [args]) runs it IN PROCESS and captures output and exit code,
#   so it never touches sys.argv and works in notebooks and tests.
# - result.exit_code, result.output; result.exception holds SystemExit/errors.

print()

if click:
    @click.group()
    def tool():
        """Demo click app."""

    @tool.command()
    @click.argument("name")
    @click.option("--shout/--no-shout", default=False)
    @click.option("--count", type=click.IntRange(1, 3), default=1)
    def hello(name, shout, count):
        for _ in range(count):
            click.echo(name.upper() if shout else name)

    r = ClickRunner()
    for argv in (["hello", "Asha", "--shout", "--count", "2"], ["hello", "Bo", "--count", "9"], ["hello"]):
        res = r.invoke(tool, argv)
        print(argv, "->", res.exit_code, res.output.strip().splitlines()[-1])
    print(r.invoke(tool, ["--help"]).output.splitlines()[0])
else:
    print("skip: click not installed")

# 10. typer via CliRunner
# ----------------------------
# - typer builds the CLI from TYPE HINTS on a function (on top of click).
# - typer.testing.CliRunner works like click's. A one-command app uses the function as the command.
# - Gotcha: with a single command, typer does not use a subcommand name.

print()

if typer:
    app = typer.Typer()

    @app.command()
    def add(a: int, b: int = 10, verbose: bool = False):
        out = a + b
        typer.echo(f"{a}+{b}={out}" if verbose else out)

    @app.command()
    def nop():
        typer.echo("nop")

    tr = TyperRunner()
    for argv in (["add", "1"], ["add", "1", "--b", "5", "--verbose"], ["add", "x"]):
        res = tr.invoke(app, argv)
        print(argv, "->", res.exit_code, res.output.strip().splitlines()[0] if res.exit_code == 0 else "(usage error)")
else:
    print("skip: typer not installed")

# 11. Config Layering: defaults < file < env < CLI
# ----------------------------
# - Standard precedence, weakest to strongest: built-in defaults, config file,
#   environment variables, command-line flags.
# - Implement as dict merging in that order; CLI options default to None so
#   "not given" is distinguishable from a real value.
# - Env values are strings: convert.

print()

DEFAULTS = {"host": "localhost", "port": 8000, "debug": False}

def load_config(argv, env, file_text):
    cfg = dict(DEFAULTS)
    cfg.update(tomllib.loads(file_text))
    if "APP_HOST" in env:
        cfg["host"] = env["APP_HOST"]
    if "APP_PORT" in env:
        cfg["port"] = int(env["APP_PORT"])
    if "APP_DEBUG" in env:
        cfg["debug"] = env["APP_DEBUG"].lower() in ("1", "true", "yes")
    p = argparse.ArgumentParser()
    p.add_argument("--host")
    p.add_argument("--port", type=int)
    p.add_argument("--debug", action="store_true", default=None)
    cli_vals = {k: v for k, v in vars(p.parse_args(argv)).items() if v is not None}
    cfg.update(cli_vals)
    return cfg

toml_text = 'host = "filehost"\nport = 9000\n'
print("defaults only :", load_config([], {}, ""))
print("+ file        :", load_config([], {}, toml_text))
print("+ env         :", load_config([], {"APP_PORT": "7000", "APP_DEBUG": "true"}, toml_text))
print("+ cli wins    :", load_config(["--port", "1234"], {"APP_PORT": "7000"}, toml_text))
# Gotcha: argparse default=8000 would ALWAYS override the file; default=None avoids that.

# 12. logging: Levels and Basics
# ----------------------------
# - Levels: DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50).
# - A logger only emits records at or above its level.
# - Use logging.getLogger(__name__) in modules; configure handlers ONCE at the app edge.
# - Prefer lazy formatting: log.info("x=%s", x) not f-strings.

print()

print({name: logging.getLevelName(n) for name, n in (("d", 10), ("i", 20), ("w", 30), ("e", 40), ("c", 50))})
log = logging.getLogger("demo.basic")
print("effective level:", logging.getLevelName(log.getEffectiveLevel()), "(root default is WARNING)")
print("isEnabledFor(INFO):", log.isEnabledFor(logging.INFO))

# 13. logging: Handlers and Formatters
# ----------------------------
# - Logger creates records -> Handler decides WHERE (StreamHandler, FileHandler, ...)
#   -> Formatter decides the TEXT. Each handler can have its own level.
# - Logging into a StringIO makes output deterministic and testable.
# - propagate=False stops records also reaching the root logger.

print()

stream = io.StringIO()
h = logging.StreamHandler(stream)
h.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))
lg = logging.getLogger("demo.handlers")
lg.setLevel(logging.DEBUG)
lg.propagate = False
lg.addHandler(h)
lg.debug("debug %s", 1)
lg.info("info line")
lg.warning("careful")
lg.error("failed %d times", 3)
print(stream.getvalue(), end="")
h.setLevel(logging.ERROR)
lg.warning("hidden now")
lg.error("shown")
print(stream.getvalue().splitlines()[-1])
lg.removeHandler(h)
# Gotcha: adding a handler every call duplicates lines. Configure once.

# 14. logging: Config with dictConfig
# ----------------------------
# - logging.config.dictConfig(dict) describes formatters, handlers, loggers in data
#   (easy to load from JSON/TOML/YAML).
# - "ext://sys.stdout" style refs exist; here we attach our own StringIO afterwards.
# - disable_existing_loggers=False so you do not silence libraries.

print()

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "[%(levelname)s] %(message)s"}},
    "handlers": {"mem": {"class": "logging.StreamHandler", "formatter": "plain", "level": "INFO"}},
    "loggers": {"demo.cfg": {"handlers": ["mem"], "level": "DEBUG", "propagate": False}},
})
cl = logging.getLogger("demo.cfg")
cap = io.StringIO()
cl.handlers[0].setStream(cap)
cl.debug("below handler level")
cl.info("configured ok")
cl.critical("on fire")
print(cap.getvalue(), end="")
cl.handlers.clear()

# 15. Interactive Input: input and getpass (notes)
# ----------------------------
# - input("Name: ") blocks waiting on the keyboard - it would hang in tests and cron.
# - getpass.getpass("Password: ") reads without echo. Never pass secrets as CLI
#   arguments (they show up in `ps` and shell history); prefer env vars or getpass.
# - Check sys.stdin.isatty() before prompting; if not a terminal, fail with a clear
#   message or read from stdin.
# - Make prompts optional: every question should also be answerable by a flag.
# (Nothing here is executed: those calls would wait for a human.)

print()

print("isatty-style check is a one-liner: sys.stdin.isatty(); skipped here on purpose")

# 16. Hand-Rolled Text Tables
# ----------------------------
# - Compute each column width from the data, then pad with str.ljust / rjust / format specs.
# - Left-align text, right-align numbers. Libraries (rich, tabulate) do this for you;
#   knowing the manual way means no dependency for small tools.

print()

def table(headers, rows):
    cells = [[str(c) for c in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) for i, h in enumerate(headers)]
    num = [all(c.replace(".", "", 1).isdigit() for c in col) for col in zip(*cells)]
    fmt = lambda row: " | ".join((c.rjust(w) if n else c.ljust(w)) for c, w, n in zip(row, widths, num))
    line = "-+-".join("-" * w for w in widths)
    return "\n".join([fmt(headers), line, *(fmt(r) for r in cells)])

print(table(["name", "qty", "price"], [("apple", 3, 1.5), ("watermelon", 12, 30.25), ("fig", 100, 0.5)]))

# 17. Shebang and __main__ Guard
# ----------------------------
# - First line "#!/usr/bin/env python3" + chmod +x lets you run ./script.py directly.
# - `if __name__ == "__main__":` runs the CLI only when executed, not when imported
#   (so tests can import main without side effects).
# - Pattern: raise SystemExit(main()) - main(argv=None) -> int.

print()

print("__name__ here is:", __name__)
print("main is importable and callable:", callable(main))
print("shlex.split helps tests: ", shlex.split('add "two words" --force'))

# 18. Packaging Entry Points (notes)
# ----------------------------
# - To install a command, declare it in pyproject.toml:
#       [project.scripts]
#       greet = "mypkg.cli:main"
#   After `pip install .` the `greet` command calls mypkg.cli.main() and uses its
#   return value as the exit code - so keep the main() -> int contract.
# - `python -m mypkg` works if mypkg/__main__.py calls raise SystemExit(main()).
# - Keep logic in importable functions; keep the CLI layer thin.

print()

print("entry point 'mypkg.cli:main' -> import mypkg.cli; raise SystemExit(mypkg.cli.main())")

if __name__ == "__main__":
    # Demo of the guard: a real script ends with raise SystemExit(main()).
    # Here we only print the code - raising SystemExit would also stop a notebook kernel run.
    rc = 0
    print("a real script would now exit with status", rc)
