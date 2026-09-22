"""Workspace - a Reflex port of the upstream real-world example.

Everything on screen is a plasma surface: the top bar, the dock and four
working panels. Shown here:

* draggable panels with edge/grid snapping and join-aware padding
* the focused panel raised through per-surface ``elevation``
* the layout persisted to localStorage (``rx.LocalStorage``)
* interactive content (list selection, checkboxes) kept clickable with ``NO_DRAG``
* mood / frost switching at runtime, and ``bump`` from a backend event
"""

from __future__ import annotations

import asyncio
import json

import reflex as rx

from reflex_plasma_ui import NO_DRAG, bump, plasma, plasma_provider

from ..common import nav_links

MAIL = [
    {"id": 1, "from": "Ana", "subject": "Launch checklist", "body": "Docs page is live. The PyPI publish is the last step - want to pair at 4?"},
    {"id": 2, "from": "Sam", "subject": "Panel resize", "body": "Filed the resize-handle issue with a sketch of the edge hit areas."},
    {"id": 3, "from": "Priya", "subject": "Demo feedback", "body": "The drag-and-fuse moment lands. Lead with it in the video."},
    {"id": 4, "from": "Theo", "subject": "Perf numbers", "body": "Sixteen panels holds 60fps on the M1 Air. Notes attached."},
]
TASKS = ["Tag v0.1.0", "Write announcement", "Record demo clip", "Publish to PyPI"]
PANELS = ["inbox", "reader", "tasks", "player"]
TRACK = 224


def _snap24(v: float) -> int:
    return max(24, round(v / 24) * 24)


class WorkspaceState(rx.State):
    """Mood, frost, focus, the layout and the panel contents."""

    mood: str = "tidal"
    frost: float = 0.35
    focused: str = "inbox"
    mail_id: int = 1
    done: list[bool] = [True, False, False, False]
    playing: bool = False
    t: int = 41
    dims: dict[str, int] = {"w": 984, "h": 552}
    layout: dict[str, dict[str, float]] = {}
    saved: str = rx.LocalStorage("", name="plasma-workspace-layout")

    @rx.var
    def col(self) -> int:
        return _snap24(min(336, self.dims["w"] * 0.38))

    @rx.var
    def row(self) -> int:
        return _snap24(self.dims["h"] * 0.52)

    @rx.var
    def home(self) -> dict[str, dict[str, float]]:
        c, r = self.col, self.row
        return {"inbox": {"x": 0, "y": 0}, "reader": {"x": c, "y": 0}, "tasks": {"x": 0, "y": r}, "player": {"x": c, "y": r}}

    @rx.var
    def offsets(self) -> dict[str, dict[str, float]]:
        home = self.home
        return {k: self.layout.get(k, home[k]) for k in PANELS}

    @rx.var
    def sizes(self) -> dict[str, dict[str, str]]:
        w, h, c, r = self.dims["w"], self.dims["h"], self.col, self.row
        return {
            "inbox": {"width": f"{c}px", "height": f"{r}px"},
            "reader": {"width": f"{w - c}px", "height": f"{r}px"},
            "tasks": {"width": f"{c}px", "height": f"{h - r}px"},
            "player": {"width": f"{w - c}px", "height": f"{h - r}px"},
        }

    @rx.var
    def mail(self) -> dict[str, str]:
        m = next(m for m in MAIL if m["id"] == self.mail_id)
        return {"from": m["from"], "subject": m["subject"], "body": m["body"]}

    @rx.var
    def clock(self) -> str:
        return f"{self.t // 60}:{self.t % 60:02d} / 3:44"

    @rx.var
    def progress(self) -> str:
        return f"{self.t / TRACK * 100:.2f}%"

    @rx.event
    def measure(self, dims: dict[str, int]):
        """Size the 2x2 grid to the stage and restore any saved layout."""
        self.dims = {"w": int(dims.get("w", 984)), "h": int(dims.get("h", 552))}
        if self.saved and not self.layout:
            try:
                self.layout = json.loads(self.saved)
            except ValueError:
                self.layout = {}

    @rx.event
    def set_mood(self, mood: str):
        self.mood = mood

    @rx.event
    def set_frost(self, value: float):
        self.frost = float(value)

    @rx.event
    def focus(self, panel: str):
        self.focused = panel

    @rx.event
    def moved(self, panel: str, offset: dict[str, float]):
        """A panel settled: keep and persist the layout."""
        self.layout = {**self.layout, panel: {"x": float(offset["x"]), "y": float(offset["y"])}}
        self.saved = json.dumps(self.layout)

    @rx.event
    def reset_layout(self):
        self.layout = dict(self.home)
        self.saved = json.dumps(self.layout)

    @rx.event
    def open_mail(self, mail_id: int):
        self.mail_id = mail_id
        self.focused = "reader"

    @rx.event
    def toggle_task(self, index: int):
        self.done[index] = not self.done[index]

    @rx.event
    def toggle_play(self):
        """Play/pause - and bump the plasma, from the backend."""
        self.playing = not self.playing
        yield bump(0.6)
        if self.playing:
            yield WorkspaceState.tick

    @rx.event(background=True)
    async def tick(self):
        while True:
            await asyncio.sleep(1)
            async with self:
                if not self.playing:
                    return
                self.t = (self.t + 1) % TRACK


W = WorkspaceState
MEASURE = "(() => { const s = document.getElementById('wstage'); return { w: Math.floor(s?.clientWidth || 984), h: Math.floor(s?.clientHeight || 552) }; })()"


def _panel(pid: str, *children: rx.Component, label: str) -> rx.Component:
    return plasma(
        *children,
        class_name=f"wpanel {pid}",
        offset=W.offsets[pid],
        on_drag_end=lambda o: W.moved(pid, o),
        on_drag_start=W.focus(pid),
        on_click=W.focus(pid),
        elevation=rx.cond(W.focused == pid, 0.75, 0.3),
        bounds_selector="#wstage",
        draggable=True,
        padding=18,
        width=W.sizes[pid]["width"],
        height=W.sizes[pid]["height"],
        aria_label=label,
    )


def page() -> rx.Component:
    mood_seg = rx.el.div(
        *[
            rx.el.button(m.capitalize(), aria_pressed=rx.cond(W.mood == m, "true", "false"), on_click=W.set_mood(m))
            for m in ["tidal", "aurora", "ember"]
        ],
        class_name="seg",
        role="group",
        aria_label="Mood",
    )
    bar = plasma(
        rx.el.div(
            rx.el.a("Workspace", href="/", class_name="wordmark"),
            rx.el.span("an example app built with reflex-plasma-ui - drag any panel", class_name="hint"),
            nav_links("/workspace"),
            mood_seg,
            rx.el.label(
                "Frost",
                rx.el.input(type="range", min=0, max=1, step=0.05, value=W.frost, on_change=W.set_frost, custom_attrs=NO_DRAG),
                class_name="frost",
            ),
            rx.el.button("Reset layout", class_name="ghost", on_click=W.reset_layout, custom_attrs=NO_DRAG),
            class_name="plate hrow",
        ),
        as_="header",
        class_name="bar",
        radius=22,
        lean=False,
        padding=18,
        elevation=0.5,
        fuse=False,
    )
    dock = plasma(
        rx.el.div(
            *[rx.el.button(g, class_name="dockbtn", aria_label=f"Dock item {i + 1}", on_click=W.focus(p))
              for i, (g, p) in enumerate(zip(["📥", "✓", "▶", "⚙"], ["inbox", "tasks", "player", "reader"], strict=True))],
            class_name="plate col",
        ),
        as_="nav",
        class_name="dock",
        radius=22,
        lean=False,
        padding=18,
        fuse=False,
        aria_label="Dock",
    )
    inbox = _panel(
        "inbox",
        rx.el.div(
            rx.el.h2("Inbox"),
            rx.el.ul(
                *[
                    rx.el.li(rx.el.button(
                        rx.el.strong(m["from"]), " ", m["subject"],
                        aria_pressed=rx.cond(W.mail_id == m["id"], "true", "false"),
                        on_click=W.open_mail(m["id"]),
                    ))
                    for m in MAIL
                ],
                custom_attrs=NO_DRAG,
            ),
            class_name="plate col",
        ),
        label="Inbox panel",
    )
    reader = _panel(
        "reader",
        rx.el.div(
            rx.el.h2(W.mail["subject"]),
            rx.el.span(W.mail["from"], class_name="from"),
            rx.el.p(W.mail["body"]),
            class_name="plate col",
        ),
        label="Reader panel",
    )
    tasks = _panel(
        "tasks",
        rx.el.div(
            rx.el.h2("Tasks"),
            rx.el.ul(
                *[
                    rx.el.li(rx.el.label(
                        rx.el.input(type="checkbox", checked=W.done[i], on_change=W.toggle_task(i)),
                        t,
                        class_name=rx.cond(W.done[i], "done", ""),
                    ))
                    for i, t in enumerate(TASKS)
                ],
                custom_attrs=NO_DRAG,
            ),
            class_name="plate col",
        ),
        label="Tasks panel",
    )
    player = _panel(
        "player",
        rx.el.div(
            rx.el.h2("Now playing"),
            rx.el.span("Sea of Tranquility - Side B", class_name="from"),
            rx.el.div(rx.el.span(style={"width": W.progress}), class_name="progress"),
            rx.el.div(
                rx.el.span(W.clock, class_name="time"),
                rx.el.button(rx.cond(W.playing, "Pause", "Play"), class_name="ghost", on_click=W.toggle_play, custom_attrs=NO_DRAG),
                class_name="hrow",
            ),
            class_name="plate col",
        ),
        label="Player panel",
    )
    return plasma_provider(
        rx.el.div(
            bar,
            rx.el.div(
                dock,
                rx.el.div(inbox, reader, tasks, player, id="wstage", class_name="wstage",
                          on_mount=rx.call_script(MEASURE, callback=W.measure)),
                class_name="wbody",
            ),
            class_name="app",
        ),
        mood=W.mood,
        theme="dark",
        frost=W.frost,
        blend=20,
        grid=24,
    )
