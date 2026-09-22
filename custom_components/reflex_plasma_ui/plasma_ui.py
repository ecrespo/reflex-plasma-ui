"""Reflex wrappers for Plasma UI (https://github.com/CruxGarden/plasma-ui).

Plasma UI draws every ``<Plasma>`` surface on the page as one shared WebGL2
plasma behind the DOM: surfaces fuse on contact, refract what is behind them,
stretch when moved and snap to a grid. The DOM stays ordinary HTML.

Components
----------
* :func:`plasma_provider` - owns the renderer and every shared setting.
* :func:`plasma` - marks an element as a plasma surface (drag, snap, fuse...).
* :func:`plasma_canvas` - the canvas element, when the provider is created
  with ``canvas=False`` so you choose where it sits.
"""

from __future__ import annotations

from typing import Any, Literal

import reflex as rx
from reflex.components.component import field
from reflex.event import no_args_event_spec, passthrough_event_spec
from reflex.utils.imports import ImportDict

from . import _js

MoodName = Literal["tidal", "aurora", "ember"]
ThemeName = Literal["auto", "light", "dark"]
MaterialName = Literal["plasma", "crystal", "metal", "mercury", "wood", "stone", "cloud"]
GroundName = Literal["field", "clear"]


def _offset_signature(
    offset: rx.Var[dict[str, float]],
) -> tuple[rx.Var[dict[str, float]]]:
    """JS ``onDragEnd({x, y})`` -> Python handler receives ``{"x": ..., "y": ...}``.

    Args:
        offset: The settled offset.

    Returns:
        The offset, passed through.
    """
    return (offset,)


class _PlasmaBase(rx.Component):
    """Shared import plumbing: every wrapper lives in page-level custom code."""

    # No ``library``: the rendered tag is defined in custom code; the npm
    # package is pulled in (and installed, pinned) through add_imports.
    library = None

    def add_imports(self) -> ImportDict:
        """Import React helpers and the Plasma UI exports the glue code uses.

        Returns:
            The imports.
        """
        return {
            "react": ["createElement", "forwardRef", "useEffect", "useMemo", "useRef", "useState"],
            _js.NPM_SPEC: ["PlasmaProvider", "Plasma", "PlasmaCanvas", "usePlasmaRuntime"],
        }


class PlasmaProvider(_PlasmaBase):
    """Owns the WebGL renderer and every shared plasma setting.

    Every prop maps 1:1 to the React ``<PlasmaProvider>`` (snake_case here,
    camelCase in JS). Leave a prop unset to keep the library default.
    """

    tag = "ReflexPlasmaProvider"

    # --- Reflex-side extras -------------------------------------------------
    name: rx.Var[str] = field(
        doc='Registry name for pulse()/bump(). Default "default". Give overlay providers their own name.'
    )
    background_selector: rx.Var[str] = field(
        doc="CSS selector of an img/canvas/video element to use as the background, "
        'e.g. "canvas.ground" for a clear-ground overlay. Takes precedence over `background`.'
    )

    # --- Look -----------------------------------------------------------------
    mood: rx.Var[MoodName | dict[str, Any]] = field(
        doc='Preset ("tidal", "aurora", "ember") or a custom mood '
        "{colors: [base, mid, accent], blend: px, spring: {stiffness, damping}}."
    )
    theme: rx.Var[ThemeName] = field(
        doc='"auto" follows the OS and <html data-theme>. Tip: theme=rx.color_mode_cond("light", "dark").'
    )
    background: rx.Var[str] = field(
        doc="CSS color (luminance drift) or image URL / data URI (refracted, slow swirl). Omit for the mood field."
    )
    radius: rx.Var[float] = field(doc="Default corner radius (px) for every surface. Default 26.")
    blend: rx.Var[float] = field(doc="Distance (px) at which surfaces start to fuse. Default: the mood's.")
    tint: rx.Var[str] = field(doc='Plasma tint color (hex). Default "#ffffff".')
    opacity: rx.Var[float] = field(doc="Tint strength, 0 (clear) to 1 (solid). Default 0.")
    frost: rx.Var[float] = field(doc="Translucency, 0 (clear) to 1 (frosted). Default 0.")
    elevation: rx.Var[float] = field(doc="Shadow depth, 0 (flat) to 1 (floating). Default 0.35.")
    smoothness: rx.Var[float] = field(doc="Outline smoothing strength. Default 1.")
    refraction: rx.Var[float] = field(doc="Lens strength. Default 1.")
    dispersion: rx.Var[float] = field(doc="Color splitting. Default 1.")
    rim: rx.Var[float] = field(doc="Colored rim strength; 0 turns it off. Default 1.")
    rim_color: rx.Var[str] = field(doc='"iridescent", "tint" (each surface\'s tint) or a hex color.')
    rim_width: rx.Var[float] = field(doc="How far the rim reaches in from the edge. Default 1.")
    highlight: rx.Var[float] = field(doc="Pointer-facing highlight; 0 turns it off. Default 1.")
    edge_line: rx.Var[float] = field(doc="Thin line along the outline; 0 turns it off. Default 1.")
    shimmer: rx.Var[float] = field(doc="Iridescent sheen drifting across each surface. Default 1.")
    shimmer_speed: rx.Var[float] = field(doc="How fast that sheen drifts. Default 1.")
    glow: rx.Var[float] = field(doc="Halo the plasma casts on the background. Default 1.")
    wash: rx.Var[float] = field(doc="The material's own cast on what is seen through it. Default 1.")
    grain: rx.Var[float] = field(doc="Film grain over the background. Default 1.")
    background_blur: rx.Var[float] = field(doc="Blur the whole background, CSS px 0-40. Default 0.")
    ground: rx.Var[GroundName] = field(
        doc='"field" paints the background; "clear" leaves the canvas transparent (overlay providers).'
    )
    preserve_drawing_buffer: rx.Var[bool] = field(
        doc="Keep frames so another provider can sample this canvas. Fixed at creation."
    )

    # --- Material -------------------------------------------------------------
    material: rx.Var[MaterialName] = field(
        doc="plasma, crystal, metal, mercury, wood, stone or cloud. Default plasma."
    )
    light_dir: rx.Var[list[float]] = field(doc="[x, y, z] light direction. Default up-left, front.")
    roughness: rx.Var[float] = field(doc="Metal finish: 0 mirror, 1 chalk. Default 0.28.")
    anisotropy: rx.Var[float] = field(doc="Highlight stretch along the grain. Default 0.")
    edge: rx.Var[float] = field(doc="Outline displacement from the rounded box, px. Default 0.")
    edge_scale: rx.Var[float] = field(doc="Displacement size, cycles/px. Default 0.01.")
    edge_sharpness: rx.Var[float] = field(doc="0 rolls the displaced edge, 1 breaks it. Default 0.")
    thickness: rx.Var[float] = field(doc="Panel thickness as a solid, px. Default 18.")
    tension: rx.Var[float] = field(doc="Surface tension (bead pull, merge eagerness). Default 0.")

    # --- Motion ---------------------------------------------------------------
    viscosity: rx.Var[float] = field(doc="0 watery/bouncy, 1 syrup; scales drag/snap springs. Default 0.5.")
    stretch: rx.Var[float] = field(doc="How far the plasma trails moving panels; 0 off. Default 1.")
    flow: rx.Var[float] = field(doc="Slow ripple along the edges. Default 0.")
    form_in: rx.Var[bool] = field(doc="New surfaces grow from nothing. Default True.")
    form_speed: rx.Var[float] = field(doc="Form in/out speed multiplier. Default 1.")
    form_out: rx.Var[bool] = field(doc="Removed surfaces shrink away. Default False.")

    # --- Pointer & layout -----------------------------------------------------
    pointer_drop: rx.Var[bool] = field(doc="Liquid drop following the pointer. Default True.")
    pointer_pull: rx.Var[bool] = field(doc="Surfaces swell toward a nearby pointer. Default True.")
    ambient_drops: rx.Var[bool] = field(doc="Decorative orbiting drops. Default False.")
    grid: rx.Var[float] = field(doc="Snap grid size, px. Default 24.")
    magnet: rx.Var[float] = field(doc="Edge latch distance, px. Default 40.")

    # --- Rendering ------------------------------------------------------------
    quality: rx.Var[float] = field(doc="Maximum canvas pixel ratio. Default 1.25.")
    freeze_on_scroll: rx.Var[bool] = field(doc="Touch only: pin the frame during a fling. Default False.")
    max_surfaces: rx.Var[int] = field(doc="Visible surface budget (recompiles shaders). Default 16.")
    z_index: rx.Var[int] = field(doc="Canvas z-index. Default -1.")
    canvas: rx.Var[bool] = field(doc="False: render plasma_canvas() yourself. Default True.")

    on_ready: rx.EventHandler[passthrough_event_spec(dict[str, bool])] = field(
        doc='Fires once the renderer exists (or WebGL2 is missing): {"supported": bool, "reduced_motion": bool}.'
    )

    def add_custom_code(self) -> list[str]:
        """Registry, bridge and provider wrapper.

        Returns:
            The custom JS.
        """
        return [_js.REGISTRY_CODE, _js.BRIDGE_CODE, _js.PROVIDER_CODE]


class Plasma(_PlasmaBase):
    """A plasma surface. Children stay ordinary, accessible HTML.

    Note that ``opacity`` and ``padding`` are *plasma* props here (tint
    strength and join-aware inner padding in px), not CSS.
    """

    tag = "ReflexPlasma"

    as_: rx.Var[str] = field(doc='Element to render, e.g. "header", "nav", "section", "a". Default "div".')
    radius: rx.Var[float] = field(doc="Corner radius (px). Default: the provider's.")
    lean: rx.Var[float | bool] = field(doc="Lean toward the pointer while standalone (px); False disables. Default 10.")
    tint: rx.Var[str] = field(doc="Tint color (hex) for this surface.")
    opacity: rx.Var[float] = field(doc="Tint strength for this surface, 0-1.")
    frost: rx.Var[float] = field(doc="Frost for this surface, 0-1.")
    elevation: rx.Var[float] = field(doc="Elevation for this surface, 0-1. Raises while dragging.")
    padding: rx.Var[float] = field(doc="Inner padding (px); halves on joined edges.")
    fuse: rx.Var[bool] = field(doc="False: never blends or joins - for bars, docks, fixed chrome. Default True.")
    draggable: rx.Var[bool] = field(doc="Move freely, snap on release; arrow keys move one grid step.")
    snap: rx.Var[bool] = field(doc="Latch to neighbour edges, else the grid. Default True.")
    group: rx.Var[str] = field(doc="Snap only against surfaces of the same group.")
    bounds_selector: rx.Var[str] = field(
        doc='CSS selector of the drag area / grid origin, e.g. "#stage". Default: the viewport.'
    )
    offset: rx.Var[dict[str, float]] = field(doc="Controlled offset {x, y}; changes spring into place.")
    default_offset: rx.Var[dict[str, float]] = field(doc="Initial offset {x, y} when uncontrolled.")
    form_in: rx.Var[bool] = field(doc="Override the provider's form-in for this surface.")
    form_out: rx.Var[bool] = field(doc="Override the provider's form-out for this surface.")

    on_drag_start: rx.EventHandler[no_args_event_spec] = field(doc="Drag started.")
    on_drag_end: rx.EventHandler[_offset_signature] = field(doc="Drag released; gets the settled {x, y}.")
    on_join_change: rx.EventHandler[passthrough_event_spec(bool)] = field(
        doc="Fused with / separated from a neighbour."
    )
    on_forming: rx.EventHandler[no_args_event_spec] = field(doc="The form-in started.")
    on_formed: rx.EventHandler[no_args_event_spec] = field(doc="The form-in settled - reveal contents here.")

    def add_custom_code(self) -> list[str]:
        """Surface wrapper.

        Returns:
            The custom JS.
        """
        return [_js.SURFACE_CODE]


class PlasmaCanvas(_PlasmaBase):
    """The canvas the plasma is drawn on (use with ``plasma_provider(canvas=False)``).

    It places and styles the element; the renderer still covers the viewport.
    """

    tag = "ReflexPlasmaCanvas"

    z_index: rx.Var[int] = field(doc="Canvas z-index. Default -1.")
    canvas_style: rx.Var[dict[str, Any]] = field(
        doc='Inline style for the canvas (camelCase keys), e.g. {"position": "absolute", "zIndex": 1}.'
    )

    def add_custom_code(self) -> list[str]:
        """Canvas wrapper.

        Returns:
            The custom JS.
        """
        return [_js.CANVAS_CODE]


plasma_provider = PlasmaProvider.create
plasma = Plasma.create
plasma_canvas = PlasmaCanvas.create
