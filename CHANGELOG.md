# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-09-23

First release to reach PyPI. Functionally identical to 0.1.0, which was tagged
but never published.

### Fixed

- Drop the `Framework :: Reflex` classifier. It is not in the trove list, so
  PyPI rejected the whole upload with `400 'Framework :: Reflex' is not a valid
  classifier`. `twine check --strict` does not catch this — it validates that
  the metadata renders, not that the classifiers exist — so the mistake only
  surfaced at the upload. Discoverability is unaffected: the `reflex` and
  `reflex-custom-components` keywords are what the Reflex gallery reads.

### Added

- A test that validates every declared classifier against `trove-classifiers`,
  and one that checks the CI matrix's Python versions are all claimed. Both run
  in the release build job, so a bad classifier can no longer spend a version
  number.

## [0.1.0] - 2026-09-22 [UNRELEASED]

Tagged, never published — see 0.1.1.

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

[Unreleased]: https://github.com/ecrespo/reflex-plasma-ui/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/ecrespo/reflex-plasma-ui/releases/tag/v0.1.1
[0.1.0]: https://github.com/ecrespo/reflex-plasma-ui/releases/tag/v0.1.0
