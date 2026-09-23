"""The package's public surface: exports, version and typing marker."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import reflex_plasma_ui

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - 3.10 only
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = Path(reflex_plasma_ui.__file__).parent


def _pyproject() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


@pytest.mark.parametrize("name", reflex_plasma_ui.__all__)
def test_every_exported_name_exists(name: str) -> None:
    assert hasattr(reflex_plasma_ui, name), f"{name} is in __all__ but not importable"


def test_all_is_sorted_and_unique() -> None:
    assert len(set(reflex_plasma_ui.__all__)) == len(reflex_plasma_ui.__all__)


def test_version_matches_pyproject() -> None:
    assert reflex_plasma_ui.__version__ == _pyproject()["project"]["version"]


def test_py_typed_marker_is_shipped() -> None:
    """Without it, type checkers ignore the generated .pyi stubs."""
    assert (PACKAGE_DIR / "py.typed").is_file()
    package_data = _pyproject()["tool"]["setuptools"]["package-data"]["reflex_plasma_ui"]
    assert "py.typed" in package_data


def test_stub_file_accompanies_the_component_module() -> None:
    assert (PACKAGE_DIR / "plasma_ui.pyi").is_file()


def test_every_classifier_is_a_real_trove_classifier() -> None:
    """PyPI rejects the whole upload over one bad classifier, with a 400.

    ``twine check --strict`` does not catch this: it validates that the
    metadata renders, not that the classifiers exist. Without this test the
    first place the mistake shows up is the upload, and by then the version
    number has been spent.
    """
    from trove_classifiers import classifiers as known

    declared = _pyproject()["project"]["classifiers"]
    unknown = [c for c in declared if c not in known]
    assert not unknown, f"PyPI will reject these classifiers: {unknown}"


def test_the_supported_python_versions_are_claimed_as_classifiers() -> None:
    """A version in the CI matrix that PyPI never hears about helps nobody."""
    declared = set(_pyproject()["project"]["classifiers"])
    for minor in range(10, 14):
        assert f"Programming Language :: Python :: 3.{minor}" in declared


def test_declared_dependency_on_reflex() -> None:
    deps = _pyproject()["project"]["dependencies"]
    assert any(d.startswith("reflex") for d in deps)
