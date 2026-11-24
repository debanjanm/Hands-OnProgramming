# Interview study reorganization

Goal: learn, revise, and practise Python, SQL, and Bash for an AI Engineer role. ML, DL, GenAI, DSA, and system design remain in separate repositories.

## Phase 1 — Inventory and correctness

- [x] Inventory all 182 notebooks and record destinations, priorities, prerequisites, and practice links in [the notebook map](docs/notebook-map.csv).
- [x] Fix the 12 audited defects and add focused regression checks.
- [x] Validate the reference solutions and affected notebooks on supported environments.

## Phase 2 — Physical reorganization

- [ ] Move notebooks and companion files using the map.
- [ ] Repair links, runner exclusions, imports, and instructions.
- [ ] Document the migration and validate all destinations.

## Phase 3 — Reference notebook pattern

- [ ] Refactor Python Functions, SQL Joins, and Bash Fundamentals.
- [ ] Verify rendered structure, questions, answers, and fresh-kernel execution.

## Phase 4 — Chapter batches

- [ ] Apply layered lessons to Python.
- [ ] Apply layered lessons to SQL.
- [ ] Apply layered lessons to Bash.
- [ ] Split long demonstrations, review repeated teaching, and retain useful advanced material.

## Phase 5 — Study experience and final checks

- [ ] Publish learn, revise, and practise routes and chapter indexes.
- [ ] Connect lessons to existing exercises and capstones.
- [ ] Validate all notebooks, local links, reference tests, and compatibility.

## Notebook contract

Start here → Quick revision → Core lesson → Interview questions → Practice → Answers → Advanced reference → Completion check.

Use Essential, Useful, and Advanced as editorial priorities. Keep outputs concise and local, preserve useful examples, and avoid duplicate curriculum copies. Ordinary teaching cells should be 5–25 lines where possible; review those over 40. Runtime setup is labelled separately.

## Safeguards

Preserve the 12 user-created untracked Bash notebooks. Do not stage or commit automatically. Record completed work and validation honestly; an unchecked phase is unfinished. Python 3.10 support is retained with feature guards, and tests should cover compatible NumPy 1.26/2 and Pandas 2/3 environments.

## Current checkpoint

Only Phase 1 has been applied. The later-phase draft is saved outside this repository. Original folders and notebook teaching structure are retained so this phase can be reviewed independently. Phase 1 is complete. See [validation results](docs/VALIDATION.md). Stop here before Phase 2.

The `original_path` column in the notebook map names the current file; `path` records the proposed destination for Phase 2. All rows remain `Inventoried` until files are moved.
