"""Application and window management, JS bridge, and file dialogs."""

from __future__ import annotations

import contextlib
import json
import os
import threading
from collections.abc import Callable
from typing import Any

from .base import Widget
from .template import build_html
from .theme import IFAZ_CSS

_HANDLERS: dict[str, Callable] = {}
_LOCK = threading.Lock()


class _JSAPI:
    _in_progress: set[tuple[str, str, str | None]] = set()

    def on_event(
        self,
        widget_id: str,
        event_name: str,
        event_data_json: str | None,
    ) -> None:
        key = (widget_id, event_name, event_data_json)
        with _LOCK:
            if key in self._in_progress:
                return
            self._in_progress.add(key)
        try:
            handler = _HANDLERS.get(widget_id)
            if handler:
                try:
                    data: Any = json.loads(event_data_json) if event_data_json else None
                except json.JSONDecodeError:
                    data = event_data_json
                handler(event_name, data)
        finally:
            with _LOCK:
                self._in_progress.discard(key)


_JSAPI_INSTANCE = _JSAPI()


class Application:
    """Main application entry point.

    Creates a native window via pywebview, renders all widgets as HTML/CSS/JS,
    and manages the JS bridge for event handling.

    Usage::

        app = Application("My App", 800, 600)
        label = Label(text="Hello")
        app.add(label)
        app.run()
    """

    def __init__(
        self,
        title: str = "ISKG App",
        width: int = 800,
        height: int = 600,
        scanlines: bool = True,
        vignette: bool = True,
        theme: str = "ifaz",
    ) -> None:
        self._title = title
        self._width = width
        self._height = height
        self._scanlines = scanlines
        self._vignette = vignette
        self._theme_name = theme

        self._root_widgets: list[Widget] = []
        self._running = False
        self._on_close_callbacks: list[Callable] = []
        self._window: Any = None

    def add(self, widget: Widget) -> Widget:
        """Register a root-level widget with the application.

        Widgets must be added to the app before ``run()`` is called.
        """
        if widget not in self._root_widgets:
            self._root_widgets.append(widget)
            widget._app = self
            for _, w in widget._collect_widgets():
                w._app = self
                if isinstance(w, Widget):
                    _HANDLERS[w._id] = w._handle_bridge_event
        return widget

    def remove(self, widget: Widget) -> None:
        """Unregister a root-level widget."""
        if widget in self._root_widgets:
            self._root_widgets.remove(widget)

    def on_close(self, callback: Callable) -> None:
        """Register a callback to call when the window is closed."""
        self._on_close_callbacks.append(callback)

    def title(self, text: str | None = None) -> str:
        """Get or set the window title."""
        if text is not None:
            self._title = text
        return self._title

    def geometry(
        self,
        x: int | None = None,
        y: int | None = None,
        w: int | None = None,
        h: int | None = None,
    ) -> tuple[int, int, int, int]:
        """Get or set the window position and size."""
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

    _saved_stderr: int | None = None

    def run(self, extra_js: str = "") -> None:
        """Open the window and start the application main loop.

        Blocks until the window is closed. Redirects GTK stderr warnings
        to /dev/null during execution.

        Args:
            extra_js: additional JavaScript to execute on startup (e.g. tooltip init code).
        """
        from ._vendor import try_import

        try_import("webview", "pywebview>=5.0")
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

        self._saved_stderr = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        os.close(devnull)

        try:
            webview.start(private_mode=False, debug=False)
        except Exception as exc:
            if self._saved_stderr is not None:
                os.dup2(self._saved_stderr, 2)
                os.close(self._saved_stderr)
                self._saved_stderr = None
            print(f"ISKG: webview.start() failed: {exc}", file=__import__("sys").stderr)
            __import__("sys").exit(1)

        self._running = False
        for cb in self._on_close_callbacks:
            cb()
        if self._saved_stderr is not None:
            os.dup2(self._saved_stderr, 2)
            os.close(self._saved_stderr)
            self._saved_stderr = None

    def _build_html(self, extra_js: str = "") -> str:
        html = build_html(
            self._root_widgets, IFAZ_CSS, extra_js=extra_js, theme_name=self._theme_name
        )
        if not self._scanlines:
            html = html.replace('<div id="iskg-scanlines"></div>', "")
        if not self._vignette:
            html = html.replace('<div id="iskg-vignette"></div>', "")
        return html

    def _eval_js(self, js: str) -> None:
        if self._window and self._running:
            with contextlib.suppress(Exception):
                self._window.evaluate_js(js)

    def _widget_destroyed(self, widget_id: str) -> None:
        _HANDLERS.pop(widget_id, None)

    def winfo_screenwidth(self) -> int:
        """Return the screen width in pixels (requires a running window)."""
        val = self._eval_js("window.screen.width;") if self._window else None
        return int(val) if val is not None else 0

    def winfo_screenheight(self) -> int:
        """Return the screen height in pixels (requires a running window)."""
        val = self._eval_js("window.screen.height;") if self._window else None
        return int(val) if val is not None else 0

    def winfo_screendpi(self) -> int:
        """Return the screen DPI (approximate, requires a running window)."""
        val = self._eval_js("window.devicePixelRatio*96;") if self._window else None
        return int(val) if val is not None else 96

    def set_theme(self, name: str) -> Application:
        """Switch the UI theme at runtime.

        Args:
            name: one of ``"ifaz"``, ``"cold"``, ``"warm"``, ``"night"``, or
                  a custom name previously registered via :meth:`register_theme`.
        """
        from .themes import resolve_theme, theme_js

        resolve_theme(name)
        self._theme_name = name
        self._eval_js(theme_js(name))
        return self

    def current_theme(self) -> str:
        """Return the name of the currently active theme."""
        return self._theme_name

    def register_theme(self, name: str, overrides: dict[str, str]) -> Application:
        """Register a new theme for runtime use.

        Args:
            name: unique theme name (e.g. ``"mytheme"``).
            overrides: dict of CSS custom properties,
                       e.g. ``{"--bg-primary": "#000", "--text": "#fff"}``.
        """
        from .themes import THEMES

        THEMES[name] = dict(overrides)
        import json

        self._eval_js(f"iskg_register_themes({json.dumps({name: overrides})});")
        return self

    def execute_js(self, js_code: str) -> Application:
        """Execute arbitrary JavaScript in the webview window."""
        self._eval_js(js_code)
        return self

    def quit(self) -> None:
        """Close the application window and exit the main loop."""
        if self._window:
            self._window.destroy()
        self._running = False

    def set_clipboard(self, text: str) -> None:
        """Copy text to the system clipboard (requires pyperclip)."""
        try:
            import pyperclip

            pyperclip.copy(text)
        except ImportError:
            pass

    def get_clipboard(self) -> str:
        """Read text from the system clipboard (requires pyperclip)."""
        try:
            import pyperclip

            return pyperclip.paste()
        except ImportError:
            return ""

    def file_dialog(
        self,
        dialog_type: str = "open",
        directory: str = "",
        file_types: list[str] | None = None,
        allow_multiple: bool = False,
    ) -> Any | None:
        """Open a native OS file dialog.

        Uses GTK directly (same toolkit as pywebview underneath) with
        explicit dialog sizing. Falls back to pywebview's built-in dialog.

        Args:
            dialog_type: ``"open"``, ``"save"``, or ``"folder"``.
            directory: starting directory path.
            file_types: list of extensions like ``["*.txt", "*.py"]``.
            allow_multiple: allow multiple file selection (open only).
        """
        result = self._gtk_file_dialog(dialog_type, directory, file_types, allow_multiple)
        if result is not None:
            return result
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

    def _gtk_file_dialog(
        self,
        dialog_type: str,
        directory: str,
        file_types: list[str] | None,
        allow_multiple: bool,
    ) -> Any | None:
        try:
            import gi  # type: ignore[import-untyped]

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk  # type: ignore[import-untyped]
        except (ImportError, ValueError):
            return None

        action_map = {
            "open": Gtk.FileChooserAction.OPEN,
            "save": Gtk.FileChooserAction.SAVE,
            "folder": Gtk.FileChooserAction.SELECT_FOLDER,
        }
        action = action_map.get(dialog_type, Gtk.FileChooserAction.OPEN)
        accept = {
            "open": "_Open",
            "save": "_Save",
            "folder": "_Select",
        }.get(dialog_type, "_Open")

        dialog = Gtk.FileChooserDialog(
            title="",
            parent=None,
            action=action,
            buttons=(
                "_Cancel",
                Gtk.ResponseType.CANCEL,
                accept,
                Gtk.ResponseType.ACCEPT,
            ),
        )
        dialog.set_default_size(700, 500)
        dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        if directory:
            dialog.set_current_folder(directory)
        if file_types:
            for ft in file_types:
                filt = Gtk.FileFilter()
                filt.set_name(ft)
                filt.add_pattern(ft)
                dialog.add_filter(filt)
        if allow_multiple:
            dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            if dialog_type == "folder":
                result = dialog.get_filename()
            elif allow_multiple:
                result = list(dialog.get_filenames())
            else:
                result = dialog.get_filename()
        else:
            result = None

        dialog.destroy()
        return result

    def alert(self, message: str) -> None:
        """Show a browser-style alert dialog."""
        self._eval_js(f"alert({json.dumps(message)})")

    def confirm(self, message: str) -> None:
        """Show a browser-style confirm dialog."""
        self._eval_js(f"confirm({json.dumps(message)})")

    def _js_eval(self, js: str) -> Any | None:
        """Evaluate JS and return the result, or None on error."""
        if self._window and self._running:
            try:
                return self._window.evaluate_js(js)
            except Exception:
                pass
        return None

    def color_dialog(
        self,
        title: str = "Choose Color",
        initial_color: str = "#000000",
    ) -> str | None:
        """Open a color picker dialog.

        Uses GTK on Linux, falls back to a browser ``<input type="color">``
        on Windows/macOS.

        Returns a hex string (e.g. ``"#ff8800"``) or ``None``.
        """
        try:
            import gi  # type: ignore[import-untyped]

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gdk, Gtk  # type: ignore[import-untyped]
        except (ImportError, ValueError):
            js = (
                f"(function(){{"
                f"var i=document.createElement('input');i.type='color';"
                f"i.value={json.dumps(initial_color)};"
                f"i.style.position='fixed';i.style.left='-9999px';"
                f"document.body.appendChild(i);"
                f"var p=new Promise(function(r){{"
                f"i.addEventListener('change',function(){{r(i.value);document.body.removeChild(i);}});"
                f"i.addEventListener('blur',function(){{setTimeout(function(){{"
                f"if(document.body.contains(i)){{r(null);document.body.removeChild(i);}}"
                f"}},300);}});"
                f"}});i.click();return p;"
                f"}})()"
            )
            result = self._js_eval(js)
            return result if result else None

        rgba = Gdk.RGBA()
        rgba.parse(initial_color)
        dialog = Gtk.ColorChooserDialog(title=title, parent=None)
        dialog.set_rgba(rgba)
        dialog.set_use_alpha(False)

        result: str | None = None
        if dialog.run() == Gtk.ResponseType.OK:
            c = dialog.get_rgba()
            result = f"#{int(c.red * 255):02x}{int(c.green * 255):02x}{int(c.blue * 255):02x}"
        dialog.destroy()
        return result

    def font_dialog(
        self,
        title: str = "Choose Font",
        initial_font: str = "",
    ) -> dict[str, Any] | None:
        """Open a font picker dialog.

        Uses GTK on Linux, falls back to a browser prompt on Windows/macOS.

        Returns a dict with keys ``family``, ``size``, ``weight``, ``style``,
        or ``None``.
        """
        try:
            import gi  # type: ignore[import-untyped]

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk  # type: ignore[import-untyped]
        except (ImportError, ValueError):
            js = (
                f"(function(){{"
                f"var r=prompt({json.dumps(title)},{json.dumps(initial_font)});"
                f"if(!r)return null;"
                f"var parts=r.trim().split(/(\\d+)/);"
                f"var family=parts[0].trim()||'Sans';"
                f"var size=parseInt(parts[1],10)||12;"
                f"return JSON.stringify({{family:family,size:size,weight:'normal',style:'normal',_full_name:r}});"
                f"}})()"
            )
            raw = self._js_eval(js)
            if raw:
                return json.loads(raw)
            return None

        dialog = Gtk.FontChooserDialog(title=title, parent=None)
        if initial_font:
            dialog.set_font_name(initial_font)

        result: dict[str, Any] | None = None
        if dialog.run() == Gtk.ResponseType.OK:
            font_name = dialog.get_font_name()
            parts = font_name.split()
            family = parts[0] if parts else "Sans"
            size = 12
            weight = "normal"
            style = "normal"
            if len(parts) > 1:
                with contextlib.suppress(ValueError):
                    size = int(parts[-1])
            result = {
                "family": family,
                "size": size,
                "weight": weight,
                "style": style,
                "_full_name": font_name,
            }
        dialog.destroy()
        return result


Window = Application
