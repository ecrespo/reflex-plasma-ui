# Releasing

A release is one tag. Everything else — tests, build, PyPI upload, GitHub
release, provenance attestation — is the
[`release`](.github/workflows/release.yml) workflow.

## One-time setup: the PyPI trusted publisher

`reflex-plasma-ui` publishes with [Trusted Publishing]. PyPI verifies the
workflow's OpenID Connect identity instead of an API token, so **no PyPI
credential exists in this repository, in its secrets, or on any developer's
machine.** Nothing to leak, nothing to rotate.

The package is not on PyPI yet, so register a **pending** publisher first:

> https://pypi.org/manage/account/publishing/ → *Add a new pending publisher*

Fill it in with exactly these values:

| Field | Value |
| --- | --- |
| PyPI Project Name | `reflex-plasma-ui` |
| Owner | `ecrespo` |
| Repository name | `reflex-plasma-ui` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

The *Environment name* matters: the `pypi` job in `release.yml` runs in a GitHub
environment called `pypi`, and PyPI will reject an upload from any other one.
After the first successful upload the pending publisher becomes an ordinary
trusted publisher on the project, and the same five values keep working.

Optionally create the matching environment in GitHub
(*Settings → Environments → New environment → `pypi`*) and add a required
reviewer. Then every upload waits for an explicit approval, which is a good
place to stop and look at the built artifacts before they become permanent.

To rehearse against TestPyPI first, register the same pending publisher at
<https://test.pypi.org/manage/account/publishing/> and run the workflow manually
with *Run workflow → dry run: false* after temporarily pointing the publish step
at `https://test.pypi.org/legacy/`.

[Trusted Publishing]: https://docs.pypi.org/trusted-publishers/

## Cutting a release

1. **Land everything on `develop`,** green.

2. **Bump the version** in `pyproject.toml` and move the `[Unreleased]` entries
   in `CHANGELOG.md` under the new version heading, with today's date and the
   two link definitions at the bottom updated.

3. **Open a pull request from `develop` to `main`** and merge it once the
   `quality` and `security` checks pass.

4. **Tag `main`:**

   ```bash
   git checkout main && git pull
   git tag -a v0.1.0 -m "v0.1.0"
   git push origin v0.1.0
   ```

The workflow then:

- refuses to continue unless the tag matches `version` in `pyproject.toml`;
- refuses to continue if that version is already on PyPI (PyPI never lets a
  version be re-uploaded, so this fails early and loudly instead of halfway
  through);
- runs the test suite, builds the sdist and wheel, and checks the rendered PyPI
  metadata with `twine check --strict`;
- uploads to PyPI through the trusted publisher;
- attests the artifacts' build provenance and creates the GitHub release with
  the sdist, the wheel and the changelog section for that version.

Publishing is effectively irreversible: a version can be yanked but never
deleted, and the project name is claimed permanently. The tag is the point of no
return.

## Releasing by hand

Only if CI is unavailable. It needs a PyPI API token, which the normal path
deliberately does without:

```bash
uv pip install -e ".[dev]"
PYTHONPATH=. uv run reflex component build   # stubs + dist/
twine check --strict dist/*
UV_PUBLISH_TOKEN=pypi-... uv publish
```

Never write that token into a file in the repository.

## After a release

Listing the component in the Reflex community gallery is a separate, optional
step, and only works once the package is on PyPI:

```bash
uv run reflex login
uv run reflex component share
```

It asks for the published package name (`reflex-plasma-ui`) and, optionally, a
preview image and a demo URL. It registers those in the gallery; it does not
upload any code.
