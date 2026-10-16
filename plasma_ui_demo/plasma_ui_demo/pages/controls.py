"""Controls - the upstream 0.8.0 components, every value held in backend state.

* ``plasma_button``: solid / clear, three sizes, a click counter, a fused group.
* ``plasma_switch``: controlled from state; the switches drive provider props.
* ``plasma_slider``: frost, blend and elevation of the whole page, live.
* ``plasma_tabs``: the selected tab is the provider's mood.
* ``plasma_accordion``: single / multiple, the open values streamed back.
"""

from __future__ import annotations

import reflex as rx

from reflex_plasma_ui import (
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

from ..common import nav, seg

MOODS = {
    "tidal": "Deep teal into violet, a calm, slightly springy liquid.",
    "aurora": "Green and magenta, the loosest spring of the three.",
    "ember": "Wine into amber, the stiffest spring: it settles fast.",
}
FAQ = [
    ("what", "What is a control here?", "An ordinary plasma surface with real HTML inside: a button, a switch, a range input."),
    ("fuse", "Why do the items touch?", "Flush surfaces fuse, so the accordion reads as one column that grows as it opens."),
    ("state", "Where does the state live?", "In a Reflex State. Every change below is a backend event and comes back as a prop."),
]


class ControlsState(rx.State):
    """Every control value, plus the provider props they drive."""

    clicks: int = 0
    pointer_drop: bool = True
    ambient_drops: bool = False
    solid: bool = True
    frost: float = 0.2
    blend: float = 40.0
    elevation: float = 0.35
    mood: str = "tidal"
    accordion_type: str = "single"
    open_items: list[str] = ["what"]

    @rx.event
    def click(self):
        self.clicks += 1

    @rx.event
    def reset_clicks(self):
        self.clicks = 0

    @rx.event
    def set_flag(self, key: str, checked: bool):
        if key in {"pointer_drop", "ambient_drops", "solid"}:
            setattr(self, key, bool(checked))

    @rx.event
    def set_level(self, key: str, value: float):
        if key in {"frost", "blend", "elevation"}:
            setattr(self, key, float(value))

    @rx.event
    def set_mood(self, mood: str):
        if mood in MOODS:
            self.mood = mood

    @rx.event
    def set_accordion_type(self, kind: str):
        self.accordion_type = kind
        # "single" holds at most one open item.
        self.open_items = self.open_items[:1] if kind == "single" else self.open_items

    @rx.event
    def set_open(self, values: list[str]):
        self.open_items = values

    @rx.var
    def open_text(self) -> str:
        return ", ".join(self.open_items) or "none"


C = ControlsState


def _readout(*children: rx.Component | str) -> rx.Component:
    return rx.el.p(*children, class_name="readout")


def buttons() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Buttons"),
        rx.el.p(
            "plasma_button is its own surface: standalone it leans toward the pointer and pulses on press. "
            "on_click is an ordinary Reflex event. Set flush, buttons fuse into one piece.",
            class_name="section-lede",
        ),
        rx.el.div(
            plasma_button("Clicked ", rx.el.strong(C.clicks), solid=C.solid, size="lg", on_click=C.click),
            plasma_button("Reset", size="md", on_click=C.reset_clicks),
            plasma_button("Small", size="sm", tint="#ff5fa2", opacity=0.5),
            plasma_button("Disabled", disabled=True),
            class_name="ctl-row",
        ),
        rx.el.div(
            plasma_switch(
                label="Solid fill on the counter",
                checked=C.solid,
                on_checked_change=lambda v: C.set_flag("solid", v),
            ),
            class_name="ctl-row",
        ),
        rx.el.div(
            plasma_button("Bold", size="sm"),
            plasma_button("Italic", size="sm"),
            plasma_button("Underline", size="sm"),
            class_name="ctl-group",
            role="group",
            aria_label="A fused button group",
        ),
    )


def switches() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Switches"),
        rx.el.p(
            "plasma_switch is controlled from state: checked comes from the backend and "
            "on_checked_change sends the new value back. These two drive the provider itself.",
            class_name="section-lede",
        ),
        rx.el.div(
            plasma_switch(
                label="Pointer drop",
                checked=C.pointer_drop,
                on_checked_change=lambda v: C.set_flag("pointer_drop", v),
            ),
            plasma_switch(
                label="Ambient drops",
                checked=C.ambient_drops,
                on_checked_change=lambda v: C.set_flag("ambient_drops", v),
                checked_tint="#b58cff",
            ),
            plasma_switch(label="Uncontrolled", default_checked=True),
            plasma_switch(label="Disabled", disabled=True),
            class_name="ctl-row",
        ),
        _readout(
            "pointer_drop=",
            rx.el.code(rx.cond(C.pointer_drop, "True", "False")),
            "  ambient_drops=",
            rx.el.code(rx.cond(C.ambient_drops, "True", "False")),
        ),
    )


def _slider(label: str, key: str, lo: float, hi: float, step: float) -> rx.Component:
    value = getattr(C, key)
    return rx.el.div(
        rx.el.label(label, rx.el.span(value), id=f"lbl-{key}"),
        plasma_slider(
            value=value,
            min=lo,
            max=hi,
            step=step,
            on_value_change=lambda v: C.set_level(key, v),
            aria_labelledby=f"lbl-{key}",
        ),
        class_name="ctl-slider",
    )


def sliders() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Sliders"),
        rx.el.p(
            "plasma_slider is a native range input under a plasma track, so keyboard and touch are the "
            "browser's. These set frost, blend and elevation for every surface on the page; drag blend past "
            "the gap in the button group above and watch it bridge.",
            class_name="section-lede",
        ),
        rx.el.div(
            _slider("Frost", "frost", 0, 1, 0.05),
            _slider("Blend (px)", "blend", 0, 80, 1),
            _slider("Elevation", "elevation", 0, 1, 0.05),
            class_name="ctl-sliders",
        ),
    )


def tabs() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Tabs"),
        rx.el.p(
            "plasma_tab_list lays the tabs out flush, so they fuse into one segmented surface. The selected "
            "tab is state, and here it is also the provider's mood.",
            class_name="section-lede",
        ),
        plasma_tabs(
            plasma_tab_list(
                *[plasma_tab(m.capitalize(), value=m) for m in MOODS],
                aria_label="Mood",
            ),
            *[plasma_tab_panel(rx.el.p(text, class_name="ctl-panel"), value=m) for m, text in MOODS.items()],
            value=C.mood,
            on_value_change=C.set_mood,
        ),
        _readout("mood=", rx.el.code(C.mood)),
    )


def accordion() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Accordion"),
        rx.el.p(
            "plasma_accordion stacks disclosure panels that fuse into one column. The open items are always "
            "a list of values, in both modes.",
            class_name="section-lede",
        ),
        seg(["single", "multiple"], C.accordion_type, C.set_accordion_type, small=True, label="Accordion type"),
        rx.el.div(
            plasma_accordion(
                *[plasma_accordion_item(rx.el.p(body), value=v, title=title) for v, title, body in FAQ],
                type=C.accordion_type,
                value=C.open_items,
                on_value_change=C.set_open,
            ),
            class_name="ctl-accordion",
        ),
        _readout("open=", rx.el.code(C.open_text)),
    )


def page() -> rx.Component:
    return plasma_provider(
        nav("/controls"),
        rx.el.main(
            buttons(),
            switches(),
            sliders(),
            tabs(),
            accordion(),
            rx.el.footer("reflex-plasma-ui · Controls · @cruxgarden/plasma-ui 0.8.0", class_name="footer"),
            class_name="site",
            style={"paddingTop": "40px"},
        ),
        mood=C.mood,
        theme="dark",
        frost=C.frost,
        blend=C.blend,
        elevation=C.elevation,
        pointer_drop=C.pointer_drop,
        ambient_drops=C.ambient_drops,
        # Four buttons, a group of three, five switches, three sliders, three tabs, three items.
        max_surfaces=24,
    )
