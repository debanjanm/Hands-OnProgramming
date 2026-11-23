# Bash

Every topic is a Jupyter notebook: a plain-English cheat sheet at the top, then numbered
sections with the commands and their real output side by side.

```bash
pip install jupyterlab
jupyter lab 01-Basics/01-Fundamentals.ipynb
```

**One shell for the whole notebook.** Cells start with `%%bash` (a small helper defined in the
first code cell). All cells of a notebook share one bash session, so variables, functions and the
working directory carry over from cell to cell, like a terminal. stdout and stderr appear in
order. A cell whose last command fails stops with an error, unless it is marked `expect_fail`
(to show a failure on purpose). `fresh` runs a cell in a brand-new shell, for `set -e`, `exit`
and `trap` demos. The session starts in a private empty temp folder and the notebook cleans it up.

```bash
python3 tools/run_notebooks.py                # run every notebook, report failures
python3 tools/run_notebooks.py --save         # ...and save the outputs into the files
python3 tools/run_notebooks.py --only Pipes   # one topic
```

## Which bash? Which tools?

The saved outputs were produced with **bash 3.2.57** (the one macOS ships at `/bin/bash`) and
the **BSD** versions of `sed`, `awk`, `grep`, `find`, `stat` and `xargs`. Features that need
bash 4 or 5 (associative arrays, `mapfile`, `${var^^}`, `;&`, `wait -n`, `coproc`) appear
as clearly labelled blocks that are **not run here**, and each notebook points out where GNU
tools (Linux) behave differently. Statements about GNU tools or newer bash versions come from
their documentation and have not been run on this machine: check them against yours.

## Topics (9 notebooks)

| Notebook | Covers |
|---|---|
| [01-Basics/01-Fundamentals](01-Basics/01-Fundamentals.ipynb) | The ground floor of every bash script: how a script gets run (shebang, `bash script`, `./script`, `source`), variables, the three kinds of quoting (plus `$'...'`), word splitting and globbing, command substitution,... |
| [01-Basics/02-Control-Flow](01-Basics/02-Control-Flow.ipynb) | Making decisions and repeating work: `test`, `[ ]` and `[[ ]]`, file / string / numeric tests, `if` / `elif` / `else`, `case`, `for` (lists, C-style, globs, `"$@"`), `while` / `until`, reading lines safely, `break` /... |
| [01-Basics/03-Functions-And-Arguments](01-Basics/03-Functions-And-Arguments.ipynb) | Defining functions (two syntaxes), calling them, and how arguments arrive as `$1 $2 ... $#`. |
| [01-Basics/04-Strings-And-Arrays](01-Basics/04-Strings-And-Arrays.ipynb) | Parameter expansion in full: length, substrings, removing prefixes/suffixes, replacing, defaults. |
| [02-Streams-And-Text/01-Pipes-And-Redirection](02-Streams-And-Text/01-Pipes-And-Redirection.ipynb) | The three standard streams (stdin 0, stdout 1, stderr 2) and file descriptors in general. |
| [02-Streams-And-Text/02-Text-Processing-Tools](02-Streams-And-Text/02-Text-Processing-Tools.ipynb) | The classic Unix text toolbox: `grep`, `sed`, `awk`, `cut`, `paste`, `join`, `sort`, `uniq`, `tr`, `wc`, `head`, `tail`, `rev`, `fold`, `column`, `comm`, `diff`, `nl`, `expand`. |
| [03-Files-And-System/01-File-System-Ops](03-Files-And-System/01-File-System-Ops.ipynb) | Testing files (`[ -f ]`, `-d`, `-e`, `-L`, `-nt` ...), listing (`ls -l`), creating trees (`mkdir -p`, brace expansion). |
| [03-Files-And-System/02-Process-And-Job-Control](03-Files-And-System/02-Process-And-Job-Control.ipynb) | What a process is, and how it differs from a program on disk |
| [04-Scripting-Craft/01-Advanced-Bash](04-Scripting-Craft/01-Advanced-Bash.ipynb) | Process substitution, heredocs and herestrings |

## Planned next

Notebooks for argument parsing (`getopts`), regular expressions, `jq`, archives and checksums,
environment and config files, debugging and testing scripts, robust scripts, POSIX `sh`
portability, performance and security, then practice problems and projects.
