#!/usr/bin/env python3
"""Run the topic notebooks and (optionally) save their outputs.

The notebooks ARE the source: edit them in Jupyter, then re-run this to refresh
the saved outputs so they read well on GitHub.

    python3 tools/run_notebooks.py                  # run every notebook, report failures
    python3 tools/run_notebooks.py --save           # ...and write the outputs into the files
    python3 tools/run_notebooks.py --only Sets      # only paths containing "Sets"
    python3 tools/run_notebooks.py --clear          # remove saved outputs

Needs: nbformat, nbclient, ipykernel.
"""
import argparse
import pathlib
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import nbformat

ROOT = pathlib.Path(__file__).resolve().parent.parent


def notebooks(only=None):
    files = sorted(p for p in ROOT.rglob("[0-9][0-9]-*.ipynb")
                   if "12-Practice-And-Projects" not in p.parts and ".ipynb_checkpoints" not in p.parts)
    return [p for p in files if not only or only in str(p)]


HOME = str(pathlib.Path.home())
TMP = re.compile(r"/(?:private/)?var/folders/[^\s'\"<>)]*|/(?:private/)?tmp/[^\s'\"<>)]*")


def scrub(text):
    """Keep machine-specific paths (home folder, temp dirs, repo location) out of saved outputs."""
    text = text.replace(str(ROOT), "<repo>/Python").replace(HOME, "~")
    return TMP.sub("<tmp>", text)


def scrub_outputs(nb):
    for cell in nb.cells:
        for out in cell.get("outputs", []):
            if "text" in out:
                out["text"] = scrub(out["text"])
            if "traceback" in out:
                out["traceback"] = [scrub(t) for t in out["traceback"]]
            for key in ("text/plain", "text/html"):
                if key in out.get("data", {}):
                    out["data"][key] = scrub(out["data"][key])


def run(args):
    path, save = args
    from nbclient import NotebookClient
    nb = nbformat.read(path, as_version=4)
    try:
        NotebookClient(nb, timeout=600, kernel_name="python3", record_timing=False,
                       resources={"metadata": {"path": str(path.parent)}}).execute()
    except Exception as exc:  # report, never crash the whole run
        lines = [l for l in str(exc).strip().splitlines() if l.strip()]
        return path, (lines[-1] if lines else repr(exc))[:200]
    if save:
        scrub_outputs(nb)
        nbformat.write(nb, path)
    return path, None


def clear(path):
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs, cell.execution_count = [], None
    nbformat.write(nb, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", help="only notebooks whose path contains this text")
    ap.add_argument("--save", action="store_true", help="write outputs into the notebooks")
    ap.add_argument("--clear", action="store_true", help="remove saved outputs and exit")
    ap.add_argument("--jobs", type=int, default=3, help="notebooks to run in parallel (default 3)")
    args = ap.parse_args()
    files = notebooks(args.only)
    if args.clear:
        for p in files:
            clear(p)
        print(f"cleared {len(files)} notebooks")
        return 0
    with ProcessPoolExecutor(args.jobs) as pool:
        results = list(pool.map(run, [(p, args.save) for p in files]))
    bad = [(p, e) for p, e in results if e]
    for p, e in bad:
        print(f"FAIL {p.relative_to(ROOT)}: {e}")
    print(f"{len(results) - len(bad)}/{len(results)} notebooks ran cleanly" + (" (outputs saved)" if args.save else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
