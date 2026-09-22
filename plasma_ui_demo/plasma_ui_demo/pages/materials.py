"""Materials - a Reflex port of the upstream materials proof of concept.

Every material shares one engine (SDF scene, springs, fusing, joins); only the
composite pass differs. Each material also brings its own physics and outline,
which live in ``presets.MATERIAL_PRESETS``.
"""

from __future__ import annotations

import math

import reflex as rx

from reflex_plasma_ui import plasma, plasma_provider, presets, pulse

from ..common import nav_links

GROUNDS = {"Slate": "#16191d", "Paper": "#d9d4cb", "Mid": "#6c6f74", "Ink": "#08090b", "Field": ""}
OPAQUE = {"wood", "stone", "metal"}
LENSES = {"plasma", "crystal"}


class MaterialsState(rx.State):
    """Material, ground, light and outline."""

    material: str = "plasma"
    ground: str = "Slate"
    angle: float = 235.0
    roughness: float = 0.28
    anisotropy: float = 0.0
    frost: float = 0.3
    radius: float = 26.0
    edge: float = 0.0
    edge_scale: float = 0.01
    sharp: float = 0.0

    @rx.event
    def pick(self, material: str):
        """Choose a material and adopt the outline it wants."""
        p = presets.MATERIAL_PRESETS[material]
        self.material = material
        self.radius, self.edge = float(p["radius"]), float(p["edge"])
        self.edge_scale, self.sharp = float(p["edge_scale"]), float(p["edge_sharpness"])

    @rx.event
    def set_ground(self, name: str):
        self.ground = name

    @rx.event
    def set_value(self, key: str, value: float):
        if key in {"angle", "roughness", "anisotropy", "frost", "radius", "edge", "sharp"}:
            setattr(self, key, float(value))

    @rx.var
    def light_dir(self) -> list[float]:
        rad = self.angle * math.pi / 180
        return [round(math.cos(rad), 4), round(math.sin(rad), 4), 0.66]

    @rx.var
    def physics(self) -> dict[str, float]:
        p = presets.MATERIAL_PRESETS[self.material]
        return {k: float(p[k]) for k in ("thickness", "tension", "blend", "viscosity", "stretch")}

    @rx.var
    def background(self) -> str:
        return GROUNDS.get(self.ground, "")

    @rx.var
    def note(self) -> str:
        return presets.MATERIAL_NOTES[self.material]

    @rx.var
    def surface_frost(self) -> float:
        return self.frost if self.material in LENSES else 0.0

    @rx.var
    def elevation(self) -> float:
        return 0.0 if self.material == "cloud" else 0.4

    @rx.var
    def opaque(self) -> bool:
        return self.material in OPAQUE

    @rx.var
    def lens(self) -> bool:
        return self.material in LENSES

    @rx.var
    def grained(self) -> bool:
        return self.material in {"metal", "wood"}


M = MaterialsState


def _ctl(label: str, key: str, lo: float, hi: float, step: float, active=True) -> rx.Component:
    value = getattr(M, key)
    return rx.el.label(
        label,
        rx.el.span(value),
        rx.el.input(type="range", min=lo, max=hi, step=step, value=value, on_change=lambda v: M.set_value(key, v)),
        class_name=rx.cond(active, "", "off"),
    )


def page() -> rx.Component:
    bar = plasma(
        rx.el.a("Materials", href="/", class_name="wordmark"),
        rx.el.div(
            *[
                rx.el.button(m, aria_pressed=rx.cond(M.material == m, "true", "false"), on_click=M.pick(m))
                for m in presets.MATERIALS
            ],
            class_name="seg small",
        ),
        rx.el.div(
            *[
                rx.el.button(g, aria_pressed=rx.cond(M.ground == g, "true", "false"), on_click=M.set_ground(g))
                for g in GROUNDS
            ],
            class_name="seg small",
        ),
        rx.el.button("Send a pulse", class_name="ghost", on_click=pulse()),
        class_name="mbar",
        radius=M.radius,
        padding=14,
        fuse=False,
        lean=False,
    )
    # Bare panels: content comes back once the material itself is right.
    body = rx.el.div(
        plasma(class_name="card", radius=M.radius, lean=False),
        rx.el.div(
            plasma(class_name="card", radius=M.radius, lean=False),
            plasma(class_name="card", radius=M.radius, lean=False),
            class_name="mcol",
        ),
        rx.el.div(
            plasma(class_name="card", radius=M.radius, draggable=True, lean=False, aria_label="Draggable panel"),
            class_name="mcol",
        ),
        class_name="mbody",
    )
    controls = plasma(
        rx.el.div(rx.el.span(M.note, class_name="note"), nav_links("/materials"), class_name="hrow", style={"width": "100%"}),
        rx.el.div(
            _ctl("Light", "angle", 0, 360, 5),
            _ctl("Roughness", "roughness", 0.04, 0.95, 0.01, M.opaque),
            _ctl("Anisotropy", "anisotropy", 0, 1, 0.05, M.grained),
            _ctl("Frost", "frost", 0, 1, 0.05, M.lens),
            _ctl("Corner", "radius", 0, 52, 1),
            _ctl("Edge", "edge", 0, 36, 1),
            _ctl("Ragged", "sharp", 0, 1, 0.05, M.edge > 0),
            class_name="mcontrols",
        ),
        class_name="mbar",
        radius=M.radius,
        padding=14,
        fuse=False,
        lean=False,
    )
    return plasma_provider(
        rx.el.div(bar, body, controls, class_name="mpage"),
        mood="tidal",
        theme="dark",
        background=M.background,
        material=M.material,
        light_dir=M.light_dir,
        roughness=M.roughness,
        anisotropy=M.anisotropy,
        thickness=M.physics["thickness"],
        tension=M.physics["tension"],
        viscosity=M.physics["viscosity"],
        stretch=M.physics["stretch"],
        blend=M.physics["blend"],
        edge=M.edge,
        edge_scale=M.edge_scale,
        edge_sharpness=M.sharp,
        radius=M.radius,
        frost=M.surface_frost,
        elevation=M.elevation,
        grain=0,
        max_surfaces=12,
    )
