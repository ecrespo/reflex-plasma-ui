# reflex-plasma-ui

[![quality](https://github.com/ecrespo/reflex-plasma-ui/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/ecrespo/reflex-plasma-ui/actions/workflows/quality.yml)
[![security](https://github.com/ecrespo/reflex-plasma-ui/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ecrespo/reflex-plasma-ui/actions/workflows/security.yml)
[![PyPI](https://img.shields.io/pypi/v/reflex-plasma-ui.svg)](https://pypi.org/project/reflex-plasma-ui/)
[![Python](https://img.shields.io/pypi/pyversions/reflex-plasma-ui.svg)](https://pypi.org/project/reflex-plasma-ui/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Plasma UI](https://github.com/CruxGarden/plasma-ui) for [Reflex](https://reflex.dev): liquid panels rendered in WebGL on canvas. Every panel on the page is **one shared plasma** — surfaces fuse on contact, refract whatever is behind them, stretch when thrown and snap to a grid. The DOM stays ordinary, accessible HTML; the canvas only draws.

Wraps `@cruxgarden/plasma-ui@0.7.0` (pinned, installed automatically by Reflex). Works on Chrome, Edge, Firefox and Safari 16.4+ (WebGL2). Without WebGL2, every surface falls back to a frosted CSS panel with drag and snap intact. The effect is GPU-heavy, so it belongs on desktop browsers.

```bash
pip install reflex-plasma-ui
```

## Quick start

```python
import reflex as rx
from reflex_plasma_ui import plasma, plasma_provider, pulse


class Layout(rx.State):
    offset: dict[str, float] = {"x": 24, "y": 24}

    def save(self, offset: dict[str, float]):
        self.offset = offset


def index():
    return plasma_provider(
        plasma(rx.el.strong("My app"), as_="header", lean=False, fuse=False, padding=16),
        rx.el.div(
            plasma(
                rx.el.h3("Inbox"),
                rx.el.button("Pulse", on_click=pulse()),
                draggable=True,
                padding=20,
                bounds_selector="#stage",
                offset=Layout.offset,
                on_drag_end=Layout.save,
                width="240px",
            ),
            id="stage",
            style={"position": "relative", "height": "70vh"},
        ),
        mood="tidal",
        theme="dark",
    )


app = rx.App()
app.add_page(index)
```

> The canvas sits at `z-index: -1`, behind the page. If your app uses the Radix theme with its page background (`RadixThemesPlugin`, `rx.theme`), that opaque background hides the canvas: set `has_background=False` or make `.radix-themes` transparent.

## Components

### `plasma_provider(*children, **props)`

Owns the renderer and every shared setting. All `<PlasmaProvider>` props are available in snake_case. Any prop left unset keeps the library default, and every prop can be bound to state, so changes go live.

| Group | Props |
| --- | --- |
| Look | `mood` (`"tidal"`/`"aurora"`/`"ember"` or a custom `{colors, blend, spring}` dict), `theme` (`auto`/`light`/`dark`), `background` (CSS color or image URL), `radius`, `blend`, `tint`, `opacity`, `frost`, `elevation`, `smoothness`, `refraction`, `dispersion` |
| Rim & sheen | `rim`, `rim_color` (`"iridescent"`, `"tint"` or hex), `rim_width`, `highlight`, `edge_line`, `shimmer`, `shimmer_speed`, `glow`, `wash`, `grain`, `background_blur` |
| Material | `material` (`plasma`, `crystal`, `metal`, `mercury`, `wood`, `stone`, `cloud`), `light_dir`, `roughness`, `anisotropy`, `edge`, `edge_scale`, `edge_sharpness`, `thickness`, `tension` |
| Motion | `viscosity`, `stretch`, `flow`, `form_in`, `form_speed`, `form_out` |
| Pointer & layout | `pointer_drop`, `pointer_pull`, `ambient_drops`, `grid`, `magnet` |
| Rendering | `ground` (`"field"`/`"clear"`), `preserve_drawing_buffer`, `quality`, `freeze_on_scroll`, `max_surfaces`, `z_index`, `canvas` |
| Reflex extras | `name` (registry name for `pulse`/`bump`, default `"default"`), `background_selector` (use an `img`/`canvas`/`video` element as the background), `on_ready` → `{"supported": bool, "reduced_motion": bool}` |

To follow Reflex's color mode, use `theme=rx.color_mode_cond("light", "dark")`.

### `plasma(*children, **props)`

A plasma surface. Anything else you pass (`class_name`, `id`, `aria_*`, `on_click`, CSS style props, …) goes to the rendered element.

| Prop | Description |
| --- | --- |
| `as_` | Element to render: `"div"` (default), `"header"`, `"nav"`, `"section"`, `"a"`… |
| `radius`, `lean` | Corner radius (px); lean toward the pointer while standalone (px, `False` disables) |
| `tint`, `opacity`, `frost`, `elevation` | Per-surface look; joined surfaces blend these into each other |
| `padding` | Inner padding (px), halved on joined edges so gutters equal the free-edge inset |
| `fuse` | `False` for bars, docks and fixed chrome that must never blend |
| `draggable`, `snap`, `group` | Drag (arrow keys step one grid cell), snap on release, snap groups |
| `bounds_selector` | CSS selector of the drag area and grid origin (default: the viewport) |
| `offset`, `default_offset` | Controlled / initial `{"x", "y"}`; changes spring into place |
| `form_in`, `form_out` | Per-surface override of the provider's form-in/out |
| `on_drag_start`, `on_drag_end(offset)`, `on_join_change(joined)`, `on_forming`, `on_formed` | Backend events |

On `plasma`, `opacity` and `padding` are the plasma props (tint strength, join-aware padding in px), not the CSS properties. Don't set `transform`, `translate` or `scale` on a surface; the library animates those.

### `plasma_canvas(class_name=..., z_index=..., canvas_style=...)`

With `plasma_provider(canvas=False)`, place the canvas yourself. `canvas_style` is the real inline style (camelCase keys).

## Runtime helpers

```python
from reflex_plasma_ui import pulse, bump, pulse_on_press, NO_DRAG

rx.el.button("Pulse", on_click=pulse())                 # at the last pointer-down
rx.el.button("Here", on_click=pulse(120, 80, strength=2))
rx.el.button("Bump", on_click=bump(0.8))

class S(rx.State):
    def play(self):
        return bump(0.6)                                # from a backend handler

rx.el.div("empty stage", custom_attrs=pulse_on_press()) # pulses on its own empty space
rx.el.ul(..., custom_attrs=NO_DRAG)                     # stays clickable in a draggable surface
```

`pulse` and `bump` run entirely in the browser. They take `provider="name"` when there is more than one provider. `forming_style()` / `FORMING_CSS` fade a surface's contents in after its material has formed.

## Presets

```python
from reflex_plasma_ui import presets

plasma_provider(..., **presets.LOOKS["aqua"])            # lumen, studio, slate, aqua, neon, entropy
plasma_provider(..., **presets.MOTIONS["honey"])         # water, gel, honey, solid
plasma_provider(..., **presets.MATERIAL_PRESETS["mercury"])  # material + its physics and outline
plasma_provider(..., **presets.CLEAR_AS_WATER)
```

## A dialog above a scrim

The material is one canvas behind everything, so a dialog above a scrim needs a second provider. It uses a clear ground and refracts the first canvas:

```python
plasma_provider(
    plasma_canvas(class_name="ground"),
    ...page...,
    rx.cond(State.open, rx.el.div(
        rx.el.div(class_name="scrim"),
        plasma_provider(
            plasma_canvas(canvas_style={"position": "absolute", "zIndex": 1}),
            plasma(..., elevation=0.7, on_formed=State.reveal),
            name="overlay",
            background_selector="canvas.ground",
            **presets.OVERLAY,  # ground="clear", canvas=False, small budget
        ),
        class_name="dialog-root",  # position: fixed; inset: 0
    )),
    preserve_drawing_buffer=True,
    canvas=False,
)
```

## How it works

The package has no `library` import of its own. Three small wrapper components (`ReflexPlasmaProvider`, `ReflexPlasma`, `ReflexPlasmaCanvas`) are compiled into the page as custom code, and Reflex installs the pinned npm package from their imports. The wrappers:

- turn serialisable props into what React expects: selectors become ref objects and live elements;
- publish each provider's `usePlasmaRuntime()` on `window.__reflexPlasma[name]`, which is how `pulse`/`bump` reach it;
- track the last pointer-down, so `pulse()` lands where the user clicked.

## Demo app

```bash
cd plasma_ui_demo
uv run reflex run
```

| Page | What it shows |
| --- | --- |
| `/` Playground | The upstream docs playground: six looks, motion presets, every provider prop bound to state, draggable panels with join tracking, arrange/scatter/add/remove, the generated Python snippet |
| `/workspace` | The upstream real-world example: bar, dock and four panels, focus elevation, layout persisted with `rx.LocalStorage`, `bump` from a backend event |
| `/materials` | All seven materials with their physics, grounds, light direction, roughness, anisotropy and outline controls |
| `/layers` | Backgrounds (field / color / image), form-in/out lifecycle events, pulses, and the two-provider dialog above a scrim |

## Development

```bash
uv venv && uv pip install -e ".[dev]"
cd plasma_ui_demo && uv run reflex run
PYTHONPATH=. uv run reflex component build   # .pyi stubs + sdist/wheel in dist/
```

The checks CI runs, which you can run locally in the same order:

```bash
ruff check custom_components tests plasma_ui_demo/plasma_ui_demo
mypy
pytest
bandit -c pyproject.toml -r custom_components plasma_ui_demo/plasma_ui_demo
pip-audit --skip-editable
```

[CONTRIBUTING.md](CONTRIBUTING.md) has the details, [RELEASING.md](RELEASING.md)
describes cutting a release, [SECURITY.md](SECURITY.md) the reporting process
and what this package's attack surface actually is, and
[CHANGELOG.md](CHANGELOG.md) what changed.

## Notes

- In `reflex run` (dev mode) React StrictMode mounts effects twice, so a surface added after the first render can fire `on_forming`/`on_formed` twice. Production builds fire them once.
- `PYTHONPATH=.` lets the stub generator import `custom_components.reflex_plasma_ui`.

## License

MIT. Plasma UI is © Crux Garden, MIT.
