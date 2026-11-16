# CLI Apps and Configuration — Notes

## What this covers
Building command-line tools with argparse (and click/typer), testing them without touching `sys.argv`, layering configuration, logging, and structuring a script so it is importable, testable and installable.

## Key points
- Shape every tool as `main(argv=None) -> int` and end with `raise SystemExit(main())`.
- Always call `parser.parse_args(list)` explicitly when you are in a notebook or a test.
- argparse features: positionals, options, `store_true`, `count`, `append`, `type=`, `choices=`, `nargs`, subcommands (`add_subparsers(required=True)`), mutually exclusive groups, custom `Action` classes, `fromfile_prefix_chars`.
- Exit codes: `0` success, `1` failure, `2` usage error (argparse). Document any others.
- click and typer are tested in-process with `CliRunner().invoke(app, [args])`; check `exit_code` and `output`.
- Config precedence: defaults < config file (tomllib) < environment < command line.
- logging: Logger -> Handler -> Formatter. Configure once at the app edge (`dictConfig`), use `getLogger(__name__)` in modules, lazy `%s` formatting.
- Text tables: compute column widths, `ljust` text, `rjust` numbers.
- Entry points live in `pyproject.toml` under `[project.scripts]`.

## Gotchas (the part worth revising twice)
- `parse_args()` with no list reads `sys.argv` — in a notebook that is the kernel's arguments.
- argparse errors call `sys.exit(2)`; catch `SystemExit` in tests.
- A non-`None` argparse default overrides the config file and env — use `default=None` for layering.
- `sys.exit(main)` (no call) exits with the wrong status; call `main()`.
- Adding a handler on every call duplicates log lines; the root logger defaults to WARNING so INFO is hidden.
- `input()` hangs under cron and tests; secrets in argv leak through `ps` and shell history. Prefer env vars or `getpass`.
- Typer with one command has no subcommand name.
- Env values are strings: convert (`int`, explicit bool parsing).

## When it matters
Any script other people (or cron) will run. A clean `main(argv) -> int` plus layered config makes tools testable, scriptable and predictable.

## One-line recap example
```python
import argparse

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    print("Hello,", p.parse_args(argv).name)
    return 0

print(main(["Asha"]))
```
