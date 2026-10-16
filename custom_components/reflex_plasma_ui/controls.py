"""Reflex wrappers for the Plasma UI controls (``@cruxgarden/plasma-ui`` 0.8.0+).

Each control is (or is built from) ordinary plasma surfaces, so it must sit
inside a :func:`~reflex_plasma_ui.plasma_provider`, fuses with whatever it
touches, and counts toward the provider's ``max_surfaces``. The provider
injects their stylesheet; colors follow ``currentColor``.

Unlike :func:`~reflex_plasma_ui.plasma`, the controls take only serialisable
props, so they import straight from the pinned npm package. The slider is the
one exception: a small wrapper keeps it responsive while bound to state.

Components
----------
* :func:`plasma_button` - a pill-shaped button that pulses when pressed.
* :func:`plasma_switch` - an on/off switch (``role="switch"``).
* :func:`plasma_slider` - a native range input under a plasma track.
* :func:`plasma_tabs`, :func:`plasma_tab_list`, :func:`plasma_tab`,
  :func:`plasma_tab_panel` - tabs fused into one segmented surface.
* :func:`plasma_accordion`, :func:`plasma_accordion_item` - disclosure
  panels fused into one column.
"""

from __future__ import annotations

from typing import Literal

import reflex as rx
from reflex.components.component import field
from reflex.event import no_args_event_spec, passthrough_event_spec
from reflex.utils.imports import ImportDict

from . import _js

ButtonSize = Literal["sm", "md", "lg"]
Orientation = Literal["horizontal", "vertical"]
AccordionType = Literal["single", "multiple"]


class _PlasmaControl(rx.Component):
    """Imports a control by name from the pinned package."""

    library: str | None = _js.NPM_SPEC


class _PlasmaControlSurface(_PlasmaControl):
    """A control that is itself a plasma surface: the per-surface props of ``plasma``.

    ``opacity`` and ``padding`` are plasma props (tint strength, join-aware
    inner padding in px), not CSS.
    """

    radius: rx.Var[float] = field(doc="Corner radius (px). Default: the provider's.")
    lean: rx.Var[float | bool] = field(doc="Lean toward the pointer while standalone (px); False disables.")
    tint: rx.Var[str] = field(doc="Tint color (hex) for this surface.")
    opacity: rx.Var[float] = field(doc="Tint strength for this surface, 0-1.")
    frost: rx.Var[float] = field(doc="Frost for this surface, 0-1.")
    elevation: rx.Var[float] = field(doc="Elevation for this surface, 0-1.")
    padding: rx.Var[float] = field(doc="Inner padding (px); halves on joined edges.")
    fuse: rx.Var[bool] = field(doc="False: never blends or joins with neighbours. Default True.")
    form_in: rx.Var[bool] = field(doc="Override the provider's form-in for this surface.")
    form_out: rx.Var[bool] = field(doc="Override the provider's form-out for this surface.")

    on_join_change: rx.EventHandler[passthrough_event_spec(bool)] = field(
        doc="Fused with / separated from a neighbour."
    )
    on_forming: rx.EventHandler[no_args_event_spec] = field(doc="The form-in started.")
    on_formed: rx.EventHandler[no_args_event_spec] = field(doc="The form-in settled.")


class PlasmaButton(_PlasmaControlSurface):
    """A button that is its own plasma surface.

    Standalone it leans toward the pointer and sends a pulse through the
    material when pressed (none under reduced motion); next to another
    surface it fuses with it. ``on_click`` and every ``<button>`` attribute
    pass through.
    """

    tag = "PlasmaButton"

    solid: rx.Var[bool] = field(doc="Fill the surface with its tint instead of clear glass. Default False.")
    size: rx.Var[ButtonSize] = field(doc='"sm", "md" or "lg". Default "md".')
    type: rx.Var[str] = field(doc='The native button type: "button", "submit" or "reset".')
    disabled: rx.Var[bool] = field(doc="Disable the button.")


class PlasmaSwitch(_PlasmaControlSurface):
    """An on/off switch: the track is a surface that takes on a tint when on.

    With ``label`` the text wraps the switch in a ``<label>`` (clicking it
    toggles, and it names the switch); without one, pass ``aria_label``.
    """

    tag = "PlasmaSwitch"

    checked: rx.Var[bool] = field(doc="Controlled state. Pair with on_checked_change.")
    default_checked: rx.Var[bool] = field(doc="Initial state when uncontrolled.")
    label: rx.Var[str] = field(doc="Text beside the switch; also its accessible name.")
    checked_tint: rx.Var[str] = field(doc="Tint of the track while on (hex). Default a soft green.")
    disabled: rx.Var[bool] = field(doc="Disable the switch.")

    on_checked_change: rx.EventHandler[passthrough_event_spec(bool)] = field(
        doc="Toggled; gets the new checked state."
    )


class PlasmaSlider(_PlasmaControlSurface):
    """A slider: a native ``<input type="range">`` under a plasma track.

    Keyboard, touch and forms are the browser's own. ``aria_label``,
    ``aria_labelledby``, ``aria_valuetext`` and ``id`` go to the input.
    ``on_value_change`` fires on every step, so a backend handler sees each one.
    Bound to state, the slider follows the pointer locally and adopts ``value``
    again once input settles, so steps are not lost to the round-trip.
    """

    library = None
    tag = "ReflexPlasmaSlider"

    value: rx.Var[float] = field(doc="Controlled value. Pair with on_value_change.")
    default_value: rx.Var[float] = field(doc="Initial value when uncontrolled.")
    min: rx.Var[float] = field(doc="Default 0.")
    max: rx.Var[float] = field(doc="Default 100.")
    step: rx.Var[float] = field(doc="Default 1.")
    disabled: rx.Var[bool] = field(doc="Disable the slider.")
    name: rx.Var[str] = field(doc="Form field name for the underlying range input.")

    on_value_change: rx.EventHandler[passthrough_event_spec(float)] = field(doc="Moved; gets the new value.")

    def add_imports(self) -> ImportDict:
        """Import the upstream slider and the React helpers its wrapper uses.

        Returns:
            The imports.
        """
        return {
            "react": ["createElement", "forwardRef", "useCallback", "useEffect", "useRef", "useState"],
            _js.NPM_SPEC: ["PlasmaSlider"],
        }

    def add_custom_code(self) -> list[str]:
        """Slider wrapper.

        Returns:
            The custom JS.
        """
        return [_js.SLIDER_CODE]


class PlasmaTabs(_PlasmaControl):
    """Tabs. The root holds state only; it is not a surface.

    With neither ``value`` nor ``default_value``, the first enabled tab is
    selected after mounting.
    """

    tag = "PlasmaTabs"

    value: rx.Var[str] = field(doc="The selected tab's value (controlled). Pair with on_value_change.")
    default_value: rx.Var[str] = field(doc="Initially selected tab when uncontrolled.")
    orientation: rx.Var[Orientation] = field(
        doc='"horizontal" or "vertical": how the list runs and which arrow keys move. Default "horizontal".'
    )

    on_value_change: rx.EventHandler[passthrough_event_spec(str)] = field(doc="A tab was selected; gets its value.")


class PlasmaTabList(_PlasmaControl):
    """The row (or column) of tabs, laid out flush so they fuse. Give it an ``aria_label``."""

    tag = "PlasmaTabList"


class PlasmaTab(_PlasmaControlSurface):
    """One segment of the tab list: a surface; the selected one takes a tint."""

    tag = "PlasmaTab"

    value: rx.Var[str] = field(doc="Identifies the tab and the plasma_tab_panel it controls.")
    disabled: rx.Var[bool] = field(doc="Disable the tab.")


class PlasmaTabPanel(_PlasmaControl):
    """Content for one tab. Only the selected panel's children are mounted."""

    tag = "PlasmaTabPanel"

    value: rx.Var[str] = field(doc="The value of the tab that shows this panel.")


class PlasmaAccordion(_PlasmaControl):
    """A stack of disclosure panels that fuse into one column of plasma.

    The open items are always a list of values, in both modes. Add a ``gap``
    to its style to keep the items apart instead.
    """

    tag = "PlasmaAccordion"

    type: rx.Var[AccordionType] = field(
        doc='"single" keeps one item open at a time; "multiple" lets any number be. Default "single".'
    )
    value: rx.Var[list[str]] = field(doc="The open items' values (controlled). Pair with on_value_change.")
    default_value: rx.Var[list[str]] = field(doc="Initially open items when uncontrolled.")

    on_value_change: rx.EventHandler[passthrough_event_spec(list[str])] = field(
        doc="An item opened or closed; gets the open items' values."
    )


class PlasmaAccordionItem(_PlasmaControlSurface):
    """One disclosure panel: a surface holding a trigger and its content (the children)."""

    tag = "PlasmaAccordionItem"

    value: rx.Var[str] = field(doc="Identifies the item in the accordion's value.")
    title: rx.Var[str] = field(doc="The always-visible header text.")
    disabled: rx.Var[bool] = field(doc="Disable the item.")
    heading_level: rx.Var[int] = field(doc="Which heading element (1-6) wraps the trigger. Default 3.")


plasma_button = PlasmaButton.create
plasma_switch = PlasmaSwitch.create
plasma_slider = PlasmaSlider.create
plasma_tabs = PlasmaTabs.create
plasma_tab_list = PlasmaTabList.create
plasma_tab = PlasmaTab.create
plasma_tab_panel = PlasmaTabPanel.create
plasma_accordion = PlasmaAccordion.create
plasma_accordion_item = PlasmaAccordionItem.create
