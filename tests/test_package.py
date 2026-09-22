"""The package's public surface: exports, version and typing marker."""

from __future__ import annotations

from pathlib import Path

import pytest
import tomllib

import reflex_plasma_ui

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


def test_declared_dependency_on_reflex() -> None:
    deps = _pyproject()["project"]["dependencies"]
    assert any(d.startswith("reflex") for d in deps)
