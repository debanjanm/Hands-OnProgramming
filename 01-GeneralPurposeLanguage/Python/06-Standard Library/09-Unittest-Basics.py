import unittest

# 01. unittest - Introduction
# ------------------------------------
# - Python's built-in testing framework - write automated checks that catch
#   regressions instead of manually re-checking behavior by hand.
# - pytest (third-party, `pip install pytest`) is the more popular modern
#   choice - simpler syntax, no boilerplate class needed - but unittest
#   ships with Python and needs nothing installed.

print("# 01. unittest - Introduction")
print("# ------------------------------------")

# 02. Code Under Test
# ------------------------------------
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# 03. Writing a Test Case
# ------------------------------------
# - Subclass unittest.TestCase; each method starting with `test_` is a check.
class TestMathFunctions(unittest.TestCase):

    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

    def test_divide_normal(self):
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

    def test_common_assertions(self):
        self.assertTrue(3 > 2)
        self.assertFalse(2 > 3)
        self.assertIsNone(None)
        self.assertIn(3, [1, 2, 3])
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=5)

# 04. setUp() and tearDown() - Run Before/After Each Test
# ------------------------------------
class TestWithSetup(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3]  # fresh state before every test method

    def tearDown(self):
        self.data = None  # cleanup after every test method

    def test_data_length(self):
        self.assertEqual(len(self.data), 3)

    def test_data_sum(self):
        self.assertEqual(sum(self.data), 6)

print("\n# 02-04. Test Cases Defined (see run below)")

# 05. Running the Tests
# ------------------------------------
print("\n# 05. Running the Tests")
suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# 06. Reading Results
# ------------------------------------
print("\n# 06. Reading Results")
print(f"tests run: {result.testsRun}, failures: {len(result.failures)}, errors: {len(result.errors)}")

# 07. pytest Equivalent (reference, not executed - requires `pip install pytest`)
# ------------------------------------
print("\n# 07. pytest Equivalent (reference)")
print("# def test_add():")
print("#     assert add(2, 3) == 5")
print("#")
print("# def test_divide_by_zero():")
print("#     with pytest.raises(ValueError):")
print("#         divide(10, 0)")
print("# Run with: pytest test_file.py")

# 08. unittest.mock - Mock() and patch() for Replacing Dependencies
# ------------------------------------
# - Mock() stands in for any object; calls/attribute access are recorded.
# - patch() temporarily replaces a real object (e.g. an external API call)
#   with a Mock, then restores the original when the `with` block ends.
from unittest.mock import Mock, patch

def fetch_price(client, symbol):
    return client.get_price(symbol)  # imagine this hits a real network API

print("\n# 08. unittest.mock - Mock() and patch()")
fake_client = Mock()
fake_client.get_price.return_value = 42.50
print("mocked call result:", fetch_price(fake_client, "AAPL"))
print("was it called with 'AAPL'?", fake_client.get_price.call_args)

def get_current_dir():
    import os
    return os.getcwd()

with patch("os.getcwd", return_value="/fake/path"):
    print("patched os.getcwd():", get_current_dir())
print("real os.getcwd() after the `with` block ends:", get_current_dir())

# 09. assertRaises as a Context Manager - Inspecting the Exception
# ------------------------------------
print("\n# 09. assertRaises Context Manager")
try:
    class TestDivideMessage(unittest.TestCase):
        def test_message(self):
            with self.assertRaises(ValueError) as ctx:
                divide(10, 0)
            self.assertEqual(str(ctx.exception), "Cannot divide by zero")

    single_result = unittest.TextTestRunner(verbosity=0).run(
        unittest.TestLoader().loadTestsFromTestCase(TestDivideMessage)
    )
    print("passed:", single_result.wasSuccessful())
except Exception as e:
    print("unexpected error:", e)

# 10. subTest() - Parameterizing Tests Without Extra Test Methods
# ------------------------------------
class TestAddParameterized(unittest.TestCase):
    def test_add_many_cases(self):
        cases = [(1, 1, 2), (2, 3, 5), (-1, 1, 0), (0, 0, 0)]
        for a, b, expected in cases:
            with self.subTest(a=a, b=b):  # each iteration reported separately
                self.assertEqual(add(a, b), expected)

print("\n# 10. subTest() Parameterized Tests")
sub_result = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromTestCase(TestAddParameterized)
)
print("all cases passed:", sub_result.wasSuccessful())

# 11. Skipping Tests
# ------------------------------------
class TestSkipping(unittest.TestCase):
    @unittest.skip("demonstration - always skipped")
    def test_always_skipped(self):
        self.fail("should never run")

    @unittest.skipIf(1 + 1 != 2, "math is broken, skip")
    def test_runs_because_condition_false(self):
        self.assertEqual(1 + 1, 2)

print("\n# 11. Skipping Tests")
skip_result = unittest.TextTestRunner(verbosity=2).run(
    unittest.TestLoader().loadTestsFromTestCase(TestSkipping)
)
print("skipped count:", len(skip_result.skipped))

# 12. Test Discovery (reference - not run here)
# ------------------------------------
print("\n# 12. Test Discovery (reference)")
print("# - unittest can auto-find tests across a project without importing")
print("#   each file by hand:")
print("#   python -m unittest discover -s tests -p 'test_*.py'")
