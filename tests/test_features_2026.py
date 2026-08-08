"""Tests for the 2026-08 feature batch.

Covers the event bus, TimeSeriesGraph/Sparkline, LogViewer, Clock/DatePicker,
window-level shortcuts, and widget drag & drop.
"""

from __future__ import annotations

from datetime import date

import pytest

from iskg import (
    Application,
    Button,
    Clock,
    DatePicker,
    Frame,
    LogViewer,
    Sparkline,
    TimeSeriesGraph,
)

# ── Event bus ─────────────────────────────────────────────────────────────────


def test_event_bus_on_off_emit():
    app = Application("t")
    seen = []

    @app.on("my-event")
    def handler(value):
        seen.append(value)

    app.emit("my-event", 42)
    assert seen == [42]

    app.off("my-event", handler)
    app.emit("my-event", 99)
    assert seen == [42]

    app.off("my-event")
    app.emit("my-event", 1)
    assert seen == [42]


def test_event_bus_theme_changed():
    app = Application("t")
    seen = []
    app.on("theme-changed", lambda name: seen.append(name))
    app.set_theme("cold")
    assert seen[-1] == "cold"


def test_event_bus_widget_created():
    app = Application("t")
    seen = []
    app.on("widget-created", lambda wid: seen.append(wid))
    btn = Button(parent=None)
    app.add(btn)
    assert btn._id in seen


# ── Charts ───────────────────────────────────────────────────────────────────


def test_timeseriesgraph_multiseries():
    app = Application("t")
    g = TimeSeriesGraph(parent=None, series={"cpu": "green", "mem": "cyan"})
    g.append("cpu", 42)
    g.append("cpu", 90)
    g.replace("mem", [10, 20, 30])
    app.add(g)
    loop = app.test_loop()
    assert "cpu" in loop.html and "mem" in loop.html
    assert g.values["cpu"] == [42.0, 90.0]
    g.append("cpu", 5)
    assert "".join(loop.js_calls)
    loop.stop()


def test_chart_smooth_path():
    app = Application("t")
    g = TimeSeriesGraph(parent=None)
    g.replace([10, 30, 20, 40, 25])
    app.add(g)
    loop = app.test_loop()
    assert "<polyline" not in loop.html
    assert "<path" in loop.html
    assert "C" in loop.html  # cubic Bézier segments
    loop.stop()

    app2 = Application("t2")
    g2 = TimeSeriesGraph(parent=None, smooth=False)
    g2.replace([10, 30, 20, 40, 25])
    app2.add(g2)
    loop2 = app2.test_loop()
    assert "<polyline" in loop2.html
    assert "<path" not in loop2.html
    loop2.stop()


def test_sparkline_single_series_convenience():
    s = Sparkline(parent=None)
    s.append(3.3)
    s.append(4.1)
    s.replace([10, 20, 30])
    assert s.values[next(iter(s.values))] == [10.0, 20.0, 30.0]
    s.clear()
    assert not any(s.values.values())


def test_chart_max_points_trims():
    g = TimeSeriesGraph(parent=None, max_pts=5)
    for i in range(10):
        g.append(i)
    vals = g.values[next(iter(g.values))]
    assert len(vals) == 5
    assert vals == [5.0, 6.0, 7.0, 8.0, 9.0]


# ── LogViewer ────────────────────────────────────────────────────────────────


def test_logviewer_append_levels_and_clear():
    app = Application("t")
    lv = LogViewer(parent=None, max_lines=2)
    lv.append("first", "INFO")
    lv.append("second", "ERROR")
    app.add(lv)
    loop = app.test_loop()
    assert "[INFO]" in loop.html and "[ERROR]" in loop.html
    lv.append("third", "WARN")  # trims to last 2
    assert [lvl for lvl, _ in lv.lines] == ["ERROR", "WARN"]
    assert any("WARN" in c for c in loop.js_calls)
    lv.clear()
    assert lv.lines == []
    loop.stop()


# ── Clock / DatePicker ───────────────────────────────────────────────────────


def test_clock_renders_ticking_js():
    app = Application("t")
    ck = Clock(parent=None, seconds=False, military=False)
    app.add(ck)
    loop = app.test_loop()
    assert "iskg-clock" in loop.html
    assert "setInterval" in loop.html
    # seconds=False guards the seconds branch at runtime (JS `if(false)`)
    assert "if(false)iskg_bridge_event" in loop.html
    loop.stop()


def test_datepicker_open_nav_select():
    app = Application("t")
    chosen = []
    dp = DatePicker(parent=None, date=date(2026, 8, 15), command=chosen.append)
    app.add(dp)
    loop = app.test_loop()
    assert "2026-08-15" in loop.html

    loop.fire(dp._id, "open", "")
    js = "".join(loop.js_calls)
    assert "August 2026" in js

    loop.fire(dp._id, "nav", "1")
    js = "".join(loop.js_calls)
    assert "September 2026" in js

    loop.fire(dp._id, "select", "2026-09-03")
    assert dp.value == date(2026, 9, 3)
    assert chosen == [date(2026, 9, 3)]
    assert dp.iso == "2026-09-03"
    loop.stop()


def test_datepicker_popup_overlays_clipped_parent():
    """The calendar popup must use fixed positioning to escape a parent
    that clips/overflows hidden, mirroring the combobox dropdown fix."""
    app = Application("t")
    card = Frame(parent=None, text="short card")
    card._config_dict["height"] = 60
    card._config_dict["overflow"] = "hidden"
    DatePicker(parent=card, date=date(2026, 8, 15))
    app.add(card)
    loop = app.test_loop()

    html = loop.html.replace('\\"', '"')
    assert 'popup.style.position="fixed"' in html
    assert "getBoundingClientRect" in html
    # closing restores the popup to its default (absolute/empty) position
    assert 'popup.style.position="";popup.style.top="";popup.style.left="";' in html
    # outside click closes the popup
    assert "contains(e.target)" in html
    loop.stop()


# ── Window-level shortcuts ───────────────────────────────────────────────────


def test_global_shortcut_bind_and_dispatch():
    app = Application("t")
    got = []
    app.bind("<Control-s>", lambda d: got.append(("ctrl-s", d.get("key"))))
    app.bind("<KeyRelease-a>", lambda d: got.append(("rel-a", d.get("key"))))
    loop = app.test_loop()
    assert 'iskg_bind_global_key("keypress","s",{"ctrl": true});' in loop.html

    loop.fire("__iskg_global__", "key", {"key": "s", "code": "KeyS", "ctrl": True})
    assert got == [("ctrl-s", "s")]
    loop.fire("__iskg_global__", "global", {"key": "a", "code": "KeyA"})
    assert got == [("ctrl-s", "s"), ("rel-a", "a")]
    loop.stop()


def test_global_shortcut_rejects_non_key_event():
    app = Application("t")
    with pytest.raises(ValueError):
        app.bind("click", lambda d: None)


# ── Drag & drop ──────────────────────────────────────────────────────────────


def test_drag_drop_between_widgets():
    app = Application("t")
    src = Button(parent=None, text="Drag me", draggable=True)
    tgt = Frame(parent=None)
    drops = []
    tgt.bind("<<Drop>>", drops.append)
    app.add(src)
    app.add(tgt)
    loop = app.test_loop()
    assert 'draggable="true"' in loop.html
    assert "iskg-drop-target" in loop.html
    assert "iskg_register_dnd" in loop.html

    loop.fire(tgt._id, "drop", {"source": src._id, "x": 4, "y": 5, "target": tgt._id})
    assert drops and drops[0]["source"] == src._id and drops[0]["x"] == 4
    loop.stop()
