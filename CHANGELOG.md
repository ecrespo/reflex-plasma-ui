# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-22

First public release.

### Added

- `plasma_provider()` — the WebGL renderer and every shared setting, with all
  53 `<PlasmaProvider>` props exposed in snake_case and bindable to state.
- `plasma()` — a plasma surface: drag, snap, fuse, per-surface look, join-aware
  padding, and the `on_drag_start` / `on_drag_end` / `on_join_change` /
  `on_forming` / `on_formed` backend events.
- `plasma_canvas()` — place the canvas yourself with `plasma_provider(canvas=False)`.
- Runtime helpers `pulse()`, `bump()`, `pulse_on_press()`, `forming_style()`,
  and the `NO_DRAG` / `FORMING_*` constants.
- `presets` — the six playground looks, four motion presets, the seven material
  recipes, `CLEAR_AS_WATER` and `OVERLAY`.
- Type stubs (`plasma_ui.pyi`) and a `py.typed` marker.
- A four-page demo app under `plasma_ui_demo/`: playground, workspace,
  materials and layers.

### Notes

- Wraps `@cruxgarden/plasma-ui@0.7.0`, pinned and installed by Reflex.
- Requires WebGL2; without it every surface falls back to a frosted CSS panel
  with drag and snap intact.

[Unreleased]: https://github.com/ecrespo/reflex-plasma-ui/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ecrespo/reflex-plasma-ui/releases/tag/v0.1.0
