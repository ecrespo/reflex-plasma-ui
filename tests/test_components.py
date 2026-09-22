"""The three wrappers: tags, prop mapping, npm pin and the custom code they emit."""

from __future__ import annotations

import reflex as rx

from reflex_plasma_ui import Plasma, PlasmaCanvas, PlasmaProvider, _js, plasma, plasma_canvas, plasma_provider


def _props(component: rx.Component) -> dict[str, str]:
    """Rendered props as ``{name: js_value}``."""
    rendered = component.render()
    return dict(p.split(":", 1) for p in rendered["props"])


def test_factories_build_their_component() -> None:
    assert isinstance(plasma_provider(), PlasmaProvider)
    assert isinstance(plasma(), Plasma)
    assert isinstance(plasma_canvas(), PlasmaCanvas)


def test_tags_point_at_the_wrappers_defined_in_custom_code() -> None:
    assert PlasmaProvider.create().tag == "ReflexPlasmaProvider"
    assert Plasma.create().tag == "ReflexPlasma"
    assert PlasmaCanvas.create().tag == "ReflexPlasmaCanvas"


def test_no_library_is_declared_so_reflex_does_not_import_the_tag() -> None:
    """The tags live in custom code; the npm package arrives through add_imports."""
    assert PlasmaProvider.create().library is None


def test_the_npm_package_is_pinned() -> None:
    assert _js.NPM_SPEC == f"{_js.NPM_PACKAGE}@{_js.NPM_VERSION}"
    assert _js.NPM_VERSION[0].isdigit(), "an unpinned spec would let a breaking release in"


def test_imports_pull_the_pinned_package_and_the_react_helpers() -> None:
    imports = plasma_provider()._get_all_imports()
    assert _js.NPM_SPEC in imports
    names = {str(i.name) for i in imports[_js.NPM_SPEC]}
    assert {"PlasmaProvider", "Plasma", "PlasmaCanvas", "usePlasmaRuntime"} <= names
    assert "createElement" in {str(i.name) for i in imports["react"]}


def test_provider_emits_registry_bridge_and_wrapper_in_order() -> None:
    assert PlasmaProvider.create().add_custom_code() == [
        _js.REGISTRY_CODE,
        _js.BRIDGE_CODE,
        _js.PROVIDER_CODE,
    ]


def test_bridge_is_defined_before_the_provider_uses_it() -> None:
    code = PlasmaProvider.create().add_custom_code()
    assert "function ReflexPlasmaBridge" in code[1]
    assert "ReflexPlasmaBridge" in code[2]


def test_surface_and_canvas_emit_only_their_own_wrapper() -> None:
    assert plasma().add_custom_code() == [_js.SURFACE_CODE]
    assert plasma_canvas().add_custom_code() == [_js.CANVAS_CODE]


def test_registry_guards_against_server_side_rendering() -> None:
    assert 'typeof window === "undefined"' in _js.REGISTRY_CODE


def test_snake_case_props_render_as_camel_case() -> None:
    props = _props(plasma_provider(background_selector="canvas.ground", background_blur=8, max_surfaces=4))
    assert props["backgroundSelector"] == '"canvas.ground"'
    assert props["backgroundBlur"] == "8"
    assert props["maxSurfaces"] == "4"


def test_as_underscore_renders_as_the_react_as_prop() -> None:
    assert _props(plasma(as_="header"))["as"] == '"header"'


def test_unset_props_are_omitted_so_library_defaults_survive() -> None:
    """Rendering a default value would silently pin the library's own default."""
    assert _props(plasma_provider()) == {}


def test_offset_dict_is_passed_through_to_the_surface() -> None:
    assert _props(plasma(offset={"x": 24, "y": 8}))["offset"] == '({ ["x"] : 24, ["y"] : 8 })'


def test_props_accept_state_vars() -> None:
    class _S(rx.State):
        mood: str = "tidal"

    assert "mood" in _props(plasma_provider(mood=_S.mood))


def test_provider_exposes_on_ready() -> None:
    assert "on_ready" in PlasmaProvider.get_event_triggers()


def test_surface_exposes_the_drag_and_form_lifecycle() -> None:
    triggers = Plasma.get_event_triggers()
    assert {"on_drag_start", "on_drag_end", "on_join_change", "on_forming", "on_formed"} <= set(triggers)


def test_on_drag_end_hands_the_settled_offset_to_the_handler() -> None:
    class _S(rx.State):
        offset: dict[str, float] = {}

        def save(self, offset: dict[str, float]):
            self.offset = offset

    component = plasma(on_drag_end=_S.save)
    assert "onDragEnd" in _props(component)


def test_children_stay_ordinary_dom() -> None:
    rendered = plasma(rx.el.strong("My app")).render()
    assert rendered["children"][0]["name"] == '"strong"'


def test_canvas_style_is_forwarded_as_a_real_inline_style() -> None:
    """Reflex would turn ``style=`` into a class, which cannot beat the canvas's own inline rules."""
    props = _props(plasma_canvas(canvas_style={"position": "absolute", "zIndex": 1}))
    assert "canvasStyle" in props
    assert "ReflexPlasmaCanvas" in _js.CANVAS_CODE
    assert "style: canvasStyle" in _js.CANVAS_CODE


def test_bounds_selector_becomes_a_ref_like_object_in_the_wrapper() -> None:
    assert "boundsSelector" in _props(plasma(bounds_selector="#stage"))
    assert "document.querySelector(boundsSelector)" in _js.SURFACE_CODE


def test_a_full_tree_renders() -> None:
    tree = plasma_provider(
        plasma(rx.el.h3("Inbox"), draggable=True, padding=20, bounds_selector="#stage"),
        plasma_canvas(z_index=2),
        mood="tidal",
        theme="dark",
        name="main",
    )
    rendered = tree.render()
    assert rendered["name"] == "ReflexPlasmaProvider"
    assert [c["name"] for c in rendered["children"]] == ["ReflexPlasma", "ReflexPlasmaCanvas"]
