"""Presets are keyword bundles for the components - so they must use real prop names."""

from __future__ import annotations

import typing

import pytest

from reflex_plasma_ui import Plasma, PlasmaProvider, plasma_provider, presets
from reflex_plasma_ui.plasma_ui import MaterialName, MoodName

PROVIDER_PROPS = set(PlasmaProvider.get_props()) - set(PlasmaProvider.get_event_triggers())
SURFACE_PROPS = set(Plasma.get_props()) - set(Plasma.get_event_triggers())

PRESET_BUNDLES: dict[str, dict] = {
    **{f"LOOKS[{k!r}]": v for k, v in presets.LOOKS.items()},
    **{f"MOTIONS[{k!r}]": v for k, v in presets.MOTIONS.items()},
    **{f"MATERIAL_PRESETS[{k!r}]": v for k, v in presets.MATERIAL_PRESETS.items()},
    "CLEAR_AS_WATER": presets.CLEAR_AS_WATER,
    "OVERLAY": presets.OVERLAY,
    "DEFAULTS": presets.DEFAULTS,
}


@pytest.mark.parametrize("name", sorted(PRESET_BUNDLES))
def test_every_preset_key_is_a_provider_prop(name: str) -> None:
    unknown = set(PRESET_BUNDLES[name]) - PROVIDER_PROPS
    assert not unknown, f"{name} sets props the provider does not have: {sorted(unknown)}"


@pytest.mark.parametrize("name", sorted(PRESET_BUNDLES))
def test_every_preset_is_accepted_by_the_provider(name: str) -> None:
    """The strongest check: the bundle actually builds a component."""
    assert plasma_provider(**PRESET_BUNDLES[name]) is not None


def test_material_list_matches_the_material_literal() -> None:
    assert set(presets.MATERIALS) == set(typing.get_args(MaterialName))


def test_material_presets_cover_every_material() -> None:
    assert set(presets.MATERIAL_PRESETS) == set(presets.MATERIALS)


@pytest.mark.parametrize("material", presets.MATERIALS)
def test_each_material_preset_selects_its_own_material(material: str) -> None:
    assert presets.MATERIAL_PRESETS[material]["material"] == material


def test_material_notes_cover_every_material() -> None:
    assert set(presets.MATERIAL_NOTES) == set(presets.MATERIALS)


def test_moods_match_the_mood_literal() -> None:
    assert set(presets.MOODS) == set(typing.get_args(MoodName))


@pytest.mark.parametrize("mood", sorted(presets.MOODS))
def test_each_mood_has_three_colors_a_blend_and_a_spring(mood: str) -> None:
    spec = presets.MOODS[mood]
    assert len(spec["colors"]) == 3
    assert all(c.startswith("#") for c in spec["colors"])
    assert spec["blend"] > 0
    assert set(spec["spring"]) == {"stiffness", "damping"}


def test_look_blurbs_cover_every_look() -> None:
    assert set(presets.LOOK_BLURBS) == set(presets.LOOKS)


@pytest.mark.parametrize("look", sorted(presets.LOOKS))
def test_each_look_names_a_known_mood(look: str) -> None:
    assert presets.LOOKS[look]["mood"] in presets.MOODS


def test_overlay_is_the_clear_ground_recipe() -> None:
    """A dialog above a scrim needs a transparent canvas it places itself."""
    assert presets.OVERLAY["ground"] == "clear"
    assert presets.OVERLAY["canvas"] is False


def test_defaults_are_documented_for_most_provider_props() -> None:
    """Reflex-only extras (name, background_selector, ...) have no library default."""
    no_library_default = {"name", "background_selector", "background", "blend"}
    missing = PROVIDER_PROPS - set(presets.DEFAULTS) - no_library_default
    assert not missing, f"props with no documented default: {sorted(missing)}"


def test_presets_are_not_shared_mutable_state() -> None:
    """Each bundle is splatted into a call, so a caller must not be able to poison it."""
    before = dict(presets.LOOKS["lumen"])
    plasma_provider(**presets.LOOKS["lumen"], theme="dark")
    assert presets.LOOKS["lumen"] == before


def test_surface_props_that_presets_never_touch_stay_on_the_surface() -> None:
    """Sanity: provider and surface prop sets are genuinely different objects."""
    assert "draggable" in SURFACE_PROPS
    assert "draggable" not in PROVIDER_PROPS
