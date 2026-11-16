"""Shared pytest setup for the practice exercises and the capstone projects.

    pytest 12-Practice-And-Projects                 # run YOUR work (exercises/ and projects/*/starter/)
    pytest 12-Practice-And-Projects --solutions     # run the reference answers (solutions/ and projects/*/reference/)

Tests load the code by file path, so exercise files may have any name.
"""
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption("--solutions", action="store_true",
                     help="test solutions/ and projects/*/reference instead of exercises/ and projects/*/starter")


@pytest.fixture(scope="session")
def use_solutions(request):
    return request.config.getoption("--solutions")


@pytest.fixture(scope="session")
def load(use_solutions):
    """load("ex01_fundamentals") -> the module from exercises/ (or solutions/ with --solutions)."""
    folder = "solutions" if use_solutions else "exercises"

    def _load(name):
        path = ROOT / folder / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{folder}_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load
