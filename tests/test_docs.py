"""The README is the PyPI page - keep its examples and names honest."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import reflex_plasma_ui

README = Path(__file__).resolve().parents[1] / "README.md"
TEXT = README.read_text(encoding="utf-8")

ALL_BLOCKS = re.findall(r"```python\n(.*?)```", TEXT, re.DOTALL)
#: Blocks using ``...name...`` placeholders are sketches, not runnable code.
SKETCH = re.compile(r"\.\.\.\w+\.\.\.")
PYTHON_BLOCKS = [b for b in ALL_BLOCKS if not SKETCH.search(b)]


def test_the_readme_has_runnable_looking_examples() -> None:
    assert len(PYTHON_BLOCKS) >= 3


def test_sketch_blocks_are_the_exception() -> None:
    """Most examples must be real code, or this file stops checking anything."""
    assert len(PYTHON_BLOCKS) > len(ALL_BLOCKS) - len(PYTHON_BLOCKS)


@pytest.mark.parametrize("index", range(len(PYTHON_BLOCKS)))
def test_every_python_block_parses(index: int) -> None:
    ast.parse(PYTHON_BLOCKS[index])


def test_every_name_imported_from_the_package_in_the_readme_exists() -> None:
    imported: set[str] = set()
    for block in PYTHON_BLOCKS:
        for node in ast.walk(ast.parse(block)):
            if isinstance(node, ast.ImportFrom) and node.module == "reflex_plasma_ui":
                imported |= {alias.name for alias in node.names}
    assert imported, "no example imports from the package"
    missing = imported - set(reflex_plasma_ui.__all__)
    assert not missing, f"the README imports names the package does not export: {sorted(missing)}"


def test_the_readme_pins_the_same_npm_version_as_the_code() -> None:
    from reflex_plasma_ui import _js

    assert _js.NPM_SPEC in TEXT, f"the README should document the pinned {_js.NPM_SPEC}"


def test_the_readme_names_the_installable_package() -> None:
    assert "pip install reflex-plasma-ui" in TEXT


def test_the_license_is_stated_and_present() -> None:
    assert "MIT" in TEXT
    assert (README.parent / "LICENSE").is_file()
