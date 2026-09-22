"""Shared fixtures: keep every test free of a running Reflex app."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_telemetry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never phone home from the test suite."""
    monkeypatch.setenv("TELEMETRY_ENABLED", "false")
