"""Application and window management, JS bridge, and file dialogs."""

from __future__ import annotations

import contextlib
import json
import os
import threading
import time
from collections.abc import Callable
from typing import Any

# webkit2gtk may render the window entirely white (uncomposited content)
# when its accelerated compositing path misbehaves on some drivers. Force
# the software/compositing-disabled path so the UI is always visible.
# setdefault() keeps an explicit user override working.
if os.name == "posix":
    os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")

from .base import Widget
from .template import build_html
from .theme import IFAZ_CSS

_HANDLERS: dict[str, Callable] = {}
_LOCK = threading.Lock()

_GTK_UNAVAILABLE = object()


class _JSAPI:
    _DEBOUNCE_MS = 50
    _last_event: dict[tuple[str, str], tuple[float, str | None]] = {}

    def on_event(
        self,
        widget_id: str,
        event_name: str,
        event_data_json: str | None,
    ) -> None:
        key = (widget_id, event_name)
        now = time.time()
        with _LOCK:
            last = self._last_event.get(key)
            if (
                last is not None
                and (now - last[0]) * 1000 < self._DEBOUNCE_MS
                and last[1] == event_data_json
            ):
                return
            self._last_event[key] = (now, event_data_json)
        handler = _HANDLERS.get(widget_id)
        if handler:
            try:
                data: Any = json.loads(event_data_json) if event_data_json else None
            except json.JSONDecodeError:
                data = event_data_json
            handler(event_name, data)


_JSAPI_INSTANCE = _JSAPI()


class SyncBatch:
    """Context manager returned by :meth:`Application.sync_batch`.

    Accumulates ``_sync`` JS emitted inside the ``with`` block and flushes it
    as a single ``evaluate_js`` call when the block exits.
    """

    def __init__(self, app: Application) -> None:
        self._app = app
        self._flushed = False

    def __enter__(self) -> SyncBatch:
        self._app._begin_sync_batch()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._app._end_sync_batch()


class Application:
    """Main application entry point.

    Creates a native window via pywebview, renders all widgets as HTML/CSS/JS,
    and manages the JS bridge for event handling.

    Usage::

        app = Application("My App", 800, 600)
        label = Label(text="Hello")
        app.add(label)
        app.run()

    Pass ``debug=True`` to log JavaScript errors to stderr::

        app = Application(debug=True)
    """

    def __init__(
        self,
        title: str = "ISKG App",
        width: int = 800,
        height: int = 600,
        scanlines: bool = True,
        vignette: bool = True,
        theme: str = "ifaz",
        debug: bool = False,
        extra_css: str = "",
        stderr_log: str | None = None,
        font_ids: list[str] | None = None,
        icon: str | None = None,
    ) -> None:
        self._title = title
        self._width = width
        self._height = height
        self._scanlines = scanlines
        self._vignette = vignette
        self._theme_name = theme
        self._debug = debug
        self._extra_css = extra_css
        self._stderr_log = stderr_log
        self._font_ids = font_ids
        self._icon = icon

        self._root_widgets: list[Widget] = []
        self._running = False
        self._close_fired = False
        self._on_close_callbacks: list[Callable] = []
        self._event_handlers: dict[str, list[Callable]] = {}
        self._window: Any = None
        self._deferred_sync: list[str] = []
        self._sync_lock = threading.Lock()
        self._sync_batch_depth = 0
        self._global_key_bindings: list[dict[str, Any]] = []
        self._timers: dict[str, Any] = {}
        _HANDLERS["__iskg_global__"] = self._handle_global_event

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
            self.emit("widget-created", widget._id)
        return widget

    def remove(self, widget: Widget) -> None:
        """Unregister a root-level widget."""
        if widget in self._root_widgets:
            self._root_widgets.remove(widget)
            _HANDLERS.pop(widget._id, None)

    def on_close(self, callback: Callable) -> None:
        """Register a callback to call when the window is closed."""
        self._on_close_callbacks.append(callback)

    def on(self, event: str, callback: Callable | None = None) -> Callable:
        """Subscribe to a global application event.

        Built-in events:

        * ``"theme-changed"`` — fired with the new theme name after
          :meth:`set_theme`.
        * ``"closing"`` — fired with ``None`` when the window is about to
          close (in addition to :meth:`on_close`).
        * ``"widget-created"`` — fired with the widget id when a widget is
          added to the tree (root widgets registered via :meth:`add`).

        Arbitrary user events are also supported.

        Args:
            event: event name.
            callback: callable invoked as ``callback(*args)`` where args are
                whatever was passed to :meth:`emit`. May be omitted to use
                as a decorator::

                    @app.on("my-event")
                    def handler(value):
                        ...

        Returns:
            The registered callback (handy as a decorator).
        """
        if callback is None:

            def deco(fn: Callable) -> Callable:
                self._event_handlers.setdefault(event, []).append(fn)
                return fn

            return deco
        self._event_handlers.setdefault(event, []).append(callback)
        return callback

    def off(self, event: str, callback: Callable | None = None) -> Application:
        """Unsubscribe one (or all) handler(s) from an event.

        Args:
            event: event name.
            callback: handler to remove; when ``None`` all handlers for the
                event are removed.
        """
        if callback is None:
            self._event_handlers.pop(event, None)
        else:
            handlers = self._event_handlers.get(event, [])
            self._event_handlers[event] = [h for h in handlers if h is not callback]
        return self

    def emit(self, event: str, *args: Any) -> Application:
        """Fire a global application event synchronously.

        Args:
            event: event name.
            *args: payload forwarded to every subscribed handler.
        """
        for handler in list(self._event_handlers.get(event, [])):
            with contextlib.suppress(Exception):
                handler(*args)
        return self

    def bind(self, event: str, callback: Callable | None = None) -> Callable:
        """Bind a window-wide (global) keyboard shortcut.

        Unlike ``Widget.bind``, these shortcuts fire regardless of which
        widget has focus. Uses the same tkinter-style syntax:
        ``"<Control-s>"``, ``"<Alt-F4>"``, ``"<KeyRelease-a>"``, etc.

        The callback receives a dict with ``key``, ``code``, ``ctrl``,
        ``alt``, ``shift``. May be used as a decorator::

            @app.bind("<Control-s>")
            def on_save(data):
                ...
        """
        if callback is None:

            def deco(fn: Callable) -> Callable:
                self._register_global_key(event, fn)
                return fn

            return deco
        self._register_global_key(event, callback)
        return callback

    def _register_global_key(self, event: str, callback: Callable) -> None:
        parsed = Widget._parse_key_event(event)
        if parsed is None:
            raise ValueError(
                f"{event!r} is not a key event; global bindings accept key events only"
            )
        entry = dict(parsed)
        entry["cb"] = callback
        self._global_key_bindings.append(entry)
        if self._running and self._window:
            self._eval_js(self._render_one_global_key_js(parsed))

    def _render_one_global_key_js(self, parsed: dict[str, Any]) -> str:
        mods = {}
        if parsed["ctrl"]:
            mods["ctrl"] = True
        if parsed["alt"]:
            mods["alt"] = True
        if parsed["shift"]:
            mods["shift"] = True
        mods_json = json.dumps(mods) if mods else "null"
        key_json = json.dumps(parsed["key"]) if parsed["key"] else "null"
        evt = json.dumps(parsed["event_type"])
        return f"iskg_bind_global_key({evt},{key_json},{mods_json});"

    def _render_global_keys_js(self) -> str:
        return "".join(self._render_one_global_key_js(e) for e in self._global_key_bindings)

    def _handle_global_event(self, event_name: str, event_data: Any) -> str | None:
        for entry in list(self._global_key_bindings):
            if entry["event_type"] not in ("keypress" if event_name == "key" else "keyrelease",):
                continue
            data = event_data or {}
            if entry.get("ctrl") and not data.get("ctrl"):
                continue
            if entry.get("alt") and not data.get("alt"):
                continue
            if entry.get("shift") and not data.get("shift"):
                continue
            if entry.get("key") and entry["key"] not in (
                data.get("key"),
                data.get("code"),
            ):
                continue
            entry["cb"](data)
            return "break"
        return None

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

    def _check_backend(self) -> None:
        """Ensure the native webview backend is available before opening a window.

        On Linux, pywebview needs GTK3 + WebKit2GTK. If they are missing the
        later ``webview.start()`` fails with a cryptic traceback; this surfaces
        a clear, distro-specific install hint instead.
        """
        import sys

        if sys.platform != "linux":
            return
        try:
            self._import_gi_backend()
        except Exception as exc:  # gi missing or typelib not installed
            raise RuntimeError(self._backend_install_hint()) from exc

    @staticmethod
    def _import_gi_backend() -> None:
        import gi

        # Pin GTK3 explicitly. An unversioned ``from gi.repository import Gtk``
        # resolves to the highest installed GTK (4.0 when both are present),
        # which then conflicts with WebKit2GTK (GTK3-only) and raises
        # "Requiring namespace 'Gtk' version '3.0', but '4.0' is already loaded".
        gi.require_version("Gtk", "3.0")
        try:
            gi.require_version("WebKit2", "4.1")
        except ValueError:
            gi.require_version("WebKit2", "4.0")
        from gi.repository import Gtk, WebKit2  # noqa: F401

    @staticmethod
    def _backend_install_hint() -> str:
        return (
            "ISKG no pudo cargar el backend de escritorio (GTK3 + WebKit2GTK).\n"
            "Instálalo según tu distribución y vuelve a ejecutar la app:\n"
            "  Arch Linux   : sudo pacman -S gtk3 webkit2gtk-4.1 python-gobject\n"
            "  Debian/Ubuntu: sudo apt install python3-gi gir1.2-webkit2-4.1\n"
            "  Fedora       : sudo dnf install python3-gobject gtk3 webkit2gtk3\n"
        )

    def run(self, extra_js: str = "") -> None:
        """Open the window and start the application main loop.

        Blocks until the window is closed. Redirects GTK stderr warnings
        to ``stderr_log`` (or ``/dev/null`` when no log path is given) during
        execution. The original descriptor is always restored via ``finally``,
        so application prints and tracebacks are never silently swallowed.

        Args:
            extra_js: additional JavaScript to execute on startup (e.g. tooltip init code).
        """
        from ._vendor import try_import

        try_import("webview", "pywebview>=5.0")

        # Re-assert before the GTK/WebKit loop starts; the GTK window is opaque,
        # so if the web-layer composition fails the user would see white. Forcing
        # the disabled-compositing path here guards against late/lazy imports.
        if os.name == "posix":
            os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")

        import webview

        self._check_backend()

        self._running = True
        html = self._build_html(extra_js)

        self._window = webview.create_window(
            self._title,
            html=html,
            width=self._width,
            height=self._height,
            js_api=_JSAPI_INSTANCE,
        )

        saved = os.dup(2)
        self._saved_stderr = saved
        log_path = self._stderr_log or os.devnull
        log_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.dup2(log_fd, 2)
        finally:
            os.close(log_fd)

        try:
            webview.start(private_mode=False, debug=False, icon=self._icon)
        except Exception as exc:
            os.dup2(saved, 2)
            self._saved_stderr = None
            os.close(saved)
            print(f"ISKG: webview.start() failed: {exc}", file=__import__("sys").stderr)
            __import__("sys").exit(1)
        finally:
            if self._saved_stderr is not None:
                os.dup2(self._saved_stderr, 2)
                os.close(self._saved_stderr)
                self._saved_stderr = None

        self._running = False
        self._fire_close_callbacks()
        if self._saved_stderr is not None:
            os.dup2(self._saved_stderr, 2)
            os.close(self._saved_stderr)
            self._saved_stderr = None

    # ── Timers & async ──────────────────────────────────────────────

    def after(self, ms: int, callback: Callable) -> Any:
        """Schedule ``callback`` to run after ``ms`` milliseconds.

        Unlike :class:`threading.Timer`, the callback runs on a daemon timer
        thread and may safely mutate widgets (updates are marshalled through
        the app's sync queue). Returns a handle with ``.cancel()`` / ``.running``.

        Args:
            ms: delay in milliseconds.
            callback: zero-argument callable.

        Returns:
            A timer handle (``Widget._Timer``-compatible) with ``.cancel()``.
        """
        import threading

        timer_id = f"t{id(callback)}_{id(self)}"
        t = threading.Timer(ms / 1000, callback)
        t.daemon = True
        timer = Widget._Timer(timer_id, t)
        self._timers[timer_id] = timer
        t.start()
        return timer

    def after_cancel(self, timer_id: str) -> None:
        """Cancel a timer previously created with :meth:`after`."""
        timers = self._timers
        t = timers.pop(timer_id, None)
        if t:
            t.cancel()

    def run_async(self, coro: Any, then: Callable | None = None) -> Any:
        """Run a coroutine in a background thread with its own event loop.

        Useful for long-running tasks (e.g. network/HTTP calls) without
        blocking the UI. When the coroutine finishes, ``then(result)`` is
        scheduled on the app via :meth:`after` (``result`` is the return value,
        or the raised exception if it failed).

        Args:
            coro: a coroutine (e.g. ``some_async_fn()``).
            then: optional callback ``then(result)`` invoked on completion.

        Returns:
            The background :class:`threading.Thread` (daemon).
        """
        import asyncio
        import threading

        def _worker() -> None:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(coro)
            except Exception as exc:  # noqa: BLE001
                result = exc
            if then is not None:
                self.after(0, lambda: then(result))

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        return th

    def _build_html(self, extra_js: str = "") -> str:
        extra_js = self._render_global_keys_js() + extra_js
        html = build_html(
            self._root_widgets,
            IFAZ_CSS,
            extra_js=extra_js,
            extra_css=self._extra_css,
            theme_name=self._theme_name,
            font_ids=self._font_ids,
        )
        if not self._scanlines:
            html = html.replace('<div id="iskg-scanlines"></div>', "")
        if not self._vignette:
            html = html.replace('<div id="iskg-vignette"></div>', "")
        return html

    def _eval_js(self, js: str) -> None:
        if self._window and self._running:
            try:
                self._window.evaluate_js(js)
            except Exception as exc:
                if self._debug:
                    import sys

                    print(f"[ISKG:js] {exc}", file=sys.stderr)

    # ── Sync batching (opt-in) ────────────────────────────────────────
    # Multiple rapid `_sync()` calls (e.g. a progress pipeline that ticks at
    # high cadence) each produce an evaluate_js round-trip. Callers can wrap a
    # burst with `with app.sync_batch():` to coalesce all pending JS into a
    # single evaluate_js() at the end of the block. Default behaviour (no
    # batch) stays immediate, so existing widget tests remain synchronous.

    def sync_batch(self) -> SyncBatch:
        """Context manager that batches `_sync` JS until the block exits."""
        return SyncBatch(self)

    def _defer_sync(self, js: str) -> None:
        with self._sync_lock:
            self._deferred_sync.append(js)
            batch = self._sync_batch_depth > 0
        if not batch:
            self._flush_sync()

    def _flush_sync(self) -> None:
        with self._sync_lock:
            if not self._deferred_sync:
                return
            js = ";".join(self._deferred_sync)
            self._deferred_sync.clear()
        if js:
            self._eval_js(js)

    def _begin_sync_batch(self) -> None:
        with self._sync_lock:
            self._sync_batch_depth += 1

    def _end_sync_batch(self) -> None:
        with self._sync_lock:
            self._sync_batch_depth = max(0, self._sync_batch_depth - 1)
            flush = self._sync_batch_depth == 0
        if flush:
            self._flush_sync()

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = bool(value)

    def _widget_destroyed(self, widget_id: str) -> None:
        _HANDLERS.pop(widget_id, None)

    def winfo_screenwidth(self) -> int:
        """Return the screen width in pixels (requires a running window)."""
        val = self._js_eval("window.screen.width;")
        return int(val) if val is not None else 0

    def winfo_screenheight(self) -> int:
        """Return the screen height in pixels (requires a running window)."""
        val = self._js_eval("window.screen.height;")
        return int(val) if val is not None else 0

    def winfo_screendpi(self) -> int:
        """Return the screen DPI (approximate, requires a running window)."""
        val = self._js_eval("window.devicePixelRatio*96;")
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
        self.emit("theme-changed", name)
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

    def _fire_close_callbacks(self) -> None:
        """Run the registered ``on_close`` callbacks exactly once."""
        if self._close_fired:
            return
        self._close_fired = True
        self.emit("closing")
        with contextlib.suppress(Exception):
            for cb in self._on_close_callbacks:
                cb()

    def quit(self) -> None:
        """Close the application window, fire ``on_close`` and exit the main loop.

        The ``on_close`` callbacks run exactly once (idempotent with the
        invocation done in :meth:`run` when the loop ends naturally).
        """
        if self._window:
            with contextlib.suppress(Exception):
                self._window.destroy()
        self._running = False
        self._fire_close_callbacks()

    def set_clipboard(self, text: str) -> None:
        """Copy text to the system clipboard (requires pyperclip)."""
        try:
            import importlib

            pyperclip = importlib.import_module("pyperclip")
            pyperclip.copy(text)
        except ImportError:
            pass

    def get_clipboard(self) -> str:
        """Read text from the system clipboard (requires pyperclip)."""
        try:
            import importlib

            pyperclip = importlib.import_module("pyperclip")
            return pyperclip.paste()
        except ImportError:
            return ""

    def file_dialog(
        self,
        dialog_type: str = "open",
        directory: str = "",
        file_types: list[str] | None = None,
        allow_multiple: bool = False,
        title: str = "",
    ) -> Any | None:
        """Open a native OS file dialog.

        Uses GTK directly (same toolkit as pywebview underneath) with
        explicit dialog sizing.

        ``_gtk_file_dialog`` returns ``_GTK_UNAVAILABLE`` when GTK is not
        importable, so a user Cancel (``None``) is not mistaken for a missing
        toolkit and does not trigger a second dialog via pywebview.
        """
        gtk_result = self._gtk_file_dialog(
            dialog_type, directory, file_types, allow_multiple, title
        )
        if gtk_result is not _GTK_UNAVAILABLE:
            return gtk_result
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

    def _run_gtk_modal(self, fn: Callable[[], None]) -> None:
        """Run a GTK dialog-owning callback on the main thread.

        pywebview dispatches JS bridge calls (which trigger ``file_dialog``,
        ``color_dialog``, etc.) on a worker thread; GTK widgets must be driven
        from the thread running the GLib main loop, otherwise ``dialog.run()``
        deadlocks or crashes WebKit. Runs inline on the main thread and
        otherwise marshals through ``GLib.idle_add`` + a semaphore, mirroring
        pywebview's own ``create_file_dialog`` implementation.
        """
        if threading.current_thread() is threading.main_thread():
            fn()
            return
        try:
            from gi.repository import GLib  # type: ignore[import-untyped]
        except (ImportError, ValueError):
            fn()
            return
        done = threading.Event()

        def _dispatch() -> bool:
            try:
                fn()
            finally:
                done.set()
            return False

        GLib.idle_add(_dispatch)
        done.wait()

    def _gtk_file_dialog(
        self,
        dialog_type: str,
        directory: str,
        file_types: list[str] | None,
        allow_multiple: bool,
        title: str = "",
    ) -> Any | None:
        try:
            import gi  # type: ignore[import-untyped]

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk  # type: ignore[import-untyped]
        except (ImportError, ValueError):
            return _GTK_UNAVAILABLE

        result_holder: list[Any] = []

        def _run() -> None:
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
                title=title or "",
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
                    result_holder.append(dialog.get_filename())
                elif allow_multiple:
                    result_holder.append(list(dialog.get_filenames()))
                else:
                    result_holder.append(dialog.get_filename())

            dialog.destroy()

        self._run_gtk_modal(_run)
        return result_holder[0] if result_holder else None

    def alert(self, message: str) -> None:
        """Show a browser-style alert dialog."""
        self._eval_js(f"alert({json.dumps(message)})")

    def confirm(self, message: str) -> bool:
        """Show a browser-style confirm dialog. Returns True if OK was clicked."""
        return bool(self._js_eval(f"confirm({json.dumps(message)})"))

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
            picked = self._js_eval(js)
            return picked if picked else None

        rgba = Gdk.RGBA()
        rgba.parse(initial_color)
        dialog = Gtk.ColorChooserDialog(title=title, parent=None)
        dialog.set_rgba(rgba)
        dialog.set_use_alpha(False)

        result: list[str] = []

        def _run() -> None:
            if dialog.run() == Gtk.ResponseType.OK:
                c = dialog.get_rgba()
                result.append(
                    f"#{int(c.red * 255):02x}{int(c.green * 255):02x}{int(c.blue * 255):02x}"
                )
            dialog.destroy()

        self._run_gtk_modal(_run)
        return result[0] if result else None

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

        result: list[dict[str, Any]] = []

        def _run() -> None:
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
                result.append(
                    {
                        "family": family,
                        "size": size,
                        "weight": weight,
                        "style": style,
                        "_full_name": font_name,
                    }
                )
            dialog.destroy()

        self._run_gtk_modal(_run)
        return result[0] if result else None

    def test_loop(self) -> TestLoop:
        """Build the widget tree without a native window (headless).

        Returns a :class:`TestLoop` recorder that captures the JS emitted by
        ``_sync()``/``_eval_js()`` instead of calling pywebview, so widgets can
        be exercised in CI/without a display (no GTK/WebKit involved).

        Example::

            app = Application("t")
            label = Label(text="hi")
            app.add(label)
            loop = app.test_loop()
            assert "hi" in loop.html
            label.text = "bye"
            assert "bye" in "".join(loop.js_calls)
            loop.stop()
        """
        self._running = True
        self._window = _TestWindow()
        return TestLoop(self)


class _TestWindow:
    """Minimal pywebview-compatible window that records ``evaluate_js`` calls."""

    def __init__(self) -> None:
        self.js_calls: list[str] = []

    def evaluate_js(self, js: str) -> None:
        self.js_calls.append(js)

    def destroy(self) -> None:
        pass


class TestLoop:
    """Headless controller returned by :meth:`Application.test_loop`.

    Exposes the rendered HTML, the JS emitted so far, and helpers to push
    bridge events into the widget tree (same path pywebview would use).
    """

    __test__ = False

    def __init__(self, app: Application) -> None:
        self._app = app
        self._html = app._build_html()

    @property
    def html(self) -> str:
        """The full HTML document built for the current widget tree."""
        return self._html

    @property
    def js_calls(self) -> list[str]:
        """Every ``evaluate_js`` string sent to the (fake) window."""
        window = self._app._window
        return list(window.js_calls) if isinstance(window, _TestWindow) else []

    def fire(self, widget_id: str, event_name: str, data: Any = None) -> None:
        """Deliver a bridge event as if it came from JS."""
        payload = json.dumps(data) if data is not None else None
        _JSAPI_INSTANCE.on_event(widget_id, event_name, payload)

    def stop(self) -> None:
        """Tear down the loop: stop the app and fire ``on_close`` callbacks."""
        self._app._running = False
        self._app._window = None
        self._app._fire_close_callbacks()


Window = Application
