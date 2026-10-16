"""reflex-plasma-ui: liquid WebGL panels (Plasma UI) for Reflex."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from . import presets
from .controls import (
    PlasmaAccordion,
    PlasmaAccordionItem,
    PlasmaButton,
    PlasmaSlider,
    PlasmaSwitch,
    PlasmaTab,
    PlasmaTabList,
    PlasmaTabPanel,
    PlasmaTabs,
    plasma_accordion,
    plasma_accordion_item,
    plasma_button,
    plasma_slider,
    plasma_switch,
    plasma_tab,
    plasma_tab_list,
    plasma_tab_panel,
    plasma_tabs,
)
from .plasma_ui import (
    GroundName,
    MaterialName,
    MoodName,
    Plasma,
    PlasmaCanvas,
    PlasmaProvider,
    ThemeName,
    plasma,
    plasma_canvas,
    plasma_provider,
)
from .runtime import (
    FORMED_EVENT,
    FORMING_ATTR,
    FORMING_CSS,
    FORMING_EVENT,
    NO_DRAG,
    NODRAG_ATTR,
    bump,
    forming_style,
    pulse,
    pulse_on_press,
)

__all__ = [
    "FORMED_EVENT",
    "FORMING_ATTR",
    "FORMING_CSS",
    "FORMING_EVENT",
    "NODRAG_ATTR",
    "NO_DRAG",
    "GroundName",
    "MaterialName",
    "MoodName",
    "Plasma",
    "PlasmaAccordion",
    "PlasmaAccordionItem",
    "PlasmaButton",
    "PlasmaCanvas",
    "PlasmaProvider",
    "PlasmaSlider",
    "PlasmaSwitch",
    "PlasmaTab",
    "PlasmaTabList",
    "PlasmaTabPanel",
    "PlasmaTabs",
    "ThemeName",
    "__version__",
    "bump",
    "forming_style",
    "plasma",
    "plasma_accordion",
    "plasma_accordion_item",
    "plasma_button",
    "plasma_canvas",
    "plasma_provider",
    "plasma_slider",
    "plasma_switch",
    "plasma_tab",
    "plasma_tab_list",
    "plasma_tab_panel",
    "plasma_tabs",
    "presets",
    "pulse",
    "pulse_on_press",
]

try:
    __version__ = _version("reflex-plasma-ui")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0+unknown"

