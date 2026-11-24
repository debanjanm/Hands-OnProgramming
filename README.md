# Hands-On Programming

A practical collection of notebooks, exercises and projects covering core
programming concepts across language categories. Everything is a Jupyter
notebook with its output saved, so it reads well right here on GitHub and is
easy to experiment with.

## Structure

| Category | Language(s) | Covers |
|---|---|---|
| [01-GeneralPurposeLanguage](01-GeneralPurposeLanguage/README.md) | Python | 123 notebooks from syntax through OOP and design patterns, async, the standard library, NumPy, Pandas, visualization and applied Python, plus practice exercises and projects |
| [02-DomainSpecificLanguage](02-DomainSpecificLanguage/README.md) | SQL | 38 notebooks on SQLite: querying, windows, patterns, schema design, performance, JSON/FTS, dialects, plus auto-checked practice problems |
| [03-Scripting](03-Scripting/README.md) | Bash | 9 notebooks: shell fundamentals, control flow, functions, strings and arrays, pipes, text tools, files, processes and signals, advanced bash |

Each category folder is named by kind, not by language, so a second language
in the same category (e.g. another general-purpose or scripting language)
slots in as a sibling folder without renaming anything.

## Conventions

- Each notebook starts with a plain-English cheat sheet (what it covers, key
  points, gotchas, when it matters), then numbered sections with the code and
  its saved output side by side.
- Everything runs locally: no internet, no database servers. Notebooks build
  their own data and clean up after themselves.
- Notebooks go beyond basic syntax where it matters: gotchas, performance and
  internals notes, and real-world patterns sit next to the core API.
- Each language folder has its own README with the full topic list and study
  order. Practice work (Python `12-Practice-And-Projects`, SQL `11-Practice`) is
  checked automatically with `pytest`.
