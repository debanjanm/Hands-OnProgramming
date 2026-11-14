# Unittest Basics — Notes

## What this covers
Python's built-in `unittest` testing framework — writing automated checks (test cases, assertions, setup/teardown, mocking) that catch regressions instead of manually re-verifying behavior.

## Key points
- **`class TestX(unittest.TestCase)`** — subclass `TestCase`; every method starting with `test_` is a separate check.
- **Common assertions** — `assertEqual`, `assertTrue`/`assertFalse`, `assertIsNone`, `assertIn`, `assertAlmostEqual` (for floats), `assertRaises` (as context manager, to check an exception is raised).
- **`setUp()` / `tearDown()`** — run before/after *every* test method in the class, for fresh state and cleanup.
- **Running tests** — `unittest.TestLoader().loadTestsFromModule(...)` + `TextTestRunner().run(suite)`; check `result.testsRun`, `.failures`, `.errors`.
- **`pytest`** (third-party, not in this file's imports but referenced) is the more popular modern alternative — simpler syntax, no class boilerplate — but `unittest` ships with Python, nothing to install.
- **`unittest.mock`** — `Mock()` stands in for any object, records calls; `patch("module.thing", return_value=...)` temporarily replaces a real object during a `with` block, restoring it afterward.
- **`assertRaises(...) as ctx`** — inspect the actual exception via `ctx.exception` (e.g. check its message).
- **`subTest(a=a, b=b)`** — parameterize a test loop so each iteration is reported as a separate result, instead of stopping at the first failure.
- **`@unittest.skip("reason")`** / **`@unittest.skipIf(condition, "reason")`** — skip tests conditionally.
- **Test discovery** — `python -m unittest discover -s tests -p 'test_*.py'` auto-finds tests across a project without importing each file by hand.

## Gotchas (the part worth revising twice)
- `patch()` only replaces the target for the duration of its `with` block (or decorated function) — the real object is restored automatically afterward; don't forget it's scoped.
- Without `subTest()`, a loop of assertions stops reporting at the first failure — `subTest()` lets every case in the loop report independently.
- `setUp()`/`tearDown()` run before/after **each** test method, not once for the whole class — don't rely on state persisting between test methods.
- A skipped test (`@unittest.skip`) still counts in the run summary as "skipped", separate from pass/fail — check `result.skipped` if you need that count.

## When it matters
Any code you want to protect from silent regressions — refactoring safely, verifying edge cases (like divide-by-zero), or replacing slow/external dependencies (network calls) with mocks during tests.

## One-line recap example
```python
import unittest
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
```
