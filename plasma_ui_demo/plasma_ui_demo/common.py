"""Small UI helpers shared by the demo pages (plain HTML, styled by plasma_demo.css)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import reflex as rx

PAGES = [
    ("Playground", "/"),
    ("Workspace", "/workspace"),
    ("Materials", "/materials"),
    ("Layers", "/layers"),
]


def nav_links(active: str) -> rx.Component:
    """Links to every demo page."""
    return rx.el.div(
        *[
            rx.el.a(name, href=href, aria_current="page" if href == active else None)
            for name, href in PAGES
        ],
        class_name="nav-links",
    )


def nav(active: str, *extra: rx.Component) -> rx.Component:
    """The fixed frosted CSS nav used by the scrolling pages."""
    return rx.el.nav(
        rx.el.a("Plasma UI", rx.el.small("for Reflex"), class_name="brand", href="/"),
        nav_links(active),
        *extra,
        class_name="nav",
        aria_label="Sections",
    )


def slider(
    label: str,
    value: rx.Var,
    on_change: Callable[[Any], Any],
    min_: float,
    max_: float,
    step: float,
    unit: str = "",
) -> rx.Component:
    """A labelled range input showing its current value."""
    return rx.el.div(
        rx.el.label(label, rx.el.span(value, unit)),
        rx.el.input(
            type="range",
            min=min_,
            max=max_,
            step=step,
            value=value,
            on_change=on_change,
            aria_label=label,
        ),
        class_name="field",
    )


def toggle(label: str, value: rx.Var[bool], on_click: Any) -> rx.Component:
    """An accessible on/off switch."""
    return rx.el.div(
        rx.el.span(label, class_name="flabel"),
        rx.el.button(
            rx.el.span(),
            role="switch",
            aria_checked=rx.cond(value, "true", "false"),
            aria_label=label,
            class_name="switch",
            on_click=on_click,
        ),
        class_name="field inline",
    )


def select_field(label: str, value: rx.Var[str], options: list[str], on_change: Any) -> rx.Component:
    """A labelled native select."""
    return rx.el.div(
        rx.el.span(label, class_name="flabel"),
        rx.el.select(
            *[rx.el.option(o, value=o) for o in options],
            value=value,
            on_change=on_change,
            aria_label=label,
        ),
        class_name="field inline",
    )


def color_field(label: str, value: rx.Var[str], on_change: Any) -> rx.Component:
    """A labelled color input with its hex value."""
    return rx.el.div(
        rx.el.span(label, class_name="flabel"),
        rx.el.span(
            rx.el.input(type="color", value=value, on_change=on_change, aria_label=label),
            rx.el.code(value),
            class_name="color",
        ),
        class_name="field inline",
    )


def seg(options: list[str], current: rx.Var[str], on_pick: Callable[[str], Any], small: bool = False, label: str = "") -> rx.Component:
    """A segmented control (static option list)."""
    return rx.el.div(
        *[
            rx.el.button(
                o,
                aria_pressed=rx.cond(current == o, "true", "false"),
                on_click=on_pick(o),
            )
            for o in options
        ],
        class_name="seg small" if small else "seg",
        role="group",
        aria_label=label,
    )
