# Security policy

## Supported versions

Only the latest released version of `reflex-plasma-ui` receives fixes.

| Version | Supported |
| --- | --- |
| 0.1.x | ✅ |

## Reporting a vulnerability

Report privately through GitHub's
[security advisories](https://github.com/ecrespo/reflex-plasma-ui/security/advisories/new)
for this repository, or by email to ecrespo@gmail.com. Please do **not** open a
public issue for a vulnerability.

Include what you have: the affected version, how to reproduce it, and the impact
you think it has. You can expect an acknowledgement within a week and a fix or a
plan within 30 days for anything confirmed.

## What this package is, in security terms

`reflex-plasma-ui` is a presentation-layer component. It has no network calls,
no file or subprocess access, no deserialisation of untrusted input and no
authentication or authorisation logic. Its attack surface is:

- **The JavaScript glue** in `custom_components/reflex_plasma_ui/_js.py`, which
  Reflex compiles into every page that uses a plasma component. It is a static
  string: no props are interpolated into it, so a prop value cannot become code.
- **The npm dependency** `@cruxgarden/plasma-ui`, pinned to an exact version
  (`0.7.0`) so an upstream release cannot change what your build installs.
- **Selector props** (`bounds_selector`, `background_selector`) are passed to
  `document.querySelector` in the browser. Treat them as you would any selector:
  they are a lookup, not an injection point, but do not build them from
  unsanitised user input.
- **`pulse(provider=...)`** is JSON-encoded before it is spliced into the
  `rx.call_script` payload, so a quote in a provider name cannot break out.

## Automated checks

Every push and pull request runs the [`security`](.github/workflows/security.yml)
workflow — bandit (SAST), pip-audit (dependency CVEs), gitleaks (secrets, over
the whole history), CodeQL, and dependency review on pull requests. It also runs
on a weekly schedule, because a dependency can become vulnerable without anyone
pushing a commit. Dependabot keeps the GitHub Actions, pip and npm dependencies
current.

Releases are published to PyPI with
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/): no API token
exists in this repository or in its CI secrets, and every artifact carries a
[build provenance attestation](https://github.com/ecrespo/reflex-plasma-ui/attestations).
