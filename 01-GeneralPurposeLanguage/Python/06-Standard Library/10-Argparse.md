# Argparse — Notes

## What this covers
The `argparse` module — builds command-line interfaces: parses `sys.argv` into named, typed values, auto-generates `--help`, and validates arguments.

## Key points
- **`ArgumentParser(description=...)`** — create the parser.
- **Positional arguments** — `parser.add_argument("name")`: required, order matters.
- **Optional arguments (flags)** — `parser.add_argument("--greeting", default=...)`: order doesn't matter.
- **`type=int`** — auto-converts the raw string input to that type.
- **`action="store_true"`** — boolean flag, `True` if present, `False` if not, no value needed.
- **`choices=[...]`** — restrict a value to a fixed set; anything else errors out.
- **`parser.parse_args()`** — reads real `sys.argv`; pass a list explicitly (`parse_args([...])`) to test without real CLI input.
- **`add_subparsers()`** — git-style subcommands (`add`, `remove`), each with its own arguments (`dest=` names which subcommand was chosen).
- **`add_argument_group("name")`** — purely organizational, groups related args together in `--help` output.
- **`add_mutually_exclusive_group()`** — only one of the group's arguments may be given; passing two of them exits with an error.
- **`nargs="+"`** (one or more, required) vs **`nargs="*"`** (zero or more) — variable-length arguments collected into a list.
- **Custom `type=` validator function** — raise `argparse.ArgumentTypeError` inside it for a clean CLI error message instead of a raw traceback.

## Gotchas (the part worth revising twice)
- Passing an invalid value (bad `choices`, both args of a mutually-exclusive group, failed custom validator) makes argparse call `sys.exit()` — catch `SystemExit` if you need to test that behavior without killing the process.
- `sys.argv[0]` isn't consumed by argparse — it's the script name; `parse_args()` (no args passed) reads from `sys.argv[1:]` automatically.
- A custom `type=` function should raise `argparse.ArgumentTypeError` (not a plain `ValueError`) to get argparse's clean CLI-style error message.
- Argument groups (`add_argument_group`) are cosmetic only — for actual either/or *validation*, you need `add_mutually_exclusive_group()` instead.

## When it matters
Any script meant to be run from the command line with options — flags, required inputs, or git-style subcommands — where you want built-in `--help`, type checking, and validation for free.

## One-line recap example
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--shout", action="store_true")
args = parser.parse_args()   # reads sys.argv automatically
```
