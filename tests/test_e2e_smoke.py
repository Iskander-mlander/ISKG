"""E2E smoke tests.

Two tiers:

1. **Headless** (default): builds a real widget tree via
   :meth:`iskg.Application.test_loop` — no GTK/WebKit or display required, so
   it always runs in CI.

2. **Real window** (``ISKG_SMOKE_TEST=1``): opens an actual pywebview window
   and drives it for a couple of seconds, verifying the bridge round-trip.
   Skipped by default; run with ``xvfb-run -a pytest tests/test_e2e_smoke.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from iskg import (
    Application,
    Button,
    Frame,
    Label,
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


@pytest.mark.skipif(
    os.environ.get("ISKG_SMOKE_TEST") != "1",
    reason="set ISKG_SMOKE_TEST=1 (optionally under xvfb-run) to open a real window",
)
def test_smoke_real_window():
    """Open a real pywebview window and verify it starts/closes cleanly."""
    import threading

    import webview

    from iskg.app import _JSAPI_INSTANCE

    app = _build_demo_app()
    loop = app.test_loop()

    window = webview.create_window(
        "ISKG smoke",
        html=loop.html,
        js_api=_JSAPI_INSTANCE,
        width=640,
        height=480,
    )

    timer = threading.Timer(4.0, window.destroy)

    try:
        # func is called once the GUI event loop is up, so the webview
        # exists before we schedule the window close.
        webview.start(func=timer.start, private_mode=False)
    finally:
        timer.cancel()
        app._running = False
        app._window = None
    assert True


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
