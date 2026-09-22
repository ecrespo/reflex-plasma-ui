# Contributing

Thanks for taking the time. This is a small package; the loop is short.

## Set up

```bash
uv venv
uv pip install -e ".[dev]"
```

## The checks CI runs

Run these before you push — they are exactly what the
[`quality`](.github/workflows/quality.yml) and
[`security`](.github/workflows/security.yml) workflows run:

```bash
ruff check custom_components tests plasma_ui_demo/plasma_ui_demo
mypy
pytest
bandit -c pyproject.toml -r custom_components plasma_ui_demo/plasma_ui_demo
pip-audit --skip-editable
```

Formatting is **not** enforced. `ruff format` would rewrite the hand-aligned
preset tables in `presets.py` and the compact layout code in the demo into
something considerably harder to read, so the gate is `ruff check` only. Match
the style of the file you are editing.

## Working on the component

The library lives in `custom_components/reflex_plasma_ui/`. The demo app under
`plasma_ui_demo/` is the testbed:

```bash
cd plasma_ui_demo && uv run reflex run
```

Because the package is installed editable, source edits show up in the demo
without reinstalling.

After changing a component's props, regenerate the type stubs:

```bash
PYTHONPATH=. uv run reflex component build
```

`PYTHONPATH=.` is what lets the stub generator import
`custom_components.reflex_plasma_ui`.

## Tests

`tests/` covers the package's public surface, the rendered props and custom
code, the JS the runtime helpers emit, the preset bundles (every key is checked
against the real component props, so a typo fails the suite) and the README's
examples. Add to the file that matches what you changed.

## Branches and pull requests

- Branch off `develop`. Pull requests target `develop`.
- `main` holds released code; `develop` merges into it when a release is cut.
- Keep the changelog's `[Unreleased]` section up to date with anything a user
  would notice.

Releasing is documented in [RELEASING.md](RELEASING.md).
