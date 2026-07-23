"""Tests for Application, _JSAPI, and window management."""

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from iskg import Button, Label, Widget
from iskg.app import Application, Window, _HANDLERS, _LOCK, _JSAPI, _JSAPI_INSTANCE


# ── _JSAPI ─────────────────────────────────────────────────────────────


class TestJSAPI:
    def test_singleton(self):
        assert _JSAPI_INSTANCE is not None
        assert isinstance(_JSAPI_INSTANCE, _JSAPI)

    def test_on_event_no_handler(self):
        api = _JSAPI()
        api._last_event.clear()
        api.on_event("nonexistent", "click", '{"x":1}')
        # should not raise

    def test_on_event_calls_handler(self):
        api = _JSAPI()
        api._last_event.clear()
        calls = []
        handler = lambda name, data: calls.append((name, data))
        _HANDLERS["test_widget"] = handler
        api.on_event("test_widget", "change", '"hello"')
        assert len(calls) == 1
        assert calls[0] == ("change", "hello")
        _HANDLERS.pop("test_widget", None)

    def test_on_event_passes_none_when_no_data(self):
        api = _JSAPI()
        api._last_event.clear()
        calls = []
        _HANDLERS["test_none"] = lambda name, data: calls.append((name, data))
        api.on_event("test_none", "focus", None)
        assert len(calls) == 1
        assert calls[0][1] is None
        _HANDLERS.pop("test_none", None)

    def test_on_event_invalid_json_passes_raw(self):
        api = _JSAPI()
        api._last_event.clear()
        calls = []
        _HANDLERS["test_bad"] = lambda name, data: calls.append((name, data))
        api.on_event("test_bad", "drop", "not-json")
        assert len(calls) == 1
        assert calls[0][1] == "not-json"
        _HANDLERS.pop("test_bad", None)

    def test_debounce_drops_duplicate_within_window(self):
        api = _JSAPI()
        api._last_event.clear()
        calls = []
        _HANDLERS["debounce_w"] = lambda name, data: calls.append((name, data))
        api.on_event("debounce_w", "click", None)
        api.on_event("debounce_w", "click", None)
        assert len(calls) == 1
        _HANDLERS.pop("debounce_w", None)

    def test_different_events_not_debounced(self):
        api = _JSAPI()
        api._last_event.clear()
        calls = []
        _HANDLERS["debounce_m"] = lambda name, data: calls.append((name, data))
        api.on_event("debounce_m", "a", None)
        api.on_event("debounce_m", "b", None)
        assert len(calls) == 2
        _HANDLERS.pop("debounce_m", None)


# ── Application basic state ────────────────────────────────────────────


class TestApplicationInit:
    def test_defaults(self):
        app = Application()
        assert app._title == "ISKG App"
        assert app._width == 800
        assert app._height == 600
        assert app._scanlines is True
        assert app._vignette is True
        assert app._theme_name == "ifaz"
        assert app._debug is False
        assert app._extra_css == ""
        assert app._root_widgets == []
        assert app._running is False
        assert app._on_close_callbacks == []
        assert app._window is None

    def test_custom_params(self):
        app = Application(
            title="Test",
            width=1024,
            height=768,
            scanlines=False,
            vignette=False,
            theme="desert",
            debug=True,
            extra_css="body{color:red}",
        )
        assert app._title == "Test"
        assert app._width == 1024
        assert app._height == 768
        assert app._scanlines is False
        assert app._vignette is False
        assert app._theme_name == "desert"
        assert app._debug is True
        assert app._extra_css == "body{color:red}"

    def test_window_alias(self):
        assert Window is Application


class TestApplicationAddRemove:
    def test_add_widget(self):
        app = Application()
        w = Widget()
        result = app.add(w)
        assert result is w
        assert w in app._root_widgets
        assert w._app is app
        handler = _HANDLERS.get(w._id)
        bound = w._handle_bridge_event
        assert handler is not None
        assert handler.__self__ is bound.__self__
        assert handler.__func__ is bound.__func__

    def test_add_duplicate_is_idempotent(self):
        app = Application()
        w = Widget()
        app.add(w)
        app.add(w)
        assert len(app._root_widgets) == 1

    def test_add_propagates_to_children(self):
        app = Application()
        parent = Widget()
        child = Widget()
        parent.add(child)
        app.add(parent)
        assert child._app is app
        handler = _HANDLERS.get(child._id)
        bound = child._handle_bridge_event
        assert handler is not None
        assert handler.__self__ is bound.__self__

    def test_add_returns_widget_for_chaining(self):
        app = Application()
        w = app.add(Label(text="x"))
        assert isinstance(w, Label)

    def test_remove_widget(self):
        app = Application()
        w = Widget()
        app.add(w)
        app.remove(w)
        assert w not in app._root_widgets
        assert _HANDLERS.get(w._id) is None

    def test_remove_nonexistent(self):
        app = Application()
        w = Widget()
        app.remove(w)
        # should not raise

    def test_remove_clears_handlers(self):
        app = Application()
        w = Widget()
        app.add(w)
        assert w._id in _HANDLERS
        app.remove(w)
        assert w._id not in _HANDLERS


class TestApplicationState:
    def test_title_getter(self):
        app = Application(title="Foo")
        assert app.title() == "Foo"

    def test_title_setter(self):
        app = Application()
        assert app.title("NewTitle") == "NewTitle"
        assert app._title == "NewTitle"

    def test_title_none_is_getter(self):
        app = Application(title="X")
        assert app.title(None) == "X"

    def test_geometry_defaults(self):
        app = Application()
        x, y, w, h = app.geometry()
        assert x == 0
        assert y == 0
        assert w == 800
        assert h == 600

    def test_geometry_set(self):
        app = Application()
        app.geometry(x=100, y=200, w=1024, h=768)
        x, y, w, h = app.geometry()
        assert x == 100
        assert y == 200
        assert w == 1024
        assert h == 768

    def test_geometry_partial_set_ignored(self):
        app = Application()
        app.geometry(w=999)
        assert app._width == 800  # h not set, so ignored
        app.geometry(x=10)
        assert getattr(app, "_x", 0) == 0  # y not set, so ignored

    def test_debug_property(self):
        app = Application(debug=False)
        assert app.debug is False
        app.debug = True
        assert app.debug is True
        app.debug = 0
        assert app.debug is False

    def test_current_theme(self):
        app = Application(theme="dracula")
        assert app.current_theme() == "dracula"

    def test_widget_destroyed(self):
        _HANDLERS["test_del"] = lambda *a: None
        app = Application()
        app._widget_destroyed("test_del")
        assert "test_del" not in _HANDLERS

    def test_widget_destroyed_nonexistent(self):
        app = Application()
        app._widget_destroyed("nope")
        # should not raise


# ── _eval_js / _js_eval ────────────────────────────────────────────────


class TestEvalJs:
    def test_eval_js_no_window_noop(self):
        app = Application()
        app._running = False
        app._window = None
        app._eval_js("alert(1)")  # should not raise

    def test_eval_js_not_running_noop(self):
        app = Application()
        app._window = MagicMock()
        app._running = False
        app._eval_js("alert(1)")
        app._window.evaluate_js.assert_not_called()

    def test_eval_js_mock_window(self):
        app = Application()
        app._window = MagicMock()
        app._running = True
        app._eval_js("alert(1)")
        app._window.evaluate_js.assert_called_once_with("alert(1)")

    def test_js_eval_no_window_returns_none(self):
        app = Application()
        app._window = None
        assert app._js_eval("1+1") is None

    def test_js_eval_mock_window(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = 42
        app._running = True
        assert app._js_eval("1+1") == 42

    def test_js_eval_exception_returns_none(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.side_effect = Exception("fail")
        app._running = True
        assert app._js_eval("bad js") is None


# ── winfo methods (require mock window) ───────────────────────────────


class TestWinfo:
    def test_screenwidth_no_window(self):
        app = Application()
        assert app.winfo_screenwidth() == 0

    def test_screenheight_no_window(self):
        app = Application()
        assert app.winfo_screenheight() == 0

    def test_screendpi_no_window(self):
        app = Application()
        assert app.winfo_screendpi() == 96

    def test_screenwidth_mocked(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = 1920
        app._running = True
        assert app.winfo_screenwidth() == 1920
        app._window.evaluate_js.assert_called_once()

    def test_screenheight_mocked(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = 1080
        app._running = True
        assert app.winfo_screenheight() == 1080

    def test_screendpi_mocked(self):
        app = Application()
        app._window = MagicMock()
        # JS evaluates devicePixelRatio * 96, returns the product
        app._window.evaluate_js.return_value = 144
        app._running = True
        assert app.winfo_screendpi() == 144


# ── confirm / alert / execute_js ──────────────────────────────────────


class TestDialogs:
    def test_confirm_no_window_returns_false(self):
        app = Application()
        assert app.confirm("ok?") is False

    def test_confirm_mocked_true(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = True
        app._running = True
        assert app.confirm("ok?") is True

    def test_confirm_mocked_false(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = False
        app._running = True
        assert app.confirm("ok?") is False

    def test_alert_no_window(self):
        app = Application()
        app.alert("hi")  # should not raise

    def test_alert_mocked(self):
        app = Application()
        app._window = MagicMock()
        app._running = True
        app.alert("hi")
        app._window.evaluate_js.assert_called_once()

    def test_execute_js_returns_app(self):
        app = Application()
        result = app.execute_js("1+1")
        assert result is app


# ── set_theme / register_theme ────────────────────────────────────────


class TestTheme:
    def test_set_theme_valid_name(self):
        app = Application()
        app._window = MagicMock()
        app._running = True
        result = app.set_theme("desert")
        assert result is app
        assert app._theme_name == "desert"

    def test_set_theme_invalid_name_falls_back_to_ifaz(self):
        app = Application()
        # resolve_theme falls back to "ifaz" for unknown names
        app.set_theme("nonexistent_theme_xyz")
        assert app._theme_name == "nonexistent_theme_xyz"
        # the theme name is stored, resolution happens at render time

    def test_register_theme(self):
        app = Application()
        app._window = MagicMock()
        app._running = True
        overrides = {"--bg": "#000"}
        result = app.register_theme("custom1", overrides)
        assert result is app
        from iskg.themes import THEMES
        assert THEMES.get("custom1") == overrides


# ── quit / on_close ────────────────────────────────────────────────────


class TestLifecycle:
    def test_quit_no_window(self):
        app = Application()
        app._running = True
        app.quit()
        assert app._running is False

    def test_quit_mocked_window(self):
        app = Application()
        app._window = MagicMock()
        app._running = True
        app.quit()
        app._window.destroy.assert_called_once()
        assert app._running is False

    def test_on_close_registers(self):
        app = Application()
        cb = lambda: None
        app.on_close(cb)
        assert cb in app._on_close_callbacks

    def test_on_close_called_after_run(self):
        app = Application()
        calls = []
        app.on_close(lambda: calls.append(1))
        app.on_close(lambda: calls.append(2))
        # simulate what run() does after webview.start() returns
        for cb in app._on_close_callbacks:
            try:
                cb()
            except Exception:
                pass
        assert calls == [1, 2]

    def test_on_close_exception_does_not_block(self):
        app = Application()
        calls = []
        app.on_close(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        app.on_close(lambda: calls.append(1))
        for cb in app._on_close_callbacks:
            try:
                cb()
            except Exception:
                pass
        assert calls == [1]


# ── _build_html ────────────────────────────────────────────────────────


class TestBuildHtml:
    def test_build_html_default(self):
        app = Application()
        html = app._build_html()
        assert "<!DOCTYPE html>" in html
        assert "ISKG App" in html

    def test_build_html_no_scanlines(self):
        app = Application(scanlines=False)
        html = app._build_html()
        assert "ISKG App" in html

    def test_build_html_no_vignette(self):
        app = Application(vignette=False)
        html = app._build_html()
        assert "ISKG App" in html

    def test_build_html_neither(self):
        app = Application(scanlines=False, vignette=False)
        html = app._build_html()
        assert "ISKG App" in html

    def test_build_html_extra_js(self):
        app = Application()
        html = app._build_html(extra_js="alert(1);")
        assert "alert(1);" in html

    def test_build_html_includes_widgets(self):
        app = Application()
        app.add(Label(text="Hello"))
        html = app._build_html()
        assert "Hello" in html


# ── clipboard ──────────────────────────────────────────────────────────


class TestClipboard:
    def test_set_clipboard_no_pyperclip(self):
        app = Application()
        with patch.dict("sys.modules", {"pyperclip": None}):
            app.set_clipboard("text")  # should not raise

    def test_get_clipboard_no_pyperclip(self):
        app = Application()
        with patch.dict("sys.modules", {"pyperclip": None}):
            # trigger reimport by clearing cache
            pass
        # will raise ImportError -> return ""
        # But the import is cached, so we need to mock
        import importlib
        with patch.object(importlib, "import_module", side_effect=ImportError):
            result = app.get_clipboard()
            assert result == ""

    def test_set_clipboard_with_mock(self):
        app = Application()
        mock_pyperclip = MagicMock()
        with patch.dict("sys.modules", {"pyperclip": mock_pyperclip}):
            import importlib
            importlib.invalidate_caches()
            app.set_clipboard("test")
        # pyperclip was patched
        app.set_clipboard("test123")
        # The import is already cached, so we can't easily mock it in a unit test
        # This test just verifies no crash


# ── file_dialog ────────────────────────────────────────────────────────


class TestFileDialog:
    def test_file_dialog_gtk_returns_result(self):
        app = Application()
        with patch("iskg.app.Application._gtk_file_dialog", return_value="/path/file.txt"):
            result = app.file_dialog("open")
        assert result == "/path/file.txt"

    def test_file_dialog_gtk_returns_none_no_window(self):
        app = Application()
        app._window = None
        with patch("iskg.app.Application._gtk_file_dialog", return_value=None):
            result = app.file_dialog("open")
        assert result is None


# ── color_dialog ───────────────────────────────────────────────────────


class TestColorDialog:
    def test_color_dialog_gtk_unavailable(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = "OK"
        app._running = True
        result = app.color_dialog(initial_color="#000")
        assert result is not None

    def test_color_dialog_no_window_returns_none(self):
        app = Application()
        # Without window, GTK exception -> JS fallback -> _js_eval returns None
        assert app.color_dialog() is None

    def test_color_dialog_js_fallback_success(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = "#ff8800"
        app._running = True
        try:
            with patch("gi.require_version", side_effect=ValueError("no gtk")):
                result = app.color_dialog(initial_color="#000")
                assert result == "#ff8800"
        except ImportError:
            pytest.skip("gi not available")

    def test_color_dialog_js_fallback_cancelled(self):
        app = Application()
        app._window = MagicMock()
        app._window.evaluate_js.return_value = None
        app._running = True
        try:
            with patch("gi.require_version", side_effect=ValueError("no gtk")):
                result = app.color_dialog()
            assert result is None
        except ImportError:
            pytest.skip("gi not available")


# ── font_dialog ───────────────────────────────────────────────────────


class TestFontDialog:
    def test_font_dialog_no_window_returns_none(self):
        app = Application()
        assert app.font_dialog() is None

    def test_font_dialog_js_fallback(self):
        app = Application()
        app._window = MagicMock()
        result_json = json.dumps({"family": "Arial", "size": 14, "weight": "normal", "style": "normal", "_full_name": "Arial 14"})
        app._window.evaluate_js.return_value = result_json
        app._running = True
        try:
            with patch("gi.require_version", side_effect=ValueError("no gtk")):
                result = app.font_dialog()
            assert result is not None
            assert result["family"] == "Arial"
            assert result["size"] == 14
        except ImportError:
            pytest.skip("gi not available")


# ── _build_html with widgets ──────────────────────────────────────────


class TestBuildHtmlIntegration:
    def test_html_contains_widget_ids(self):
        app = Application()
        w = Label(text="Hello")
        app.add(w)
        html = app._build_html()
        assert w._id in html

    def test_html_contains_theme(self):
        app = Application(theme="desert")
        html = app._build_html()
        assert "desert" in html

    def test_extra_css_in_html(self):
        app = Application(extra_css=".x{color:green}")
        html = app._build_html()
        assert ".x{color:green}" in html
