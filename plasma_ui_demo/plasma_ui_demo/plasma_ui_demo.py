"""reflex-plasma-ui demo: Plasma UI's liquid WebGL panels, driven from Reflex.

Pages
-----
/           Playground - every provider prop as backend state, looks, motion presets
/workspace  Workspace  - the upstream real-world example, ported
/materials  Materials  - plasma, crystal, metal, mercury, wood, stone, cloud
/layers     Layers     - backgrounds, form-in/out lifecycle, pulses, dialog above a scrim
"""

import reflex as rx

from .pages import layers, materials, playground, workspace

FONTS = (
    "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600"
    "&family=JetBrains+Mono&family=Onest:wght@400;500&display=swap"
)

app = rx.App(
    stylesheets=["/plasma_demo.css"],
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="stylesheet", href=FONTS),
    ],
)
app.add_page(
    playground.page,
    route="/",
    title="Plasma UI for Reflex - Playground",
    description="Liquid WebGL panels for Reflex: they fuse on contact, refract and snap to a grid.",
    on_load=playground.PlaygroundState.init_theme,
)
app.add_page(workspace.page, route="/workspace", title="Plasma UI for Reflex - Workspace")
app.add_page(materials.page, route="/materials", title="Plasma UI for Reflex - Materials")
app.add_page(layers.page, route="/layers", title="Plasma UI for Reflex - Layers")
