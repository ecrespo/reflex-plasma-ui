"""The control wrappers: tags, the pinned import, prop mapping and value events."""

from __future__ import annotations

import pytest
import reflex as rx

from reflex_plasma_ui import (
    PlasmaAccordion,
    PlasmaAccordionItem,
    PlasmaButton,
    PlasmaSlider,
    PlasmaSwitch,
    PlasmaTab,
    PlasmaTabList,
    PlasmaTabPanel,
    PlasmaTabs,
    _js,
    plasma_accordion,
    plasma_accordion_item,
    plasma_button,
    plasma_provider,
    plasma_slider,
    plasma_switch,
    plasma_tab,
    plasma_tab_list,
    plasma_tab_panel,
    plasma_tabs,
)

#: Rendered straight from the upstream export. The slider has a wrapper, tested below.
CONTROLS = [
    (PlasmaButton, "PlasmaButton"),
    (PlasmaSwitch, "PlasmaSwitch"),
    (PlasmaTabs, "PlasmaTabs"),
    (PlasmaTabList, "PlasmaTabList"),
    (PlasmaTab, "PlasmaTab"),
    (PlasmaTabPanel, "PlasmaTabPanel"),
    (PlasmaAccordion, "PlasmaAccordion"),
    (PlasmaAccordionItem, "PlasmaAccordionItem"),
]
#: The controls that are themselves surfaces, and so take the per-surface props.
SURFACES = [PlasmaButton, PlasmaSwitch, PlasmaSlider, PlasmaTab, PlasmaAccordionItem]


class _S(rx.State):
    on: bool = False
    level: float = 40.0
    tab: str = "a"
    open: list[str] = []

    def set_on(self, checked: bool):
        self.on = checked

    def set_level(self, value: float):
        self.level = value

    def set_tab(self, value: str):
        self.tab = value

    def set_open(self, value: list[str]):
        self.open = value


def _props(component: rx.Component) -> dict[str, str]:
    """Rendered props as ``{name: js_value}``."""
    return dict(p.split(":", 1) for p in component.render()["props"])


@pytest.mark.parametrize(("cls", "tag"), CONTROLS)
def test_each_control_renders_the_upstream_export_by_name(cls: type[rx.Component], tag: str) -> None:
    component = cls.create()
    assert component.tag == tag
    assert component.render()["name"] == tag


@pytest.mark.parametrize(("cls", "tag"), CONTROLS)
def test_each_control_imports_from_the_pinned_package(cls: type[rx.Component], tag: str) -> None:
    """The same spec as the provider's, so both resolve to one module and share its context."""
    imports = cls.create()._get_all_imports()
    assert {str(i.tag) for i in imports[_js.NPM_SPEC]} == {tag}


@pytest.mark.parametrize(("cls", "_tag"), CONTROLS)
def test_controls_need_no_glue_code(cls: type[rx.Component], _tag: str) -> None:
    assert cls.create().add_custom_code() == []


@pytest.mark.parametrize(("cls", "_tag"), CONTROLS)
def test_unset_props_are_omitted_so_library_defaults_survive(cls: type[rx.Component], _tag: str) -> None:
    assert _props(cls.create()) == {}


def test_an_unset_slider_renders_no_props_either() -> None:
    assert _props(plasma_slider()) == {}


@pytest.mark.parametrize("cls", SURFACES)
def test_surface_controls_take_the_per_surface_props(cls: type[rx.Component]) -> None:
    props = _props(cls.create(tint="#ff5fa2", opacity=0.4, radius=12, lean=False, form_in=False))
    assert props["tint"] == '"#ff5fa2"'
    assert props["opacity"] == "0.4"
    assert props["lean"] == "false"
    assert props["formIn"] == "false"
    assert {"on_join_change", "on_forming", "on_formed"} <= set(cls.get_event_triggers())


def test_slider_renders_through_its_wrapper_and_imports_the_upstream_slider() -> None:
    component = plasma_slider()
    assert component.tag == "ReflexPlasmaSlider"
    assert component.library is None
    imports = component._get_all_imports()
    assert {str(i.tag) for i in imports[_js.NPM_SPEC]} == {"PlasmaSlider"}
    assert component.add_custom_code() == [_js.SLIDER_CODE]


def test_slider_wrapper_holds_the_value_locally_and_resyncs_after_settling() -> None:
    """A state-bound slider must not be reset to the old prop between round-trips."""
    code = _js.SLIDER_CODE
    assert "const ReflexPlasmaSlider = forwardRef" in code
    assert "value: local" in code
    assert "setTimeout(() => setLocal(latest.current)" in code
    assert "__SETTLE__" not in code
    assert str(_js.SLIDER_SETTLE_MS) in code
    # Uncontrolled sliders are passed straight through.
    assert "if (!controlled) return createElement(PlasmaSlider, { ...props, onValueChange, ref })" in code


def test_button_props_and_click() -> None:
    props = _props(plasma_button("Save", solid=True, size="sm", type="submit", on_click=_S.set_on(True)))
    assert props["solid"] == "true"
    assert props["size"] == '"sm"'
    assert props["type"] == '"submit"'
    assert "onClick" in props


def test_switch_is_controlled_from_state_and_reports_the_new_state() -> None:
    props = _props(plasma_switch(label="Wi-Fi", checked=_S.on, on_checked_change=_S.set_on, checked_tint="#6cf2a8"))
    assert props["label"] == '"Wi-Fi"'
    assert props["checkedTint"] == '"#6cf2a8"'
    assert "on" in props["checked"]
    assert "_ev_0" in props["onCheckedChange"], "the checked flag must reach the handler"


def test_slider_range_and_value_event() -> None:
    props = _props(
        plasma_slider(value=_S.level, on_value_change=_S.set_level, min=0, max=10, step=0.5, aria_label="Volume")
    )
    assert (props["min"], props["max"], props["step"]) == ("0", "10", "0.5")
    assert props['"aria-label"'] == '"Volume"'
    assert "_ev_0" in props["onValueChange"]


def test_slider_default_value_renders_camel_case() -> None:
    assert _props(plasma_slider(default_value=25))["defaultValue"] == "25"


def test_tabs_tree_renders_root_list_tabs_and_panels() -> None:
    tree = plasma_tabs(
        plasma_tab_list(plasma_tab("One", value="a"), plasma_tab("Two", value="b"), aria_label="Sections"),
        plasma_tab_panel("First", value="a"),
        plasma_tab_panel("Second", value="b"),
        value=_S.tab,
        on_value_change=_S.set_tab,
        orientation="vertical",
    )
    rendered = tree.render()
    assert [c["name"] for c in rendered["children"]] == ["PlasmaTabList", "PlasmaTabPanel", "PlasmaTabPanel"]
    assert [c["name"] for c in rendered["children"][0]["children"]] == ["PlasmaTab", "PlasmaTab"]
    props = _props(tree)
    assert props["orientation"] == '"vertical"'
    assert "_ev_0" in props["onValueChange"]


def test_accordion_takes_a_list_of_open_values() -> None:
    props = _props(plasma_accordion(type="multiple", default_value=["q1", "q2"]))
    assert props["type"] == '"multiple"'
    assert props["defaultValue"] == '["q1", "q2"]'


def test_accordion_value_event_hands_the_list_to_the_handler() -> None:
    props = _props(plasma_accordion(value=_S.open, on_value_change=_S.set_open))
    assert "_ev_0" in props["onValueChange"]


def test_accordion_item_header_and_heading_level() -> None:
    props = _props(plasma_accordion_item("Answer", value="q1", title="What is it?", heading_level=2, disabled=True))
    assert props["title"] == '"What is it?"'
    assert props["headingLevel"] == "2"
    assert props["disabled"] == "true"


def test_controls_compose_inside_a_provider() -> None:
    tree = plasma_provider(
        plasma_button("Go"),
        plasma_switch(aria_label="On"),
        plasma_accordion(plasma_accordion_item("A", value="q1", title="Q")),
    )
    imports = tree._get_all_imports()
    names = {str(i.tag) for i in imports[_js.NPM_SPEC]}
    assert {"PlasmaProvider", "PlasmaButton", "PlasmaSwitch", "PlasmaAccordion", "PlasmaAccordionItem"} <= names
