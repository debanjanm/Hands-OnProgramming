#!/usr/bin/env python3
"""Generate a Jupyter notebook next to every topic `.py` file.

The `.py` files stay the source of truth. Notebooks are generated, one-way:
edit the `.py` (or its `.md` notes) and rebuild - changes made inside a
notebook are overwritten on the next build.

    python3 tools/build_notebooks.py              # (re)build every notebook
    python3 tools/build_notebooks.py --only Sets  # only paths containing "Sets"
    python3 tools/build_notebooks.py --check      # build, then execute all
    python3 tools/build_notebooks.py --clean      # delete generated notebooks

How a topic file becomes a notebook
  * each numbered section (`# NN. Title` + `# ----` + comment block) becomes a
    markdown cell (title + explanation) followed by a code cell;
  * the `print("# NN. ...")` lines that only echo the heading are dropped, since
    the markdown cell already shows them;
  * the companion `.md` notes become the first cell;
  * tiny compatibility shims are added only where a notebook differs from a
    script (`__file__`, `input()`, `asyncio.run`);
  * files in SCRIPT_ONLY really need to run as scripts (multiprocessing with the
    spawn start method), so they get a *runner* notebook: it runs the script and
    imports it to experiment with its functions.

Notebooks are saved WITHOUT outputs so git diffs stay small and deterministic.
Needs: nbformat. `--check` also needs nbclient + ipykernel.
"""
import argparse
import pathlib
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = "tools/build_notebooks.py"

HEADER = re.compile(r"^# (\d+)\. (.+?)\s*$")
SEPARATOR = re.compile(r"^# -{5,}")
ECHO = re.compile(r"""^print\((["'])(\\n)*#""")  # print("# ...") / print("\n# ...")

# Files that must stay scripts: worker functions have to be importable by child
# processes (spawn start method), which cells defined in a notebook are not.
SCRIPT_ONLY = {
    "09-Multithreading-And-Multiprocessing": '''# Worker functions live at module level in the .py, so a Pool can pickle them.
from multiprocessing import Pool

if __name__ == "__main__":  # not needed in a notebook, harmless in a script
    with Pool(2) as pool:
        print(pool.map(mod.square, range(8)))
''',
    "12-Multiprocessing-Pool-And-Shared-State": '''# Worker functions live at module level in the .py, so a Pool can pickle them.
from multiprocessing import Pool

with Pool(2) as pool:
    print("square :", pool.map(mod.square, range(8)))
    print("add    :", pool.starmap(mod.add, [(1, 2), (3, 4)]))
''',
}

SHIM_FILE = '# notebook shim: scripts get __file__, notebooks do not\n__file__ = str(__import__("pathlib").Path("{name}.py").resolve())'
# Per-file replacement for the __file__ shim (kept out of the .py files on purpose).
FILE_SHIM_OVERRIDE = {
    # tracemalloc.Filter(True, __file__) selects allocations made in this file; in a
    # notebook, code is compiled from temp files named .../ipykernel_<pid>/<n>.py
    "12-Mutability-And-Memory-Model":
        '# notebook shim: a notebook has no __file__; cells compile to ipykernel temp files\n'
        '__file__ = "*ipykernel_*"',
}
SHIM_INPUT = '''# notebook shim: ipykernel re-installs its own input() before every cell, so patch
# the kernel's raw_input instead; then input() reads sys.stdin like a script does.
import sys
def _input(prompt=""):
    sys.stdout.write(prompt); sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    return line.rstrip("\\n")
get_ipython().kernel.raw_input = _input'''
SHIM_ASYNC = '''# notebook shim: a notebook already has a running event loop, so asyncio.run() and
# asyncio.Runner would fail. Run them on a private loop in a worker thread instead.
import asyncio, concurrent.futures
_real_asyncio_run = asyncio.run
def _run(coro, **kwargs):
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        return pool.submit(_real_asyncio_run, coro, **kwargs).result()
asyncio.run = _run
if hasattr(asyncio, "Runner"):
    _RealRunner = asyncio.Runner
    class _Runner:
        def __init__(self, **kwargs):
            self._pool = concurrent.futures.ThreadPoolExecutor(1)
            self._runner = self._pool.submit(_RealRunner, **kwargs).result()
        def run(self, coro, **kwargs):
            return self._pool.submit(self._runner.run, coro, **kwargs).result()
        def get_loop(self):
            return self._runner.get_loop()
        def close(self):
            self._pool.submit(self._runner.close).result()
            self._pool.shutdown()
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            self.close()
    asyncio.Runner = _Runner'''


def md_from_comments(lines):
    out = []
    for line in lines:
        text = line[2:] if line.startswith("# ") else line[1:]
        out.append(text.rstrip())
    return "\n".join(out).strip()


def split_sections(src):
    """Return (preamble_lines, [(num, title, md_body, code_lines), ...])."""
    lines = src.split("\n")
    heads = [i for i in range(len(lines) - 1)
             if HEADER.match(lines[i]) and SEPARATOR.match(lines[i + 1])]
    if not heads:
        return lines, []
    sections = []
    for n, start in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        m = HEADER.match(lines[start])
        j = start + 2
        body = []
        while j < end and lines[j].startswith("#"):
            body.append(lines[j])
            j += 1
        # drop blank lines, then print() lines that merely echo the heading block
        while j < end and (not lines[j].strip() or ECHO.match(lines[j])):
            j += 1
        sections.append((m.group(1), m.group(2), md_from_comments(body), lines[j:end]))
    return lines[:heads[0]], sections


def read_notes(py):
    md = py.with_suffix(".md")
    if not md.exists():
        return py.stem, ""
    text = md.read_text().strip().split("\n")
    title = re.sub(r"\s+[—-]\s+Notes\s*$", "", text[0].lstrip("# ").strip())
    body = "\n".join(text[1:]).strip()
    body = re.sub(r"^## ", "### ", body, flags=re.M)
    return title, body


def has_code(lines):
    return any(l.strip() and not l.lstrip().startswith("#") for l in lines)


def shims_for(src, name):
    cells = []
    if "__file__" in src:
        cells.append(FILE_SHIM_OVERRIDE.get(name) or SHIM_FILE.format(name=name))
    if re.search(r"stdin|\bpdb\b|(?<![\w.])input\(", src):
        cells.append(SHIM_INPUT)
    if "asyncio.run(" in src:
        cells.append(SHIM_ASYNC)
    return cells


def build(py):
    name = py.stem
    src = py.read_text()
    title, notes = read_notes(py)
    pre, sections = split_sections(src)
    cells = []
    banner = (f"> Generated from [`{py.name}`]({py.name}) by `{MARK}` - edit the `.py` "
              f"(or its `.md` notes), not this notebook. Changes made here are "
              f"overwritten on the next build.")
    cells.append(new_markdown_cell(f"# {title}\n\n{banner}"))
    if notes:
        cells.append(new_markdown_cell("## Quick notes\n\n" + notes))

    if name in SCRIPT_ONLY:
        cells.append(new_markdown_cell(
            "## Why this one is a runner notebook\n\n"
            "Multiprocessing uses the `spawn` start method on macOS and Windows: child "
            "processes re-import the module that defines the worker functions. Functions "
            "defined in a notebook cell cannot be re-imported, so the real code stays in "
            f"[`{py.name}`]({py.name}). This notebook **runs it** and **imports it** so you "
            "can still experiment.\n\n"
            "### Sections in the script\n\n" +
            "\n".join(f"- {n}. {t}" for n, t, _, _ in sections)))
        cells.append(new_markdown_cell("### 1. Run the whole script"))
        cells.append(new_code_cell(
            "import subprocess, sys\n"
            f"run = subprocess.run([sys.executable, \"{py.name}\"], capture_output=True, text=True)\n"
            "print(run.stdout)\n"
            "print(run.stderr)"))
        cells.append(new_markdown_cell(
            "### 2. Import it and experiment\n\nImporting runs the top-level demos "
            "(their printing is silenced here); the `__main__` part is skipped."))
        cells.append(new_code_cell(
            "import contextlib, importlib, io, sys\n"
            "sys.path.insert(0, \".\")\n"
            "with contextlib.redirect_stdout(io.StringIO()):\n"
            f"    mod = importlib.import_module(\"{name}\")\n"
            "print([n for n, v in vars(mod).items()\n"
            "       if callable(v) and getattr(v, \"__module__\", None) == mod.__name__ and not n.startswith(\"_\")])"))
        cells.append(new_code_cell(SCRIPT_ONLY[name]))
    else:
        for shim in shims_for(src, name):
            cells.append(new_code_cell(shim, metadata={"tags": ["notebook-shim"]}))
        if has_code(pre):
            cells.append(new_code_cell("\n".join(pre).strip("\n")))
        for num, sec_title, body, code in sections:
            cells.append(new_markdown_cell(f"## {num}. {sec_title}" + (f"\n\n{body}" if body else "")))
            code_text = "\n".join(code).strip("\n")
            if code_text.strip():
                cells.append(new_code_cell(code_text))

    nb = new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "generated_by": MARK,
    })
    nb.nbformat_minor = 5
    for i, cell in enumerate(nb.cells):
        cell["id"] = f"c{i:04d}"
    nbformat.validate(nb)
    out = py.with_suffix(".ipynb")
    nbformat.write(nb, out)
    return out


def topic_files(only=None):
    files = sorted(p for p in ROOT.rglob("[0-9][0-9]-*.py") if "demo_package" not in p.parts)
    return [p for p in files if not only or only in str(p)]


def execute(nb_path):
    from nbclient import NotebookClient
    nb = nbformat.read(nb_path, as_version=4)
    try:
        NotebookClient(nb, timeout=600, kernel_name="python3",
                       resources={"metadata": {"path": str(nb_path.parent)}}).execute()
        return nb_path, None
    except Exception as exc:  # report, never crash the whole check
        last = [l for l in str(exc).strip().splitlines() if l.strip()]
        return nb_path, (last[-1] if last else repr(exc))[:200]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", help="only files whose path contains this text")
    ap.add_argument("--check", action="store_true", help="execute every notebook after building")
    ap.add_argument("--clean", action="store_true", help="delete generated notebooks")
    args = ap.parse_args()

    if args.clean:
        n = 0
        for nb_path in ROOT.rglob("*.ipynb"):
            if MARK in nb_path.read_text()[:2000] or MARK in nb_path.read_text():
                nb_path.unlink()
                n += 1
        print(f"removed {n} generated notebooks")
        return 0

    built = [build(p) for p in topic_files(args.only)]
    print(f"built {len(built)} notebooks")
    if not args.check:
        return 0
    with ProcessPoolExecutor(4) as pool:
        results = list(pool.map(execute, built))
    bad = [(p, e) for p, e in results if e]
    for p, e in bad:
        print(f"FAIL {p.relative_to(ROOT)}: {e}")
    print(f"{len(results) - len(bad)}/{len(results)} notebooks executed cleanly")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
