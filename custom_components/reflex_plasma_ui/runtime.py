"""Client-side commands and helpers: the Reflex face of ``usePlasmaRuntime()``.

``pulse`` and ``bump`` return event specs that run entirely in the browser,
so they can be wired straight to a trigger (``on_click=pulse()``) or returned
from a backend event handler (``return pulse(strength=0.8)``).
"""

from __future__ import annotations

import json

import reflex as rx
from reflex.event import EventSpec

#: Attribute that stops a press from starting a drag (buttons, links and
#: inputs are already excluded by the library).
NODRAG_ATTR = "data-plasma-nodrag"
#: ``custom_attrs`` for content inside a draggable surface that must stay clickable.
NO_DRAG: dict[str, str] = {NODRAG_ATTR: "true"}

#: Set on a surface's element while it forms in.
FORMING_ATTR = "data-plasma-forming"
FORMING_EVENT = "plasmaforming"
FORMED_EVENT = "plasmaformed"

#: CSS that holds a surface's children back until the material has formed in.
FORMING_CSS = (
    "[data-plasma-forming] > * { opacity: 0; transition: none; }\n"
    ".plasma-panel > * { transition: opacity 160ms ease-out; }\n"
)


def _js(value: object) -> str:
    if value is None:
        return "undefined"
    if isinstance(value, rx.Var):
        return str(value)
    return json.dumps(value)


def pulse(
    x: float | None = None,
    y: float | None = None,
    strength: float = 1.0,
    provider: str | None = None,
) -> EventSpec:
    """Send a pulse through the plasma.

    Args:
        x: Viewport x (px). Default: where the pointer last went down.
        y: Viewport y (px). Default: where the pointer last went down.
        strength: Pulse strength, 1 is the library default.
        provider: Registry name of the provider (``plasma_provider(name=...)``).

    Returns:
        A frontend-only event spec.
    """
    return rx.call_script(
        f"window.__reflexPlasma?.pulse({_js(x)}, {_js(y)}, {_js(strength)}, {_js(provider)})"
    )


def bump(energy: float = 0.6, provider: str | None = None) -> EventSpec:
    """Add energy to the plasma (it ripples, then settles).

    Args:
        energy: 0-1.
        provider: Registry name of the provider.

    Returns:
        A frontend-only event spec.
    """
    return rx.call_script(f"window.__reflexPlasma?.bump({_js(energy)}, {_js(provider)})")


def pulse_on_press(strength: float = 1.0, provider: str | None = None) -> dict[str, str]:
    """``custom_attrs`` that pulse at the pointer when the element itself is pressed.

    Presses on its children are ignored, so a stage full of panels pulses
    only on its empty space.

    Args:
        strength: Pulse strength.
        provider: Registry name of the provider.

    Returns:
        The attributes to pass as ``custom_attrs``.
    """
    return {"data-plasma-pulse": provider or "", "data-plasma-pulse-strength": str(strength)}


def forming_style() -> rx.Component:
    """A ``<style>`` tag with :data:`FORMING_CSS` (contents fade in after the material).

    Returns:
        The style element.
    """
    return rx.el.style(FORMING_CSS)
