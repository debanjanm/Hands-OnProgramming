import argparse

# 01. argparse - Introduction
# ------------------------------------
# - Builds command-line interfaces: parses sys.argv into named, typed values,
#   auto-generates --help, validates required/optional arguments.

print("# 01. argparse - Introduction")
print("# ------------------------------------")

# 02. Building a Parser
# ------------------------------------
parser = argparse.ArgumentParser(description="Demo CLI tool")

# 03. Positional Arguments (required, order matters)
# ------------------------------------
parser.add_argument("name", help="name to greet")

# 04. Optional Arguments (flags, order doesn't matter)
# ------------------------------------
parser.add_argument("--greeting", default="Hello", help="greeting word")

# 05. Type Conversion
# ------------------------------------
parser.add_argument("--times", type=int, default=1, help="how many times to greet")

# 06. Boolean Flags (store_true)
# ------------------------------------
parser.add_argument("--shout", action="store_true", help="uppercase the greeting")

# 07. Choices - Restrict to a Fixed Set of Values
# ------------------------------------
parser.add_argument("--style", choices=["plain", "formal"], default="plain")

print("\n# 02-07. Parser Built With Positional/Optional/Typed/Flag/Choice Args")

# 08. Parsing Arguments
# ------------------------------------
# - Normally argparse reads sys.argv; here we pass a fixed list to keep this
#   file runnable standalone without real command-line input.
demo_args = ["Debanjan", "--greeting", "Hi", "--times", "2", "--shout"]
args = parser.parse_args(demo_args)

print("\n# 08. Parsing Arguments")
print("simulated command: python script.py", " ".join(demo_args))
print("parsed namespace:", args)

# 09. Using the Parsed Values
# ------------------------------------
print("\n# 09. Using the Parsed Values")
message = f"{args.greeting}, {args.name}!"
if args.shout:
    message = message.upper()
for _ in range(args.times):
    print(message)

# 10. --help (reference - what a real user sees)
# ------------------------------------
print("\n# 10. --help (reference)")
parser.print_help()

# 11. Real Usage (reference, not executed here)
# ------------------------------------
print("\n# 11. Real Usage (reference)")
print("# In a real script, replace parse_args(demo_args) with parse_args()")
print("# so it reads actual command-line input from sys.argv:")
print("#   python script.py Debanjan --greeting Hi --times 2 --shout")

# 12. Subcommands with add_subparsers() - a Git-Style CLI
# ------------------------------------
# - Each subcommand (e.g. "add", "remove") gets its own parser with its
#   own arguments, like `git commit -m "..."` vs `git push origin main`.
print("\n# 12. Subcommands with add_subparsers()")
cli = argparse.ArgumentParser(description="Task manager CLI")
subparsers = cli.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add", help="add a task")
add_parser.add_argument("title", help="task title")
add_parser.add_argument("--priority", type=int, default=1)

remove_parser = subparsers.add_parser("remove", help="remove a task")
remove_parser.add_argument("task_id", type=int)

add_result = cli.parse_args(["add", "Buy milk", "--priority", "2"])
print("parsed 'add':", add_result)

remove_result = cli.parse_args(["remove", "5"])
print("parsed 'remove':", remove_result)

# 13. Argument Groups - Organizing --help Output
# ------------------------------------
print("\n# 13. Argument Groups")
grouped_parser = argparse.ArgumentParser(description="Server CLI")
network_group = grouped_parser.add_argument_group("network options")
network_group.add_argument("--host", default="localhost")
network_group.add_argument("--port", type=int, default=8080)

logging_group = grouped_parser.add_argument_group("logging options")
logging_group.add_argument("--log-level", default="INFO")
grouped_parser.print_help()

# 14. Mutually Exclusive Arguments
# ------------------------------------
# - Only one of the group's arguments may be given; passing both errors out.
print("\n# 14. Mutually Exclusive Arguments")
verbosity_parser = argparse.ArgumentParser()
verbosity_group = verbosity_parser.add_mutually_exclusive_group()
verbosity_group.add_argument("--quiet", action="store_true")
verbosity_group.add_argument("--verbose", action="store_true")

print("--quiet alone:", verbosity_parser.parse_args(["--quiet"]))
try:
    verbosity_parser.parse_args(["--quiet", "--verbose"])
except SystemExit:
    print("# - passing both --quiet and --verbose exits with an error, as expected")

# 15. nargs='+' / nargs='*' - Variable-Length Arguments
# ------------------------------------
print("\n# 15. nargs='+' and nargs='*'")
nargs_parser = argparse.ArgumentParser()
nargs_parser.add_argument("--tags", nargs="*", default=[])   # zero or more
nargs_parser.add_argument("files", nargs="+")                 # one or more, required
nargs_result = nargs_parser.parse_args(["a.txt", "b.txt", "--tags", "urgent", "review"])
print("files:", nargs_result.files)
print("tags:", nargs_result.tags)

# 16. Custom type= Validator Function
# ------------------------------------
# - A type= function that raises ArgumentTypeError gives a clean CLI error
#   message instead of an ugly traceback for bad input.
def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return parsed

print("\n# 16. Custom type= Validator")
validator_parser = argparse.ArgumentParser()
validator_parser.add_argument("--count", type=positive_int, default=1)
print("valid input:", validator_parser.parse_args(["--count", "5"]))
try:
    validator_parser.parse_args(["--count", "-3"])
except SystemExit:
    print("# - '-3' fails positive_int() validation, argparse reports it and exits")
