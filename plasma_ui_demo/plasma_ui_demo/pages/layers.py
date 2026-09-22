"""Layers - backgrounds, the surface lifecycle, pulses and a dialog above a scrim.

* ``background``: the procedural mood field, a CSS color, or an image URL.
* ``form_in`` / ``form_out`` / ``form_speed`` with ``on_forming`` / ``on_formed``
  streamed to the backend.
* ``pulse_on_press`` / ``pulse`` / ``bump``.
* Two providers: the ground keeps its frames (``preserve_drawing_buffer``) and
  renders its canvas as ``canvas.ground``; the dialog's provider draws with a
  clear ground and refracts that canvas (``background_selector``).
"""

from __future__ import annotations

from datetime import datetime

import reflex as rx

from reflex_plasma_ui import bump, plasma, plasma_canvas, plasma_provider, presets, pulse, pulse_on_press

from ..common import nav, seg, slider, toggle

BACKGROUNDS = {"field": "", "color": "#1b2a3a", "image": "/backdrop.jpg"}
TINTS = ["#ff5fa2", "#5fd4ff", "#b58cff", "#ffb347", "#6cf2a8", "#ff7a5c", "#7c9bff", "#f4e36b"]


class LayersState(rx.State):
    """Background, lifecycle cards and the dialog."""

    background: str = "field"
    cards: list[int] = [1, 2, 3]
    next_id: int = 4
    form_speed: float = 1.0
    form_out: bool = True
    log: list[str] = []
    strength: float = 1.0
    dialog_open: bool = False
    dialog_ready: bool = False

    @rx.var
    def background_src(self) -> str:
        return BACKGROUNDS.get(self.background, "")

    @rx.var
    def card_items(self) -> list[dict[str, str]]:
        return [{"id": str(c), "title": f"Surface {c}", "tint": TINTS[c % len(TINTS)]} for c in self.cards]

    def _log(self, text: str):
        self.log = [f"{datetime.now():%H:%M:%S}  {text}", *self.log][:7]

    @rx.event
    def set_background(self, name: str):
        self.background = name

    @rx.event
    def add_card(self):
        if len(self.cards) < 8:
            self.cards = [*self.cards, self.next_id]
            self.next_id += 1

    @rx.event
    def remove_card(self):
        if self.cards:
            gone = self.cards[-1]
            self.cards = self.cards[:-1]
            self._log(f"surface {gone} removed" + (" - forming out" if self.form_out else ""))

    @rx.event
    def set_speed(self, value: float):
        self.form_speed = float(value)

    @rx.event
    def flip_form_out(self):
        self.form_out = not self.form_out

    @rx.event
    def set_strength(self, value: float):
        self.strength = float(value)

    @rx.event
    def forming(self, card: str):
        self._log(f"surface {card}: on_forming")

    @rx.event
    def formed(self, card: str):
        self._log(f"surface {card}: on_formed")

    @rx.event
    def open_dialog(self):
        self.dialog_open, self.dialog_ready = True, False

    @rx.event
    def close_dialog(self):
        self.dialog_open, self.dialog_ready = False, False

    @rx.event
    def dialog_formed(self):
        """The dialog's material has arrived: reveal its contents."""
        self.dialog_ready = True
        self._log("dialog: on_formed - contents revealed")


L = LayersState


def backgrounds() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Backgrounds"),
        rx.el.p(
            "background takes a CSS color (luminance drift), an image URL (refracted, slow swirl) or, "
            "left unset, the procedural mood field. It is live: switch it and every surface refracts the new ground.",
            class_name="section-lede",
        ),
        seg(list(BACKGROUNDS), L.background, L.set_background, label="Background"),
    )


def lifecycle() -> rx.Component:
    card = lambda c: plasma(  # noqa: E731
        rx.el.div(rx.el.h3(c["title"]), rx.el.small("formed in, then its contents faded in"), class_name="plate"),
        class_name="chip",
        tint=c["tint"],
        opacity=0.35,
        padding=16,
        on_forming=L.forming(c["id"]),
        on_formed=L.formed(c["id"]),
        key=c["id"],
    )
    return rx.el.section(
        rx.el.h2("Lifecycle"),
        rx.el.p(
            "A surface forms in when it mounts and, with form_out, shrinks away when it unmounts. "
            "on_forming and on_formed reach the backend; the demo CSS holds each card's contents "
            "back while the element carries data-plasma-forming.",
            class_name="section-lede",
        ),
        rx.el.div(
            rx.el.button("Add surface", class_name="btn", on_click=L.add_card, disabled=L.cards.length() >= 8),
            rx.el.button("Remove surface", class_name="btn", on_click=L.remove_card, disabled=L.cards.length() == 0),
            class_name="row wrap",
        ),
        rx.el.div(
            rx.el.div(slider("Form speed", L.form_speed, L.set_speed, 0.25, 3, 0.25, "x"), style={"flex": "1"}),
            rx.el.div(toggle("Form out", L.form_out, L.flip_form_out), style={"flex": "1"}),
            class_name="row",
            style={"maxWidth": "560px", "gap": "32px"},
        ),
        rx.el.div(rx.foreach(L.card_items, card), class_name="lgrid"),
        rx.el.div(rx.foreach(L.log, lambda line: rx.el.div(line)), class_name="log"),
    )


def pulses() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Pulses"),
        rx.el.p(
            "pulse_on_press() marks an element so pressing it (not its children) sends a pulse from the "
            "pointer. pulse() and bump() are client-side events you can wire to any trigger or return "
            "from a backend handler.",
            class_name="section-lede",
        ),
        rx.el.div(
            rx.el.button("pulse(x=120, y=120)", class_name="btn", on_click=pulse(120, 120)),
            rx.el.button("bump(0.9)", class_name="btn", on_click=bump(0.9)),
            class_name="row wrap",
        ),
        rx.el.div(slider("Pad strength", L.strength, L.set_strength, 0.2, 3, 0.1), style={"maxWidth": "320px"}),
        rx.el.div(
            "Press anywhere in here",
            class_name="pulse-pad",
            # pulse_on_press() gives the attributes; the strength follows state.
            custom_attrs={**pulse_on_press(), "data-plasma-pulse-strength": L.strength},
        ),
    )


def dialog_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("A dialog above a scrim"),
        rx.el.p(
            "One canvas sits behind everything, so a dialog above a scrim needs a second provider: "
            "ground=\"clear\" draws only its own surfaces, and background_selector=\"canvas.ground\" "
            "hands it the first canvas to refract. Its contents wait for on_formed.",
            class_name="section-lede",
        ),
        rx.el.button("Open the dialog", class_name="btn primary", on_click=L.open_dialog),
    )


def dialog() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="scrim", on_click=L.close_dialog),
        plasma_provider(
            plasma_canvas(canvas_style={"position": "absolute", "zIndex": 1}),
            plasma(
                rx.el.div(
                    rx.cond(
                        L.dialog_ready,
                        rx.fragment(
                            rx.el.h2("Plasma, twice"),
                            rx.el.p(
                                "This panel lives on its own clear-ground canvas, refracting the page's "
                                "ground canvas underneath the scrim.",
                                style={"color": "var(--muted)"},
                            ),
                            rx.el.div(
                                rx.el.button("Pulse the dialog", class_name="btn", on_click=pulse(provider="overlay")),
                                rx.el.button("Close", class_name="btn primary", on_click=L.close_dialog),
                                class_name="row",
                            ),
                        ),
                    ),
                    class_name="plate",
                    style={"minHeight": "180px"},
                ),
                class_name="dialog-panel",
                elevation=0.7,
                padding=14,
                radius=30,
                lean=False,
                on_formed=L.dialog_formed,
                role="dialog",
                aria_modal="true",
                aria_label="Example dialog",
            ),
            name="overlay",
            background_selector="canvas.ground",
            **presets.OVERLAY,
        ),
        class_name="dialog-root",
    )


def page() -> rx.Component:
    return plasma_provider(
        plasma_canvas(class_name="ground"),
        nav("/layers"),
        rx.el.main(
            backgrounds(),
            lifecycle(),
            pulses(),
            dialog_section(),
            rx.el.footer("reflex-plasma-ui · Layers", class_name="footer"),
            class_name="site",
            style={"paddingTop": "40px"},
        ),
        rx.cond(L.dialog_open, dialog()),
        mood="aurora",
        theme="dark",
        background=L.background_src,
        preserve_drawing_buffer=True,
        canvas=False,
        form_out=L.form_out,
        form_speed=L.form_speed,
    )
