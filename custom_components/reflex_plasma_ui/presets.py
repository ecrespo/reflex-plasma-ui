"""Presets ported from the Plasma UI playground and examples.

Every preset is a plain dict of ``plasma_provider`` keyword arguments, so they
compose: ``plasma_provider(**LOOKS["aqua"], **MOTIONS["honey"], mood="ember")``.
"""

from __future__ import annotations

from typing import Any

#: Preset moods, as in the library (colors: deep base, mid tone, accent).
MOODS: dict[str, dict[str, Any]] = {
    "tidal": {"colors": ["#04111c", "#0f4c5c", "#6a5acd"], "blend": 40, "spring": {"stiffness": 170, "damping": 16}},
    "aurora": {"colors": ["#050b12", "#0f5e46", "#b04bd6"], "blend": 40, "spring": {"stiffness": 120, "damping": 11}},
    "ember": {"colors": ["#12060a", "#6b1a2a", "#e39a3b"], "blend": 40, "spring": {"stiffness": 260, "damping": 20}},
}

MATERIALS: list[str] = ["plasma", "crystal", "metal", "mercury", "wood", "stone", "cloud"]

#: The library's provider defaults (what an unset prop means).
DEFAULTS: dict[str, Any] = {
    "mood": "tidal", "theme": "auto", "radius": 26, "tint": "#ffffff", "opacity": 0, "frost": 0,
    "elevation": 0.35, "smoothness": 1, "refraction": 1, "dispersion": 1, "rim": 1,
    "rim_color": "iridescent", "rim_width": 1, "highlight": 1, "edge_line": 1, "shimmer": 1,
    "shimmer_speed": 1, "glow": 1, "wash": 1, "grain": 1, "background_blur": 0, "ground": "field",
    "preserve_drawing_buffer": False, "material": "plasma", "light_dir": [-0.42, -0.62, 0.66],
    "roughness": 0.28, "anisotropy": 0, "edge": 0, "edge_scale": 0.01, "edge_sharpness": 0,
    "thickness": 18, "tension": 0, "viscosity": 0.5, "stretch": 1, "flow": 0, "form_in": True,
    "form_speed": 1, "form_out": False, "pointer_drop": True, "pointer_pull": True,
    "ambient_drops": False, "grid": 24, "magnet": 40, "quality": 1.25, "freeze_on_scroll": False,
    "max_surfaces": 16, "z_index": -1, "canvas": True,
}

#: The six complete looks from the playground nav (Lumen is the default look).
LOOKS: dict[str, dict[str, Any]] = {
    "lumen": dict(
        mood="tidal", tint="#ffffff", opacity=0, frost=0, rim_color="iridescent", rim=1, rim_width=1,
        highlight=1, shimmer=1, glow=1, wash=1, grain=1, background_blur=0, edge_line=1,
        viscosity=0.5, stretch=1, flow=0, blend=40, refraction=1, dispersion=1, smoothness=1,
        elevation=0.35, ambient_drops=False,
    ),
    "studio": dict(
        mood="tidal", tint="#000000", opacity=0.55, frost=0.85, rim_color="iridescent", rim=0.25,
        rim_width=0.7, highlight=0.4, shimmer=0.6, glow=0.5, wash=1, grain=1, background_blur=0,
        edge_line=0.8, viscosity=0.7, stretch=0.4, flow=0, blend=32, refraction=0.6, dispersion=0.4,
        smoothness=1, elevation=0.2, ambient_drops=False,
    ),
    "slate": dict(
        mood="tidal", tint="#1c2733", opacity=1, frost=0, rim_color="#3d4c5c", rim=0.5, rim_width=0.6,
        highlight=0, shimmer=0, glow=0, wash=0, grain=0.4, background_blur=0, edge_line=0.6,
        viscosity=0.6, stretch=0, flow=0, blend=40, refraction=0, dispersion=0, smoothness=1,
        elevation=0.12, ambient_drops=False,
    ),
    "aqua": dict(
        mood="tidal", tint="#ffffff", opacity=0, frost=0, rim_color="iridescent", rim=0, shimmer=0,
        glow=0, wash=0, grain=0, highlight=0, edge_line=0.35, rim_width=1, background_blur=0,
        viscosity=0.35, stretch=1, flow=0.4, blend=40, refraction=1.5, dispersion=1.6, smoothness=1,
        elevation=0, ambient_drops=False,
    ),
    "neon": dict(
        mood="ember", tint="#160b1e", opacity=0.75, frost=0.2, rim_color="#ff2d95", rim=1.6,
        rim_width=1.3, highlight=0.6, shimmer=1.4, glow=1.4, wash=1, grain=1, background_blur=0,
        edge_line=1.4, viscosity=0.15, stretch=1.2, flow=0, blend=40, refraction=1, dispersion=2,
        smoothness=1, elevation=0.55, ambient_drops=False,
    ),
    "entropy": dict(
        mood="aurora", tint="#ffffff", opacity=0, frost=0.25, rim_color="iridescent", rim=1.3,
        rim_width=1.4, highlight=1, shimmer=1.6, glow=1.4, wash=1, grain=1, background_blur=0,
        edge_line=1, viscosity=0, stretch=2.5, flow=2, blend=56, refraction=1.4, dispersion=2.2,
        smoothness=1, elevation=0.5, ambient_drops=True,
    ),
}

LOOK_BLURBS: dict[str, str] = {
    "lumen": "Clear plasma, iridescent rim. The default look.",
    "studio": "Frosted workspace. Calm motion, quiet edges.",
    "slate": "Opaque panels, no shine. Reads as a plain app.",
    "aqua": "Clear as water. Every sheen off, only the lens remains.",
    "neon": "Dark tinted panels, colored rims, fast and springy.",
    "entropy": "Every motion field at maximum. Wobbly, dreamy, never still.",
}

#: Motion presets (viscosity / stretch / flow).
MOTIONS: dict[str, dict[str, float]] = {
    "water": {"viscosity": 0.1, "stretch": 1.3, "flow": 0.6},
    "gel": {"viscosity": 0.5, "stretch": 1, "flow": 0},
    "honey": {"viscosity": 0.85, "stretch": 1.8, "flow": 0.3},
    "solid": {"viscosity": 0.6, "stretch": 0, "flow": 0},
}

#: Each material with the physics and outline it wants (from examples/materials).
MATERIAL_PRESETS: dict[str, dict[str, Any]] = {
    "plasma": dict(material="plasma", thickness=18, tension=0, blend=24, viscosity=0.5, stretch=1,
                   radius=26, edge=0, edge_scale=0.01, edge_sharpness=0),
    "crystal": dict(material="crystal", thickness=26, tension=0, blend=14, viscosity=0.9, stretch=0.15,
                    radius=10, edge=3, edge_scale=0.05, edge_sharpness=1),
    "metal": dict(material="metal", thickness=10, tension=0, blend=8, viscosity=0.85, stretch=0.2,
                  radius=3, edge=0, edge_scale=0.01, edge_sharpness=0),
    "mercury": dict(material="mercury", thickness=30, tension=0.9, blend=54, viscosity=0.2, stretch=1.6,
                    radius=26, edge=2, edge_scale=0.004, edge_sharpness=0),
    "wood": dict(material="wood", thickness=16, tension=0, blend=6, viscosity=1, stretch=0,
                 radius=5, edge=1.5, edge_scale=0.02, edge_sharpness=0.3),
    "stone": dict(material="stone", thickness=22, tension=0, blend=4, viscosity=1, stretch=0,
                  radius=8, edge=7, edge_scale=0.03, edge_sharpness=0.85),
    "cloud": dict(material="cloud", thickness=40, tension=0.35, blend=60, viscosity=0.15, stretch=2.2,
                  radius=40, edge=26, edge_scale=0.005, edge_sharpness=0),
}

MATERIAL_NOTES: dict[str, str] = {
    "plasma": "The original. A lens with a coloured rim.",
    "crystal": "Glass with its bevel cut into facets.",
    "metal": "A conductor: no diffuse, all reflection.",
    "mercury": "The same conductor, with the surface tension left in.",
    "wood": "Rings, pores and a streaked highlight.",
    "stone": "Rough, matte, flecked, veined.",
    "cloud": "The one volume rather than a surface.",
}

#: The "clear as water" recipe from the README.
CLEAR_AS_WATER: dict[str, Any] = dict(
    rim=0, highlight=0, shimmer=0, glow=0, wash=0, grain=0, edge_line=0.35, refraction=1.5, dispersion=1.6
)

#: Settings for a second, clear-ground provider stacked above a scrim.
OVERLAY: dict[str, Any] = dict(
    ground="clear", canvas=False, pointer_drop=False, grain=0, glow=0, max_surfaces=2
)
