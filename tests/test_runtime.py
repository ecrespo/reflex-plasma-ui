"""Client-side helpers: the JS they emit and the attributes they hand back."""

from __future__ import annotations

import reflex as rx

from reflex_plasma_ui import runtime


def _script(spec) -> str:
    """Pull the literal JS out of a ``rx.call_script`` event spec."""
    for var, value in spec.args:
        if str(var) == "javascript_code":
            return value._var_value
    raise AssertionError("no javascript_code argument in the event spec")


def test_pulse_defaults_to_undefined_coordinates() -> None:
    assert _script(runtime.pulse()) == "window.__reflexPlasma?.pulse(undefined, undefined, 1.0, undefined)"


def test_pulse_passes_explicit_arguments_through() -> None:
    js = _script(runtime.pulse(120, 80, strength=2, provider="overlay"))
    assert js == 'window.__reflexPlasma?.pulse(120, 80, 2, "overlay")'


def test_pulse_quotes_the_provider_name() -> None:
    """A bare name would be a JS identifier lookup, not a string."""
    assert '"main"' in _script(runtime.pulse(provider="main"))


def test_provider_name_with_a_quote_is_escaped() -> None:
    js = _script(runtime.pulse(provider='ev"il'))
    assert js.endswith(r'"ev\"il")')


def test_bump_emits_energy_and_provider() -> None:
    assert _script(runtime.bump(0.8, provider="overlay")) == 'window.__reflexPlasma?.bump(0.8, "overlay")'


def test_bump_default_energy() -> None:
    assert _script(runtime.bump()) == "window.__reflexPlasma?.bump(0.6, undefined)"


def test_helpers_are_optional_chained_so_a_missing_registry_is_a_no_op() -> None:
    assert _script(runtime.pulse()).startswith("window.__reflexPlasma?.")
    assert _script(runtime.bump()).startswith("window.__reflexPlasma?.")


def test_pulse_accepts_a_state_var() -> None:
    """A Var must be inlined as JS, not JSON-encoded into a string."""
    js = _script(runtime.pulse(strength=rx.Var("myStrength")))
    assert "myStrength" in js and '"myStrength"' not in js


def test_pulse_on_press_defaults_to_the_default_provider() -> None:
    attrs = runtime.pulse_on_press()
    # An empty name means "whatever provider is registered as default".
    assert attrs == {"data-plasma-pulse": "", "data-plasma-pulse-strength": "1.0"}


def test_pulse_on_press_carries_provider_and_strength() -> None:
    attrs = runtime.pulse_on_press(strength=2.5, provider="overlay")
    assert attrs["data-plasma-pulse"] == "overlay"
    assert attrs["data-plasma-pulse-strength"] == "2.5"


def test_no_drag_uses_the_documented_attribute() -> None:
    assert runtime.NO_DRAG == {runtime.NODRAG_ATTR: "true"}
    assert runtime.NODRAG_ATTR == "data-plasma-nodrag"


def test_forming_constants_match_the_css_selector() -> None:
    assert runtime.FORMING_ATTR in runtime.FORMING_CSS
    assert runtime.FORMING_EVENT == "plasmaforming"
    assert runtime.FORMED_EVENT == "plasmaformed"


def test_forming_style_is_a_style_element_holding_the_css() -> None:
    element = runtime.forming_style()
    assert isinstance(element, rx.Component)
    assert element.tag == "style"
