import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="plasma_ui_demo",
    # Plain HTML + the demo stylesheet: no Radix theme, whose opaque page
    # background would hide the plasma canvas (it sits at z-index -1).
    plugins=[],
    disable_plugins=[SitemapPlugin],
    telemetry_enabled=False,
)
