"""reflex-plasma-ui: liquid WebGL panels (Plasma UI) for Reflex."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from . import presets
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
    "PlasmaCanvas",
    "PlasmaProvider",
    "ThemeName",
    "__version__",
    "bump",
    "forming_style",
    "plasma",
    "plasma_canvas",
    "plasma_provider",
    "presets",
    "pulse",
    "pulse_on_press",
]

try:
    __version__ = _version("reflex-plasma-ui")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0+unknown"

