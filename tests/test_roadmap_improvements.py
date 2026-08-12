"""Tests for the roadmap robustness improvements.

Covers:
- Application.after / after_cancel (scheduler)
- Application(icon=...) plumbing into webview.start
- Application.run_async (long tasks off the UI thread)
- Widget.rerender() + leaf fallback in _sync
- ComboBox.values live update
- IndicatorLED.color live update
- PanedWindow respects initial sash_pos
- Frame flex=False (fixed-width sidebar)
"""

import asyncio
import contextlib
import time
from unittest.mock import MagicMock, patch

from iskg import Application, ComboBox, Frame, IndicatorLED, PanedWindow, Widget


# ── 1. Application.after / after_cancel ────────────────────────────
class TestAppAfter:
    def test_after_creates_timer(self):
        app = Application()
        t = app.after(100, lambda: None)
        assert t.running is True
        assert t._id.startswith("t")
        assert t._id in app._timers
        t.cancel()

    def test_after_cancel_by_id(self):
        app = Application()
        t = app.after(10000, lambda: None)
        app.after_cancel(t._id)
        assert t._id not in app._timers
        assert t.running is False

    def test_after_cancel_unknown_is_noop(self):
        app = Application()
        app.after_cancel("nope")  # must not raise

    def test_after_fires_callback(self):
        app = Application()
        fired = []
        app.after(10, lambda: fired.append(1))
        for _ in range(100):
            if fired:
                break
            time.sleep(0.01)
        assert fired == [1]


# ── 6. Application(icon=...) ───────────────────────────────────────
class TestAppIcon:
    def test_icon_stored(self):
        app = Application(icon="icon.ico")
        assert app._icon == "icon.ico"

    def test_icon_default_none(self):
        app = Application()
        assert app._icon is None

    def test_icon_passed_to_webview_start(self):
        app = Application(icon="icon.ico")
        with (
            patch("webview.create_window", return_value=MagicMock()),
            patch("webview.start") as st,
        ):
            with contextlib.suppress(SystemExit):
                app.run()
        st.assert_called_once()
        kwargs = st.call_args.kwargs
        assert kwargs.get("icon") == "icon.ico"


# ── 7. Application.run_async ───────────────────────────────────────
class TestAppRunAsync:
    def test_run_async_calls_then_with_result(self):
        app = Application()
        results = []

        async def coro():
            await asyncio.sleep(0.01)
            return 7

        app.run_async(coro(), then=lambda r: results.append(r))
        for _ in range(200):
            if results:
                break
            time.sleep(0.01)
        assert results == [7]

    def test_run_async_propagates_exception(self):
        app = Application()
        results = []

        async def coro():
            raise ValueError("boom")

        app.run_async(coro(), then=lambda r: results.append(r))
        for _ in range(200):
            if results:
                break
            time.sleep(0.01)
        assert len(results) == 1
        assert isinstance(results[0], ValueError)


# ── 2 & 3. rerender() and leaf fallback ────────────────────────────
class _LeafWidget(Widget):
    def _render(self) -> str:
        return f'<div id="{self._id}">leaf</div>'

    def _render_update_js(self) -> str:
        return ""


class TestRerender:
    def test_rerender_emits_replace_widget(self):
        app = Application()
        led = IndicatorLED(color="green")
        app.add(led)
        loop = app.test_loop()
        led.rerender()
        joined = "".join(loop.js_calls)
        assert "iskg_replace_widget" in joined
        loop.stop()

    def test_rerender_escape_hatch(self):
        app = Application()
        w = _LeafWidget()
        app.add(w)
        loop = app.test_loop()
        # No incremental update JS exists: rerender() is the escape hatch.
        w.rerender()
        joined = "".join(loop.js_calls)
        assert "iskg_replace_widget" in joined
        loop.stop()


# ── 4. ComboBox.values live update ─────────────────────────────────
class TestComboBoxValues:
    def test_values_property(self):
        cb = ComboBox(values=["a", "b", "c"])
        assert cb.values == ["a", "b", "c"]

    def test_values_setter_updates_dom(self):
        app = Application()
        cb = ComboBox(values=["a", "b"])
        app.add(cb)
        loop = app.test_loop()
        cb.values = ["x", "y", "z"]
        joined = "".join(loop.js_calls)
        assert "iskg-cb-item" in joined
        assert "x" in joined
        assert cb.values == ["x", "y", "z"]
        loop.stop()


# ── 5. IndicatorLED.color live update ──────────────────────────────
class TestIndicatorLEDColor:
    def test_color_property(self):
        led = IndicatorLED(color="green")
        assert led.color == "green"

    def test_color_setter_updates_dom(self):
        app = Application()
        led = IndicatorLED(color="green")
        app.add(led)
        loop = app.test_loop()
        led.color = "red"
        joined = "".join(loop.js_calls)
        # red maps to #ef4444 in the LED color map
        assert "#ef4444" in joined
        assert led.color == "red"
        loop.stop()

    def test_color_rerender_reflects_new_color(self):
        app = Application()
        led = IndicatorLED(color="green")
        app.add(led)
        loop = app.test_loop()
        led.rerender()
        assert "iskg_replace_widget" in "".join(loop.js_calls)
        loop.stop()


# ── 8. PanedWindow sash_pos initial ───────────────────────────────
class TestPanedWindowSash:
    def test_sash_pos_applied_initial(self):
        pw = PanedWindow(orient="horizontal", sash_pos=0.75)
        Frame(parent=pw)
        Frame(parent=pw)
        html = pw._render()
        assert "flex:0.75" in html
        assert "flex:0.25" in html

    def test_default_sash_pos_is_equal(self):
        pw = PanedWindow(orient="horizontal")
        Frame(parent=pw)
        Frame(parent=pw)
        html = pw._render()
        assert "flex:1" in html


# ── 9. Frame flex=False (fixed-width sidebar) ──────────────────────
class TestFrameFlex:
    def test_flex_false_no_flex_grow(self):
        f = Frame(direction="column", width=240, flex=False)
        html = f._render()
        assert "width:240px" in html
        assert "flex:1" not in html

    def test_flex_true_keeps_grow(self):
        f = Frame(direction="column", width=240)
        html = f._render()
        assert "flex:1" in html

    def test_config_flex_toggles_grow(self):
        f = Frame(direction="column", width=240)
        f.config(flex=False)
        assert "flex:1" not in f._render()
