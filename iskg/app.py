import json
import os
import sys
import threading

from .theme import IFAZ_CSS
from .template import build_html
from .base import Widget

_HANDLERS = {}
_LOCK = threading.Lock()


class _JSAPI:
    _in_progress = set()

    def on_event(self, widget_id, event_name, event_data_json):
        key = (widget_id, event_name, event_data_json)
        with _LOCK:
            if key in self._in_progress:
                return
            self._in_progress.add(key)
        try:
            handler = _HANDLERS.get(widget_id)
            if handler:
                try:
                    data = json.loads(event_data_json) if event_data_json else None
                except json.JSONDecodeError:
                    data = event_data_json
                handler(event_name, data)
        finally:
            with _LOCK:
                self._in_progress.discard(key)


_JSAPI_INSTANCE = _JSAPI()


class Application:
    def __init__(
        self, title="ISKG App", width=800, height=600, scanlines=True, vignette=True
    ):
        self._title = title
        self._width = width
        self._height = height
        self._scanlines = scanlines
        self._vignette = vignette

        self._root_widgets = []
        self._running = False
        self._on_close_callbacks = []
        self._window = None

    def add(self, widget):
        if widget not in self._root_widgets:
            self._root_widgets.append(widget)
            widget._app = self
            for _, w in widget._collect_widgets():
                w._app = self
                if isinstance(w, Widget):
                    _HANDLERS[w._id] = w._handle_bridge_event
        return widget

    def remove(self, widget):
        if widget in self._root_widgets:
            self._root_widgets.remove(widget)

    def on_close(self, callback):
        self._on_close_callbacks.append(callback)

    def title(self, text=None):
        if text is not None:
            self._title = text
        return self._title

    def geometry(self, x=None, y=None, w=None, h=None):
        if w is not None and h is not None:
            self._width = w
            self._height = h
        if x is not None and y is not None:
            self._x = x
            self._y = y
        return (
            getattr(self, "_x", 0),
            getattr(self, "_y", 0),
            self._width,
            self._height,
        )

    _saved_stderr = None

    def run(self, extra_js=""):
        self._saved_stderr = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        os.close(devnull)

        import webview

        self._running = True
        html = self._build_html(extra_js)

        self._window = webview.create_window(
            self._title,
            html=html,
            width=self._width,
            height=self._height,
            js_api=_JSAPI_INSTANCE,
        )

        webview.start(private_mode=False, debug=False)
        self._running = False
        for cb in self._on_close_callbacks:
            cb()
        if self._saved_stderr is not None:
            os.dup2(self._saved_stderr, 2)
            os.close(self._saved_stderr)
            self._saved_stderr = None

    def _build_html(self, extra_js=""):
        html = build_html(self._root_widgets, IFAZ_CSS, extra_js=extra_js)
        if not self._scanlines:
            html = html.replace('<div id="iskg-scanlines"></div>', "")
        if not self._vignette:
            html = html.replace('<div id="iskg-vignette"></div>', "")
        return html

    def _eval_js(self, js):
        if self._window and self._running:
            try:
                self._window.evaluate_js(js)
            except Exception:
                pass

    def _widget_destroyed(self, widget_id):
        _HANDLERS.pop(widget_id, None)

    def execute_js(self, js_code):
        self._eval_js(js_code)
        return self

    def quit(self):
        if self._window:
            self._window.destroy()
        self._running = False

    def set_clipboard(self, text):
        try:
            import pyperclip

            pyperclip.copy(text)
        except ImportError:
            pass

    def get_clipboard(self):
        try:
            import pyperclip

            return pyperclip.paste()
        except ImportError:
            return ""

    def file_dialog(
        self, dialog_type="open", directory="", file_types=None, allow_multiple=False
    ):
        try:
            import webview as _wv
        except ImportError:
            return None
        if not self._window or not self._running:
            return None
        dt = _wv.FileDialog.OPEN
        if dialog_type == "save":
            dt = _wv.FileDialog.SAVE
        elif dialog_type == "folder":
            dt = _wv.FileDialog.FOLDER
        return self._window.create_file_dialog(
            dt,
            directory,
            allow_multiple,
            file_types=file_types or (),
        )

    def alert(self, message):
        self._eval_js(f"alert({json.dumps(message)})")

    def confirm(self, message):
        self._eval_js(f"confirm({json.dumps(message)})")


Window = Application
