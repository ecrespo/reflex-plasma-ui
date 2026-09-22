"""Playground - a Reflex port of the Plasma UI docs playground.

Every provider prop is backend state; drag panels, change looks, watch the
generated Python snippet follow along.
"""

from __future__ import annotations

import random
from typing import Any

import reflex as rx

from reflex_plasma_ui import plasma, plasma_provider, presets, pulse, pulse_on_press

from ..common import color_field, nav, select_field, slider, toggle

PANEL_W, PANEL_H = 216, 144
PANEL_SEED = [
    ("Inbox", "4 unread, 2 flagged."),
    ("Tasks", "Ship the release notes."),
    ("Player", "Side B, 12:41 remaining."),
    ("Notes", "Draft for Thursday's demo."),
    ("Files", "23 items, 1.2 GB."),
    ("Metrics", "Up 12% this week."),
    ("Chat", "3 people online."),
    ("Calendar", "Next: standup at 10."),
]
PANEL_COLORS = ["#ff5fa2", "#5fd4ff", "#b58cff", "#ffb347", "#6cf2a8", "#ff7a5c", "#7c9bff", "#f4e36b"]
WIDE = [(1, 1), (10, 1), (19, 5), (4, 13), (13, 16), (19, 17), (1, 20), (19, 23)]
NARROW = [(0, 1), (0, 7), (5, 14), (0, 21), (5, 21), (0, 27), (5, 27), (0, 33)]

NUMERIC = {
    "blend", "refraction", "dispersion", "rim", "radius", "opacity", "frost", "elevation",
    "viscosity", "stretch", "flow", "rim_width", "highlight", "edge_line", "shimmer",
    "shimmer_speed", "glow", "wash", "grain", "background_blur", "smoothness", "grid", "magnet",
}
TEXT = {"mood", "theme", "tint", "rim_style", "rim_hex"}
BOOLS = {"panel_colors", "pointer_drop", "pointer_pull", "ambient_drops"}

DEFAULTS: dict[str, Any] = dict(
    mood="tidal", theme="dark", blend=40.0, refraction=1.0, dispersion=1.0, rim=1.0, radius=26.0,
    tint="#ffffff", opacity=0.0, frost=0.0, elevation=0.35, panel_colors=False, viscosity=0.5,
    stretch=1.0, flow=0.0, rim_style="iridescent", rim_hex="#9ff3e4", rim_width=1.0, highlight=1.0,
    edge_line=1.0, shimmer=1.0, shimmer_speed=1.0, glow=1.0, wash=1.0, grain=1.0,
    background_blur=0.0, smoothness=1.0, pointer_drop=True, pointer_pull=True,
    ambient_drops=False, grid=24.0, magnet=40.0,
)
# Props the generated snippet never lists (UI-only or expressed differently).
SNIPPET_SKIP = {"theme", "panel_colors", "rim_style", "rim_hex"}


def _look_patch(name: str) -> dict[str, Any]:
    """A playground look expressed in this page's state fields."""
    patch = dict(presets.LOOKS[name])
    rim_color = patch.pop("rim_color", "iridescent")
    if rim_color.startswith("#"):
        patch["rim_style"], patch["rim_hex"] = "color", rim_color
    else:
        patch["rim_style"] = rim_color
    patch["panel_colors"] = False
    return {k: (float(v) if k in NUMERIC else v) for k, v in patch.items()}


class PlaygroundState(rx.State):
    """Every provider setting of the playground, plus the panel layout."""

    look: str = "lumen"
    mood: str = "tidal"
    theme: str = "dark"
    blend: float = 40.0
    refraction: float = 1.0
    dispersion: float = 1.0
    rim: float = 1.0
    radius: float = 26.0
    tint: str = "#ffffff"
    opacity: float = 0.0
    frost: float = 0.0
    elevation: float = 0.35
    panel_colors: bool = False
    viscosity: float = 0.5
    stretch: float = 1.0
    flow: float = 0.0
    rim_style: str = "iridescent"
    rim_hex: str = "#9ff3e4"
    rim_width: float = 1.0
    highlight: float = 1.0
    edge_line: float = 1.0
    shimmer: float = 1.0
    shimmer_speed: float = 1.0
    glow: float = 1.0
    wash: float = 1.0
    grain: float = 1.0
    background_blur: float = 0.0
    smoothness: float = 1.0
    pointer_drop: bool = True
    pointer_pull: bool = True
    ambient_drops: bool = False
    grid: float = 24.0
    magnet: float = 40.0

    count: int = 5
    offsets: list[dict[str, float]] = [
        {"x": float(cx * 24), "y": float(cy * 24)} for cx, cy in WIDE
    ]
    joined: list[bool] = [False] * len(PANEL_SEED)
    supported: bool = True
    ready: bool = False

    # ---- derived -------------------------------------------------------------
    @rx.var
    def rim_color(self) -> str:
        """What the provider's rim_color prop receives."""
        return self.rim_hex if self.rim_style == "color" else self.rim_style

    @rx.var
    def joined_count(self) -> int:
        """Joined panels among the visible ones."""
        return sum(1 for j in self.joined[: self.count] if j)

    @rx.var
    def panels(self) -> list[dict[str, Any]]:
        """The visible panels with everything their surface needs."""
        out = []
        for i in range(self.count):
            title, body = PANEL_SEED[i]
            tint = PANEL_COLORS[i] if self.panel_colors else self.tint
            opacity = max(self.opacity, 0.35) if self.panel_colors else self.opacity
            amt = round(min(max(opacity, 0), 1) * 40)
            out.append({
                "title": title,
                "body": body,
                "tint": tint,
                "opacity": opacity,
                "offset": self.offsets[i],
                "status": "Joined" if self.joined[i] else "Standalone",
                "plate": f"color-mix(in srgb, {tint} {amt}%, var(--plate))",
                "label": f"{title} panel. Use arrow keys to move.",
            })
        return out

    @rx.var
    def code(self) -> str:
        """The Python that reproduces the current look."""
        props = []
        for key, default in DEFAULTS.items():
            if key in SNIPPET_SKIP:
                continue
            value = getattr(self, key)
            if value != default or key == "mood":
                if isinstance(value, bool):
                    props.append(f"{key}={value}")
                elif isinstance(value, str):
                    props.append(f'{key}="{value}"')
                else:
                    props.append(f"{key}={value:g}")
        if self.theme != "auto":
            props.append(f'theme="{self.theme}"')
        if self.rim_style != "iridescent":
            props.append(f'rim_color="{self.rim_color}"')
        panel = 'draggable=True, bounds_selector="#stage", padding=20'
        if self.panel_colors:
            panel += f', tint="{PANEL_COLORS[0]}", opacity={max(self.opacity, 0.35):g}'
        lines = ",\n    ".join(props)
        return (
            "from reflex_plasma_ui import plasma, plasma_provider\n\n"
            "plasma_provider(\n"
            f"    plasma(rx.el.h3(\"Inbox\"), {panel}),\n"
            f"    {lines},\n"
            ")"
        )

    @rx.var
    def plate_bg(self) -> str:
        """The CSS plates follow the tint, like the upstream docs."""
        amt = round(min(max(self.opacity, 0), 1) * 40)
        return f"color-mix(in srgb, {self.tint} {amt}%, var(--plate))"

    @rx.event
    def init_theme(self):
        """Mirror the current theme onto <html> when the page loads."""
        return _apply_theme(self.theme)

    # ---- settings ------------------------------------------------------------
    @rx.event
    def set_num(self, key: str, value: float):
        """Set a numeric setting from a range input."""
        if key in NUMERIC:
            setattr(self, key, float(value))
            self.look = ""

    @rx.event
    def set_text(self, key: str, value: str):
        """Set a string setting."""
        if key in TEXT:
            setattr(self, key, value)
            self.look = ""
            if key == "theme":
                return _apply_theme(value)

    @rx.event
    def flip(self, key: str):
        """Toggle a boolean setting."""
        if key in BOOLS:
            setattr(self, key, not getattr(self, key))
            self.look = ""

    @rx.event
    def apply_look(self, name: str):
        """Apply one of the six nav looks."""
        for key, value in _look_patch(name).items():
            setattr(self, key, value)
        self.look = name

    @rx.event
    def apply_motion(self, name: str):
        """Apply a motion preset."""
        for key, value in presets.MOTIONS[name].items():
            setattr(self, key, float(value))
        self.look = ""

    @rx.event
    def reset_all(self):
        """Back to the defaults (the Lumen look)."""
        for key, value in DEFAULTS.items():
            setattr(self, key, value)
        self.look = "lumen"
        return _apply_theme("dark")

    @rx.event
    def on_ready(self, info: dict[str, bool]):
        """Renderer ready (or WebGL2 missing)."""
        self.ready = True
        self.supported = info.get("supported", False)

    # ---- layout --------------------------------------------------------------
    @rx.event
    def compose(self, width: int | float | None):
        """The starting composition: a flush pair, a stepped neighbour, a stepped pair."""
        w = float(width or 700)
        cells = WIDE if w >= 680 else NARROW
        self.offsets = [
            {"x": float(min(cx * 24, max(0, w - PANEL_W))), "y": float(cy * 24)} for cx, cy in cells
        ]

    @rx.event
    def arrange(self, width: int | float | None):
        """Line the panels up flush, so they read as one surface."""
        w = float(width or 700)
        g = self.grid
        cols = min(max(1, int((w - g) // PANEL_W)), 4)
        self.offsets = [
            {"x": g + (i % cols) * PANEL_W, "y": g + (i // cols) * PANEL_H} for i in range(len(PANEL_SEED))
        ]

    @rx.event
    def scatter(self, size: dict[str, float] | None):
        """Drop the panels on random grid cells."""
        size = size or {}
        w, h, g = size.get("w", 700), size.get("h", 600), self.grid
        cx, cy = max(1, int((w - PANEL_W) // g)), max(1, int((h - PANEL_H) // g))
        # Scattering panels on screen: an ordinary PRNG is exactly right here.
        self.offsets = [
            {"x": float(random.randrange(cx) * g), "y": float(random.randrange(cy) * g)}  # noqa: S311  # nosec B311
            for _ in PANEL_SEED
        ]

    @rx.event
    def add_panel(self):
        """Show one more panel."""
        self.count = min(self.count + 1, len(PANEL_SEED))

    @rx.event
    def remove_panel(self):
        """Hide the last panel (it forms out)."""
        self.count = max(self.count - 1, 1)
        self.joined[self.count] = False

    @rx.event
    def drag_end(self, index: int, offset: dict[str, float]):
        """Keep the settled offset so the layout survives re-renders."""
        self.offsets[index] = {"x": float(offset["x"]), "y": float(offset["y"])}

    @rx.event
    def set_joined(self, index: int, joined: bool):
        """A panel fused with, or separated from, a neighbour."""
        self.joined[index] = joined


def _apply_theme(theme: str):
    """Mirror the provider theme onto <html data-theme> so the CSS follows."""
    if theme == "auto":
        return rx.call_script("delete document.documentElement.dataset.theme")
    return rx.call_script(f"document.documentElement.dataset.theme = '{theme}'")


STAGE_WIDTH = "document.getElementById('stage')?.clientWidth || 700"
STAGE_SIZE = "(() => { const s = document.getElementById('stage'); return { w: s?.clientWidth || 700, h: s?.clientHeight || 600 }; })()"

S = PlaygroundState


def _num(label: str, key: str, lo: float, hi: float, step: float, unit: str = "") -> rx.Component:
    return slider(label, getattr(S, key), lambda v: S.set_num(key, v), lo, hi, step, unit)


def hero() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            plasma(
                rx.el.h1("Plasma UI"),
                rx.el.p(
                    "Liquid panels for Reflex, rendered in WebGL on canvas. Every panel is one shared "
                    "plasma: they fuse on contact, refract what's behind them, and snap to a grid.",
                    class_name="lede",
                ),
                rx.el.div(
                    rx.el.a("Open the playground", href="#playground", class_name="btn primary"),
                    rx.el.button("Send a pulse", class_name="btn", on_click=pulse()),
                    class_name="row",
                ),
                rx.el.p(
                    rx.cond(
                        S.supported,
                        "Rendered with WebGL2. Best on a desktop: the effect is GPU-heavy.",
                        "WebGL2 is unavailable here, so every surface falls back to frosted CSS.",
                    ),
                    class_name="hero-note",
                ),
                class_name="hero-title",
                radius=36,
            ),
            plasma(rx.el.code("pip install reflex-plasma-ui"), class_name="hero-install", radius=36),
            class_name="hero-stack",
        ),
        class_name="hero",
        id="top",
    )


def usage() -> rx.Component:
    snippet = '''import reflex as rx
from reflex_plasma_ui import plasma, plasma_provider

class Layout(rx.State):
    offsets: dict[str, dict[str, float]] = {"inbox": {"x": 0, "y": 0}}

    def save(self, panel_id: str, offset: dict[str, float]):
        self.offsets[panel_id] = offset

def index():
    return plasma_provider(
        plasma(rx.el.span("My app"), as_="header", lean=False),
        plasma(
            rx.el.h3("Inbox"),
            draggable=True, padding=20,
            offset=Layout.offsets["inbox"],
            on_drag_end=lambda o: Layout.save("inbox", o),
        ),
        mood="tidal",
    )'''
    return rx.el.section(
        rx.el.h2("Usage"),
        plasma(rx.el.div(rx.el.pre(rx.el.code(snippet)), class_name="plate"), class_name="code", radius=26, lean=False, padding=14),
        rx.el.p(
            "Plasma is for containers: panels, docks, cards, dialogs. Place surfaces flush (one piece) "
            "or further apart than the blend distance; smaller gaps draw as liquid bridging. Content "
            "stays plain, accessible HTML - the canvas only draws.",
            class_name="section-lede",
        ),
        id="usage",
    )


def stage() -> rx.Component:
    panel = lambda p, i: plasma(  # noqa: E731
        rx.el.div(
            rx.el.h3(p["title"]),
            rx.el.p(p["body"]),
            rx.el.span(p["status"], class_name="status"),
            class_name="plate",
            style={"background": p["plate"]},
        ),
        class_name="panel",
        draggable=True,
        bounds_selector="#stage",
        offset=p["offset"],
        tint=p["tint"],
        opacity=p["opacity"],
        padding=20,
        width=f"{PANEL_W}px",
        height=f"{PANEL_H}px",
        aria_label=p["label"],
        on_drag_end=lambda o: S.drag_end(i, o),
        on_join_change=lambda j: S.set_joined(i, j),
        key=p["title"],
    )
    return rx.el.div(
        rx.el.div(
            rx.foreach(S.panels, panel),
            id="stage",
            class_name="stage",
            custom_attrs=pulse_on_press(),
            on_mount=rx.call_script(STAGE_WIDTH, callback=S.compose),
        ),
        rx.el.div(
            rx.el.span(S.count, " panels, ", S.joined_count, " joined"),
            rx.el.span(S.grid, "px grid"),
            class_name="stage-bar",
        ),
        class_name="stage-wrap",
    )


def controls() -> rx.Component:
    return plasma(
        rx.el.div(
            rx.el.h3("Layout"),
            rx.el.div(
                rx.el.button("Arrange", class_name="btn", on_click=rx.call_script(STAGE_WIDTH, callback=S.arrange)),
                rx.el.button("Scatter", class_name="btn", on_click=rx.call_script(STAGE_SIZE, callback=S.scatter)),
                rx.el.button("Add panel", class_name="btn", on_click=S.add_panel, disabled=S.count >= len(PANEL_SEED)),
                rx.el.button("Remove panel", class_name="btn", on_click=S.remove_panel, disabled=S.count <= 1),
                class_name="row wrap",
            ),
            rx.el.h3("Motion"),
            _num("Viscosity", "viscosity", 0, 1, 0.05),
            _num("Stretch", "stretch", 0, 2.5, 0.1),
            _num("Flow", "flow", 0, 2, 0.1),
            rx.el.div(
                *[
                    rx.el.button(
                        name,
                        class_name="btn",
                        aria_pressed=rx.cond(
                            (S.viscosity == p["viscosity"]) & (S.stretch == p["stretch"]) & (S.flow == p["flow"]),
                            "true",
                            "false",
                        ),
                        on_click=S.apply_motion(name),
                    )
                    for name, p in presets.MOTIONS.items()
                ],
                class_name="row wrap presets",
                role="group",
                aria_label="Motion presets",
            ),
            rx.el.h3("Material"),
            select_field("Mood", S.mood, list(presets.MOODS), lambda v: S.set_text("mood", v)),
            select_field("Theme", S.theme, ["auto", "light", "dark"], lambda v: S.set_text("theme", v)),
            color_field("Tint", S.tint, lambda v: S.set_text("tint", v)),
            _num("Opacity", "opacity", 0, 1, 0.05),
            _num("Frost", "frost", 0, 1, 0.05),
            _num("Radius", "radius", 0, 48, 2, "px"),
            _num("Elevation", "elevation", 0, 1, 0.05),
            toggle("Color each panel", S.panel_colors, S.flip("panel_colors")),
            _num("Blend distance", "blend", 0, 90, 2, "px"),
            _num("Smoothness", "smoothness", 0.4, 2, 0.1),
            _num("Refraction", "refraction", 0, 2.5, 0.1),
            _num("Dispersion", "dispersion", 0, 3, 0.1),
            rx.el.h3("Rim"),
            select_field("Style", S.rim_style, ["iridescent", "color", "tint"], lambda v: S.set_text("rim_style", v)),
            rx.cond(S.rim_style == "color", color_field("Rim color", S.rim_hex, lambda v: S.set_text("rim_hex", v))),
            _num("Strength", "rim", 0, 2.5, 0.1),
            _num("Width", "rim_width", 0.3, 3, 0.1),
            _num("Highlight", "highlight", 0, 2, 0.1),
            _num("Edge line", "edge_line", 0, 2, 0.1),
            rx.el.h3("Sheen"),
            _num("Shimmer", "shimmer", 0, 2, 0.1),
            _num("Shimmer speed", "shimmer_speed", 0, 40, 1),
            _num("Glow", "glow", 0, 2, 0.1),
            _num("Wash", "wash", 0, 1.5, 0.1),
            _num("Grain", "grain", 0, 2, 0.1),
            _num("Background blur", "background_blur", 0, 40, 1, "px"),
            rx.el.h3("Snapping"),
            _num("Grid", "grid", 8, 48, 4, "px"),
            _num("Magnet", "magnet", 0, 80, 4, "px"),
            rx.el.h3("Pointer"),
            toggle("Pointer drop", S.pointer_drop, S.flip("pointer_drop")),
            toggle("Pointer pull", S.pointer_pull, S.flip("pointer_pull")),
            toggle("Ambient drops", S.ambient_drops, S.flip("ambient_drops")),
            rx.el.button("Reset everything", class_name="btn", on_click=S.reset_all, margin_top="1rem"),
            class_name="plate",
        ),
        class_name="controls",
        radius=30,
        lean=False,
        padding=14,
        aria_label="Playground controls",
    )


def playground() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Playground"),
        rx.el.p(
            "Drag panels; they fuse on contact and snap to the grid on release. Throw one to stretch "
            "the plasma. Click empty space to send a pulse. Every control is Reflex state bound to "
            "plasma_provider - and it changes the whole page.",
            class_name="section-lede",
        ),
        rx.el.div(stage(), controls(), class_name="play"),
        plasma(rx.el.div(rx.el.pre(rx.el.code(S.code)), class_name="plate"), class_name="code", radius=26, lean=False, padding=14),
        id="playground",
    )


API_ROWS = [
    ("plasma_provider(*children, **props)", "Owns the renderer. Every React prop in snake_case (mood, theme, tint, frost, material, viscosity, ...), plus name, background_selector and on_ready."),
    ("plasma(*children, **props)", "A surface: as_, radius, lean, tint, opacity, frost, elevation, padding, fuse, draggable, snap, group, bounds_selector, offset, default_offset, form_in, form_out."),
    ("on_drag_end / on_join_change", "Backend events: the settled {x, y} offset, and a bool when a surface fuses or separates. Also on_drag_start, on_forming, on_formed."),
    ("plasma_canvas(class_name, z_index, canvas_style)", "Place the canvas yourself with plasma_provider(canvas=False) - needed for a clear-ground overlay."),
    ("pulse(x, y, strength, provider)", "Client-side event: a pulse through the plasma; with no coordinates it lands where the pointer last went down."),
    ("bump(energy, provider)", "Client-side event: add energy, the plasma ripples then settles."),
    ("pulse_on_press() / NO_DRAG", "custom_attrs helpers: pulse when an element itself is pressed; keep content clickable inside a draggable surface."),
    ("presets", "LOOKS (lumen, studio, slate, aqua, neon, entropy), MOTIONS, MATERIAL_PRESETS, MOODS, CLEAR_AS_WATER, OVERLAY."),
]


def api() -> rx.Component:
    return rx.el.section(
        rx.el.h2("API"),
        plasma(
            rx.el.div(
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(rx.el.tr(rx.el.th("Call"), rx.el.th("What it does"))),
                        rx.el.tbody(*[rx.el.tr(rx.el.td(rx.el.code(a)), rx.el.td(b)) for a, b in API_ROWS]),
                    ),
                    class_name="table-wrap",
                ),
                class_name="plate",
            ),
            class_name="api",
            radius=26,
            lean=False,
            padding=14,
        ),
        id="api",
    )


def looks_seg() -> rx.Component:
    return rx.el.div(
        *[
            rx.el.button(
                name,
                title=presets.LOOK_BLURBS[name],
                aria_pressed=rx.cond(S.look == name, "true", "false"),
                on_click=S.apply_look(name),
            )
            for name in presets.LOOKS
        ],
        class_name="seg small",
        role="group",
        aria_label="Configuration",
    )


def page() -> rx.Component:
    return plasma_provider(
        nav("/", looks_seg()),
        rx.el.main(
            hero(),
            usage(),
            playground(),
            api(),
            rx.el.footer(
                "reflex-plasma-ui · wraps @cruxgarden/plasma-ui 0.7.0 (MIT) · a Crux Garden project",
                class_name="footer",
            ),
            class_name="site",
            style={"--plate-bg": S.plate_bg},
        ),
        mood=S.mood,
        theme=S.theme,
        freeze_on_scroll=True,
        blend=S.blend,
        refraction=S.refraction,
        dispersion=S.dispersion,
        rim=S.rim,
        smoothness=S.smoothness,
        radius=S.radius,
        tint=S.tint,
        opacity=S.opacity,
        frost=S.frost,
        elevation=S.elevation,
        viscosity=S.viscosity,
        stretch=S.stretch,
        flow=S.flow,
        rim_color=S.rim_color,
        rim_width=S.rim_width,
        highlight=S.highlight,
        edge_line=S.edge_line,
        shimmer=S.shimmer,
        shimmer_speed=S.shimmer_speed,
        glow=S.glow,
        wash=S.wash,
        grain=S.grain,
        background_blur=S.background_blur,
        pointer_drop=S.pointer_drop,
        pointer_pull=S.pointer_pull,
        ambient_drops=S.ambient_drops,
        grid=S.grid,
        magnet=S.magnet,
        form_out=True,
        on_ready=S.on_ready,
    )
