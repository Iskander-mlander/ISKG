"""Headless smoke tests.

Builds a real widget tree via :meth:`iskg.Application.test_loop` — no
GTK/WebKit or display required, so it always runs in CI. The real-window
smoke that drove an actual pywebview window under xvfb was removed: it
never stabilised in GitHub Actions.
"""

from __future__ import annotations

import os
import subprocess
import sys

from iskg import (
    Application,
    Button,
    Frame,
    Label,
    Menu,
    ProgressBar,
    ScrolledFrame,
    Slider,
)


def _build_demo_app() -> Application:
    app = Application("ISKG E2E", 640, 480, theme="cold")
    root = Frame(parent=None, height_mode="flex")
    Label(root, text="ISKG smoke", font_size=18).grid(row=0, column=0, columnspan=2)
    p = ProgressBar(root, max_=100, value=40)
    p.grid(row=1, column=0)
    s = Slider(root, from_=0, to=10, value=4)
    s.grid(row=1, column=1)
    sf = ScrolledFrame(root)
    sf.grid(row=2, column=0, columnspan=2)
    Label(sf, text="log line 1")
    Label(sf, text="log line 2")
    Button(root, text="Go", command=lambda: None).grid(row=3, column=0)
    app.add(root)
    return app


def _widgets(app: Application) -> list[object]:
    out: list[object] = []
    for w in app._root_widgets:
        out.extend(w._collect_widgets())
    return [w for _, w in out]


def test_smoke_headless_builds_tree():
    app = _build_demo_app()
    loop = app.test_loop()
    assert "ISKG smoke" in loop.html
    assert "log line 2" in loop.html
    assert "ProgressBar" in loop.html or "iskg-progress" in loop.html
    loop.stop()


def test_smoke_headless_roundtrip():
    app = _build_demo_app()
    loop = app.test_loop()
    slider = None
    for w in _widgets(app):
        if isinstance(w, Slider):
            slider = w
            break
    assert slider is not None
    slider.value = 7
    js = "".join(loop.js_calls)
    assert "el.value=7" in js
    loop.stop()


def test_smoke_headless_fire_command():
    app = _build_demo_app()
    loop = app.test_loop()
    got = []
    for w in _widgets(app):
        if isinstance(w, Button):
            w.bind("click", lambda data: got.append(1))
            loop.fire(w._id, "click", "")
    assert got, "button command must be reachable via the bridge"
    loop.stop()


def test_contextmenu_headless_command():
    app = _build_demo_app()
    loop = app.test_loop()
    btn = next(w for w in _widgets(app) if isinstance(w, Button))

    calls = []
    menu = Menu()
    menu.add_item("Copy", command=lambda: calls.append("copy"))
    sub = menu.add_menu("Export")
    sub.add_item("PNG", command=lambda: calls.append("png"))

    btn.set_menu(menu)
    js = "".join(loop.js_calls)
    assert 'iskg_bind_contextmenu("' + btn._id + '")' in js

    loop.fire(btn._id, "contextmenu", {"x": 10, "y": 20})
    js = "".join(loop.js_calls)
    unescaped = js.replace('\\"', '"')
    assert 'iskg_open_contextmenu("' + btn._id + '"' in js
    assert 'data-cmd="Copy"' in unescaped
    assert 'data-cmd="Export/PNG"' in unescaped

    loop.fire(btn._id, "contextcmd", "Copy")
    assert calls == ["copy"]
    loop.fire(btn._id, "contextcmd", "Export/PNG")
    assert calls == ["copy", "png"]
    loop.fire(btn._id, "contextcmd", "Export/Missing")
    assert calls == ["copy", "png"]
    loop.stop()


def test_contextmenu_bind_reports_position():
    app = _build_demo_app()
    loop = app.test_loop()
    btn = next(w for w in _widgets(app) if isinstance(w, Button))

    got = []
    btn.bind("contextmenu", lambda data: got.append(data))
    loop.fire(btn._id, "contextmenu", {"x": 10, "y": 20})
    assert got and got[0]["x"] == 10 and got[0]["y"] == 20
    loop.stop()


def test_smoke_script_entrypoint():
    """The R3 launcher smoke must still be importable/runnable headless."""
    here = os.path.dirname(os.path.abspath(__file__))
    rc = subprocess.run(
        [
            sys.executable,
            "-c",
            "from iskg import Application; app=Application(); app.test_loop().stop(); print('ok')",
        ],
        capture_output=True,
        text=True,
        cwd=os.path.join(here, ".."),
    )
    assert rc.returncode == 0
    assert "ok" in rc.stdout
