"""Base Widget class with layout engines (pack/grid/place), event bindings,
style rendering, and widget tree management."""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable
from typing import Any

_counter: list[int] = [0]


def _new_id() -> str:
    _counter[0] += 1
    return f"iw{_counter[0]}"


_CONFIG_TO_CSS: list[tuple[str, str, bool]] = [
    ("padding", "padding", True),
    ("bg", "background", False),
    ("background", "background", False),
    ("fg", "color", False),
    ("foreground", "color", False),
    ("font-size", "font-size", True),
    ("font-family", "font-family", False),
    ("font-weight", "font-weight", False),
    ("border-color", "border-color", False),
    ("border-width", "border-width", True),
    ("border-radius", "border-radius", True),
    ("opacity", "opacity", False),
    ("text-align", "text-align", False),
    ("margin", "margin", True),
    ("cursor", "cursor", False),
    ("width", "width", True),
    ("height", "height", True),
    ("min-width", "min-width", True),
    ("min-height", "min-height", True),
    ("max-width", "max-width", True),
    ("max-height", "max-height", True),
    ("flex", "flex", False),
    ("overflow", "overflow", False),
    ("overflow-x", "overflow-x", False),
    ("overflow-y", "overflow-y", False),
    ("gap", "gap", True),
    ("order", "order", False),
    ("align-self", "align-self", False),
    ("justify-self", "justify-self", False),
    ("align-items", "align-items", False),
    ("justify-content", "justify-content", False),
    ("inset", "inset", True),
    ("top", "top", True),
    ("right", "right", True),
    ("bottom", "bottom", True),
    ("left", "left", True),
    ("object-fit", "object-fit", False),
    ("aspect-ratio", "aspect-ratio", False),
    ("z-index", "z-index", False),
    ("transform", "transform", False),
    ("transition", "transition", False),
    ("white-space", "white-space", False),
    ("text-overflow", "text-overflow", False),
    ("line-height", "line-height", False),
]

_PX_KEYS: set[str] = {k for k, _, px in _CONFIG_TO_CSS if px}


def _validate_css_value(key: str, val: Any) -> None:
    if key in _PX_KEYS and val is not None and val != "" and isinstance(val, str):
        cleaned = val.strip()
        if cleaned and not any(c.isdigit() for c in cleaned):
            warnings.warn(
                f"Numeric CSS key '{key}' received non-numeric string {val!r}. "
                f"Expected a number (e.g. 10) or mixed string (e.g. '10px 5px').",
                stacklevel=3,
            )


class Widget:
    """Base class for all ISKG widgets.

    Manages widget identity, parent-child tree, layout configuration,
    style rendering, event bindings, and bridge communication with the
    JavaScript frontend.

    Every concrete widget (Button, Label, Frame, etc.) inherits from this class.

    Configuration kwargs and ``.config()`` accept any key. Underscores in keys
    are converted to hyphens. Common CSS keys (``fg``, ``bg``, ``font_size``,
    ``padding``, ``margin``, ``flex``, ``overflow``, etc.) from
    ``_CONFIG_TO_CSS`` are automatically mapped to inline styles. Keys starting
    with ``--`` are treated as CSS custom properties.
    """

    def __init__(self, parent: Widget | None = None, **kwargs: Any) -> None:
        self._id: str = _new_id()
        self._parent: Widget | None = None
        self._children: list[Widget] = []
        self._config_dict: dict[str, Any] = {}
        self._layout_mode: str | None = None
        self._layout_info: dict[str, Any] = {}
        self._bindings: dict[str, Callable] = {}
        self._key_bindings: list[dict[str, Any]] = []
        self._destroyed: bool = False
        self._app: Any = None
        self._textvariable: Any = None
        self._variable: Any = None
        self._last_sync_js: str = ""

        for k, v in kwargs.items():
            key = k.replace("_", "-")
            if key == "state":
                self._config_dict["state"] = v
                self._config_dict["disabled"] = v == "disabled"
            elif key == "font":
                self._set_font(v)
            elif key in ("textvariable", "text-variable"):
                self._textvariable = v
                self._config_dict["textvariable"] = v
                if v is not None:
                    v._widgets.append(self)
            elif key in ("variable",):
                self._variable = v
                self._config_dict["variable"] = v
                if v is not None:
                    v._widgets.append(self)
            elif key == "tooltip":
                self._config_dict["tooltip"] = str(v) if v else ""
            else:
                self._config_dict[key] = v

        if parent is not None:
            parent.add(self)

    @property
    def widget_id(self) -> str:
        """Unique identifier for this widget instance."""
        return self._id

    @property
    def parent(self) -> Widget | None:
        """Parent widget, or None if this is a root widget."""
        return self._parent

    @property
    def app(self) -> Any:
        """The Application instance this widget belongs to, or None."""
        if self._app:
            return self._app
        if self._parent:
            return self._parent.app
        return None

    def add(self, child: Widget) -> None:
        """Add a child widget to this widget's children list.

        If the child is already present, this is a no-op.
        """
        if child in self._children:
            return
        child._parent = self
        self._children.append(child)
        app = self.app
        if app is not None:
            from .app import _HANDLERS

            child._app = app
            for _, w in child._collect_widgets():
                w._app = app
                if isinstance(w, Widget):
                    _HANDLERS[w._id] = w._handle_bridge_event

    def remove(self, child: Widget) -> None:
        """Remove a child widget from this widget's children list."""
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def pack(
        self,
        side: str = "top",
        fill: str = "none",
        expand: bool = False,
        padx: int = 0,
        pady: int = 0,
        anchor: str = "nw",
        in_: Widget | None = None,
    ) -> Widget:
        """Arrange this widget using pack layout.

        Args:
            side: ``"top"``, ``"left"``, ``"bottom"``, or ``"right"``.
            fill: ``"none"``, ``"x"``, ``"y"``, or ``"both"``.
            expand: whether to take extra space.
            padx: horizontal padding in pixels.
            pady: vertical padding in pixels.
            anchor: ``"nw"``, ``"n"``, ``"ne"``, ``"w"``, ``"e"``, ``"sw"``, ``"s"``, ``"se"``.
            in_: parent widget to pack into. If different from current parent,
                the widget is reparented automatically.
        """
        if in_ is not None and in_ is not self._parent:
            if self._parent is not None:
                self._parent.remove(self)
            in_.add(self)
        if self._layout_mode and self._layout_mode != "pack":
            warnings.warn(
                f"Widget {self._id}: pack() called after {self._layout_mode}(). "
                f"Previous layout will be overwritten.",
                stacklevel=2,
            )
        self._layout_mode = "pack"
        self._config_dict.pop("hidden", None)
        self._layout_info = {
            "side": side,
            "fill": fill,
            "expand": expand,
            "padx": padx,
            "pady": pady,
            "anchor": anchor,
        }
        return self

    def grid(
        self,
        row: int = 0,
        column: int = 0,
        rowspan: int = 1,
        columnspan: int = 1,
        sticky: str = "",
        padx: int = 0,
        pady: int = 0,
    ) -> Widget:
        """Arrange this widget using grid layout.

        Args:
            row: row index (0-based).
            column: column index (0-based).
            rowspan: number of rows to span.
            columnspan: number of columns to span.
            sticky: combination of ``"n"``, ``"s"``, ``"e"``, ``"w"``,
                or ``"c"`` for center.
            padx: horizontal padding.
            pady: vertical padding.

        To control row/column weights and minimum sizes, use
        :meth:`~iskg.widgets._containers.Frame.grid_columnconfigure`
        and :meth:`~iskg.widgets._containers.Frame.grid_rowconfigure`
        on the parent *Frame*.
        """
        if self._layout_mode and self._layout_mode != "grid":
            warnings.warn(
                f"Widget {self._id}: grid() called after {self._layout_mode}(). "
                f"Previous layout will be overwritten.",
                stacklevel=2,
            )
        self._layout_mode = "grid"
        self._config_dict.pop("hidden", None)
        self._config_dict.pop("_grid_saved", None)
        self._layout_info = {
            "row": row,
            "column": column,
            "rowspan": rowspan,
            "columnspan": columnspan,
            "sticky": sticky,
            "padx": padx,
            "pady": pady,
        }
        return self

    def place(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
        anchor: str = "nw",
    ) -> Widget:
        """Position this widget at absolute coordinates.

        Args:
            x: left offset in pixels.
            y: top offset in pixels.
            width: explicit width in pixels, or None for auto.
            height: explicit height in pixels, or None for auto.
            anchor: ``"nw"``, ``"n"``, ``"ne"``, ``"w"``, ``"e"``, ``"sw"``, ``"s"``, ``"se"``.
        """
        if self._layout_mode and self._layout_mode != "place":
            warnings.warn(
                f"Widget {self._id}: place() called after {self._layout_mode}(). "
                f"Previous layout will be overwritten.",
                stacklevel=2,
            )
        self._layout_mode = "place"
        self._config_dict.pop("hidden", None)
        self._layout_info = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "anchor": anchor,
        }
        return self

    def grid_remove(self) -> None:
        """Remove from grid layout, remembering position.
        Call :meth:`grid` with the same parameters to restore.
        """
        self._config_dict["_grid_saved"] = dict(self._layout_info)
        self._config_dict["hidden"] = True
        self._sync()

    def grid_forget(self) -> None:
        """Remove from grid layout (position lost).
        Call :meth:`grid` with new parameters to re-display.
        """
        self._config_dict["hidden"] = True
        self._sync()

    pack_forget = grid_forget

    @property
    def tooltip(self) -> str:
        """Get/set the hover tooltip text for this widget."""
        return self._config_dict.get("tooltip", "")

    @tooltip.setter
    def tooltip(self, value: str) -> None:
        self._config_dict["tooltip"] = str(value)
        self._sync()

    def _render_tooltip_js(self) -> str:
        text = self._config_dict.get("tooltip", "")
        if not text:
            return ""
        escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
        return f'''(function(){{
var el=document.getElementById("{self._id}");
if(!el)return;
var tip=document.createElement("div");
tip.className="iskg-tooltip";
tip.innerHTML="{escaped}";
tip.style.display="none";
document.body.appendChild(tip);
var timer=null;
el.onmouseenter=function(e){{
  timer=setTimeout(function(){{
    var r=el.getBoundingClientRect();
    tip.style.display="block";
    tip.style.left=Math.min(e.clientX,document.documentElement.clientWidth-tip.offsetWidth)+"px";
    tip.style.top=(r.bottom+4)+"px";
  }},400);
}};
el.onmouseleave=function(){{clearTimeout(timer);tip.style.display="none";}};
}})();'''

    def config(self, **kwargs: Any) -> Widget:
        """Configure widget properties.

        Accepts any keyword argument; underscores in keys are converted to
        hyphens for CSS. Common keys: ``fg``, ``bg``, ``font_size``,
        ``padding``, ``border_color``, ``opacity``, etc.

        Also accepts ``state`` (``"normal"``, ``"disabled"``, ``"readonly"``),
        ``visible`` (bool), ``textvariable``, and ``variable`` which are
        handled specially.
        """
        for k, v in kwargs.items():
            key = k.replace("_", "-")
            if key == "state":
                self._set_state(v)
            elif key == "visible":
                if v:
                    self._eval_js(f'iskg_set_visible("{self._id}",true);')
                else:
                    self._eval_js(f'iskg_set_visible("{self._id}",false);')
            elif key == "font":
                self._set_font(v)
            elif key in ("textvariable", "text-variable"):
                if v is not None:
                    v._widgets.append(self)
                self._textvariable = v
                self._config_dict["textvariable"] = v
            elif key in ("variable",):
                if v is not None:
                    v._widgets.append(self)
                self._variable = v
                self._config_dict["variable"] = v
            elif key == "tooltip":
                self._config_dict["tooltip"] = str(v) if v else ""
                self._eval_js(self._render_tooltip_js())
            else:
                if "-" in key and not key.startswith("--"):
                    known = {css_k for css_k, _, _ in _CONFIG_TO_CSS}
                    if key not in known:
                        warnings.warn(
                            f"Unknown config key '{key}' on {type(self).__name__} "
                            f"(set via config({k}=...)). If this is a custom CSS property, "
                            f"prefix it with '--'.",
                            stacklevel=2,
                        )
                    else:
                        _validate_css_value(key, v)
                self._config_dict[key] = v
        self._sync()
        return self

    def _get_cfg(self, key: str, default: Any = None) -> Any:
        """Read config key, trying hyphen first, then underscore."""
        if key in self._config_dict:
            return self._config_dict[key]
        alt = key.replace("-", "_")
        return self._config_dict.get(alt, default)

    def _var_updated(self, var: Any) -> None:
        """Called when a bound variable changes value.
        Override in subclasses to update the widget display.
        """
        pass

    def cget(self, key: str) -> Any:
        """Get a widget configuration value by key."""
        return self._config_dict.get(key.replace("_", "-"))

    def _eval_js(self, js: str) -> None:
        app = self.app
        if app and app._running:
            app._eval_js(js)

    def _set_font(self, v: Any) -> None:
        if isinstance(v, str):
            self._config_dict["font"] = v
            return
        if isinstance(v, (list, tuple)):
            if len(v) > 0:
                self._config_dict["font-family"] = v[0]
            if len(v) > 1:
                self._config_dict["font-size"] = v[1]
            if len(v) > 2:
                self._config_dict["font-weight"] = v[2]

    def _set_state(self, state: str) -> None:
        self._config_dict["state"] = state
        self._config_dict["disabled"] = state == "disabled"
        if state == "disabled":
            self._eval_js(f'iskg_set_enabled("{self._id}",false);')
        elif state == "readonly":
            self._eval_js(f'iskg_set_attr("{self._id}","readonly","true");')
        else:
            self._eval_js(f'iskg_set_enabled("{self._id}",true);')
            self._eval_js(f'iskg_set_attr("{self._id}","readonly","");')

    @property
    def state(self) -> str:
        """Get the widget state (``"normal"``, ``"disabled"``, ``"readonly"``)."""
        return self._config_dict.get("state", "normal")

    @state.setter
    def state(self, value: str) -> None:
        self._set_state(value)

    @property
    def visible(self) -> bool:
        """Whether the widget is visible."""
        return not self._config_dict.get("hidden", False)

    @visible.setter
    def visible(self, value: bool) -> None:
        self._config_dict["hidden"] = not value
        self._eval_js(f'iskg_set_visible("{self._id}",{str(value).lower()});')

    @property
    def width(self) -> int | None:
        return self._config_dict.get("width")

    @width.setter
    def width(self, value: int | None) -> None:
        if value is None:
            self._config_dict.pop("width", None)
        else:
            self._config_dict["width"] = int(value)
        self._sync()

    @property
    def height(self) -> int | None:
        return self._config_dict.get("height")

    @height.setter
    def height(self, value: int | None) -> None:
        if value is None:
            self._config_dict.pop("height", None)
        else:
            self._config_dict["height"] = int(value)
        self._sync()

    @property
    def cursor(self) -> str:
        return self._config_dict.get("cursor", "default")

    @cursor.setter
    def cursor(self, value: str) -> None:
        self._config_dict["cursor"] = value
        self._sync()

    def focus(self) -> None:
        """Move keyboard focus to this widget."""
        self._eval_js(f'iskg_focus("{self._id}");')

    focus_set = focus

    @property
    def takefocus(self) -> bool:
        """Whether this widget can receive keyboard focus. Default ``True`` for
        interactive widgets (Button, Entry, etc.), ``False`` for containers."""
        return self._config_dict.get("takefocus", self._default_takefocus())

    @takefocus.setter
    def takefocus(self, value: bool) -> None:
        self._config_dict["takefocus"] = bool(value)

    def _default_takefocus(self) -> bool:
        return False

    @staticmethod
    def _tabindex_attr(takefocus: bool) -> str:
        return ' tabindex="0"' if takefocus else ""

    def _collect_focusable(self) -> list[Widget]:
        result: list[Widget] = []
        self._collect_focusable_into(result)
        return result

    def _collect_focusable_into(self, result: list[Widget]) -> None:
        if self._destroyed:
            return
        if self.takefocus:
            result.append(self)
        for child in self._children:
            if not child._destroyed:
                child._collect_focusable_into(result)

    def focus_next(self) -> None:
        """Move focus to the next widget in tab order."""
        chain = self._collect_focusable()
        if not chain:
            return
        try:
            idx = chain.index(self)
            nxt = chain[(idx + 1) % len(chain)]
        except ValueError:
            nxt = chain[0]
        nxt.focus()

    def focus_prev(self) -> None:
        """Move focus to the previous widget in tab order."""
        chain = self._collect_focusable()
        if not chain:
            return
        try:
            idx = chain.index(self)
            nxt = chain[(idx - 1) % len(chain)]
        except ValueError:
            nxt = chain[-1]
        nxt.focus()

    def hide(self) -> None:
        """Hide this widget."""
        self.visible = False

    def show(self) -> None:
        """Show this widget."""
        self.visible = True

    class _Timer:
        """A cancelable timer returned by :meth:`after`.

        Attributes:
            running: ``True`` while the timer is pending.
        """

        def __init__(self, timer_id: str, timer: Any) -> None:
            self._id = timer_id
            self._timer = timer
            self.running = True

        def cancel(self) -> None:
            """Cancel this timer. No-op if already fired or cancelled."""
            if self.running:
                self.running = False
                self._timer.cancel()

    def after(self, ms: int, callback: Callable) -> _Timer:
        """Schedule a function to run after *ms* milliseconds.

        Args:
            ms: delay in milliseconds.
            callback: function to call (no arguments).

        Returns:
            A :class:`_Timer` with ``.cancel()`` and ``.running``.
        """
        import threading

        timer_id = f"t{id(callback)}_{id(self)}"
        t = threading.Timer(ms / 1000, callback)
        t.daemon = True
        timer_obj = self._Timer(timer_id, t)
        self._config_dict.setdefault("_timers", {})[timer_id] = timer_obj
        t.start()
        return timer_obj

    def after_cancel(self, timer_id: str) -> None:
        """Cancel a timer by its string ID (legacy)."""
        timers = self._config_dict.get("_timers", {})
        t = timers.pop(timer_id, None)
        if t:
            t.cancel()

    def update(self) -> None:
        """Force a sync update of this widget's rendering."""
        self._sync()

    @staticmethod
    def _parse_key_event(spec: str) -> dict[str, Any] | None:
        """Parse a tkinter-style key event spec like ``"<KeyPress-a>"``.

        Returns a dict with keys: ``event_type`` (``"keypress"``/``"keyrelease"``),
        ``key`` (str or None), ``ctrl``, ``alt``, ``shift`` (bool).
        Returns ``None`` if the spec is not a key event.
        """
        s = spec.strip()
        if not (s.startswith("<") and s.endswith(">")):
            return None
        if s.startswith("<<"):
            return None  # virtual event like <<Custom>>, not a key event
        s = s[1:-1]
        parts = s.split("-")
        result: dict[str, Any] = {
            "event_type": "keypress",
            "key": None,
            "ctrl": False,
            "alt": False,
            "shift": False,
        }
        for p in parts:
            pl = p.lower()
            if pl in ("keypress", "key"):
                result["event_type"] = "keypress"
            elif pl == "keyrelease":
                result["event_type"] = "keyrelease"
            elif pl in ("control", "ctrl"):
                result["ctrl"] = True
            elif pl == "alt":
                result["alt"] = True
            elif pl == "shift":
                result["shift"] = True
            else:
                result["key"] = p
        return result

    def _install_key_binding(self, parsed: dict[str, Any], callback: Callable) -> None:
        entry = dict(parsed)
        entry["cb"] = callback
        self._key_bindings.append(entry)
        self._bindings[parsed["event_type"]] = callback
        if self._app and self._app._running:
            self._eval_js(self._render_key_binding_js(parsed))

    def _render_key_binding_js(self, parsed: dict[str, Any]) -> str:
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
        return f'iskg_bind_key("{self._id}",{evt},{key_json},{mods_json});'

    def _render_key_bindings_js(self) -> str:
        parts = [self._render_key_binding_js(e) for e in self._key_bindings]
        return "".join(parts)

    def bind(self, event: str, callback: Callable) -> None:
        """Bind a callback to an event.

        Supports standard bridge events (``"click"``, ``"change"``, etc.),
        tkinter-style key events (``"<KeyPress-a>"``, ``"<KeyRelease-Return>"``,
        ``"<Control-c>"``, ``"<Key>"``), and virtual events
        (``"<<CustomEvent>>"``).

        Key event callbacks receive a dict with ``key``, ``code``, ``ctrl``,
        ``alt``, ``shift``.
        """
        parsed = self._parse_key_event(event)
        if parsed is not None:
            self._install_key_binding(parsed, callback)
        else:
            self._bindings[event] = callback

    def unbind(self, event: str) -> None:
        """Remove a previously bound event callback."""
        parsed = self._parse_key_event(event)
        if parsed is not None:
            et = parsed["event_type"]
            self._key_bindings[:] = [
                e
                for e in self._key_bindings
                if not (
                    e["event_type"] == et
                    and e["key"] == parsed["key"]
                    and e["ctrl"] == parsed["ctrl"]
                    and e["alt"] == parsed["alt"]
                    and e["shift"] == parsed["shift"]
                )
            ]
            self._bindings.pop(et, None)
            if self._app and self._app._running:
                self._eval_js(f'iskg_unbind_key("{self._id}",{json.dumps(et)});')
        else:
            self._bindings.pop(event, None)

    def event_generate(self, event: str, data: Any = None) -> bool:
        """Generate a virtual event that bubbles up the parent chain.

        Args:
            event: event name (e.g. ``"<<Custom>>"``, ``"click"``, ``"change"``).
            data: optional data passed to the callback.

        Returns:
            ``True`` if propagation should stop (callback returned ``"break"``).
        """
        if self._handle_bridge_event(event, data) == "break":
            return True
        if self._parent and not self._parent._destroyed:
            return self._parent.event_generate(event, data)
        return False

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> str | None:
        if event_name in ("change", "input"):
            if self._textvariable is not None and not getattr(self, "_variable_handled", False):
                self._textvariable.set(str(event_data), _from_widget=self)
            if self._variable is not None and not getattr(self, "_variable_handled", False):
                self._variable.set(event_data, _from_widget=self)
        cb = self._bindings.get(event_name)
        if cb:
            result = cb(event_data)
            if result == "break":
                return "break"
        cmd = self._config_dict.get("command")
        if cmd and event_name in ("click", "change"):
            cmd()
        return None

    def destroy(self) -> None:
        """Destroy this widget and all its children."""
        self._destroyed = True
        for child in list(self._children):
            child.destroy()
        if self._parent:
            self._parent.remove(self)
        if self._app:
            self._app._widget_destroyed(self._id)

    def _sync(self) -> None:
        if self._destroyed or not (self._app and self._app._running):
            return
        parts: list[str] = []
        js = self._render_update_js()
        if js:
            parts.append(js)
        style_js = self._render_style_update_js()
        if style_js:
            parts.append(style_js)
        attr_js = self._render_attr_update_js()
        if attr_js:
            parts.append(attr_js)
        combined = ";".join(parts) if parts else ""
        if combined and combined != self._last_sync_js:
            self._last_sync_js = combined
            self._app._eval_js(combined)

    def _render(self) -> str:
        """Return the HTML string for this widget. Override in subclasses."""
        if self._layout_mode == "grid" or self._layout_mode == "pack":
            return f'<div id="{self._id}" style="{self._render_style()}"></div>'
        return ""

    def _render_js(self) -> str:
        """Return JavaScript to initialise this widget. Override in subclasses."""
        return self._render_key_bindings_js() + self._render_tooltip_js()

    def _render_update_js(self) -> str:
        """Return JavaScript to update this widget's DOM. Override in subclasses."""
        return ""

    @staticmethod
    def _css_value(val: Any, is_px: bool) -> str:
        if isinstance(val, (int, float)):
            return f"{val}px" if is_px else str(val)
        s = str(val).strip()
        if is_px and s:
            from re import split as _re_split

            parts = _re_split(r"\s+", s)
            parts = [f"{p}px" if p and p[-1].isdigit() else p for p in parts]
            return " ".join(parts)
        return s

    def _render_style_css(self) -> str:
        css = ""
        for cfg_key, css_prop, is_px in _CONFIG_TO_CSS:
            val = self._config_dict.get(cfg_key)
            if val is not None and val != "":
                css += f"{css_prop}:{self._css_value(val, is_px)};"
        for k, v in self._config_dict.items():
            if k.startswith("--"):
                css += f"{k}:{v};"
        return css

    def _render_style_update_js(self) -> str:
        css = self._render_style_css()
        if css:
            return f'iskg_set_style("{self._id}",{json.dumps(css)});'
        return ""

    def _render_attr_update_js(self) -> str:
        parts = []
        disabled = self._config_dict.get("disabled")
        if disabled is not None:
            parts.append(f'iskg_set_enabled("{self._id}",{"false" if disabled else "true"});')
        return "".join(parts) if parts else ""

    def _render_attrs(self) -> str:
        """Return common HTML attributes (tabindex, disabled)."""
        attrs = ""
        if self._config_dict.get("disabled"):
            attrs += " disabled"
        if self._config_dict.get("takefocus", self._default_takefocus()):
            attrs += ' tabindex="0"'
        return attrs

    def _render_style(self) -> str:
        li = self._layout_info
        style = ""
        if self._config_dict.get("hidden"):
            style += "display:none;"
        if self._layout_mode == "pack":
            side = li.get("side", "top")
            expand = li.get("expand", False)
            fill = li.get("fill", "none")
            if side in ("left", "right"):
                # row: main-axis = horizontal, cross-axis = vertical
                if expand:
                    style += "flex:1;min-height:0;min-width:0;"
                else:
                    style += "flex-shrink:0;"
                if fill in ("y", "both"):
                    style += "align-self:stretch;"
                if fill in ("x", "both") and expand:
                    style += "width:100%;"
                if side == "right" and not expand:
                    style += "margin-left:auto;"
            else:
                # column: main-axis = vertical, cross-axis = horizontal
                if expand:
                    style += "flex:1;min-height:0;min-width:0;"
                if fill in ("x", "both"):
                    style += "align-self:stretch;"
                if fill in ("y", "both") and not expand:
                    style += "height:100%;"
                if side == "bottom":
                    style += "margin-top:auto;"
            if li.get("padx"):
                style += f"padding-left:{li['padx']}px;padding-right:{li['padx']}px;"
            if li.get("pady"):
                style += f"padding-top:{li['pady']}px;padding-bottom:{li['pady']}px;"
        elif self._layout_mode == "grid":
            g = li
            s = f"grid-row:{g.get('row', 0) + 1}/span {max(1, g.get('rowspan', 1))};"
            s += f"grid-column:{g.get('column', 0) + 1}/span {max(1, g.get('columnspan', 1))};"
            if g.get("padx"):
                s += f"padding-left:{g['padx']}px;padding-right:{g['padx']}px;"
            if g.get("pady"):
                s += f"padding-top:{g['pady']}px;padding-bottom:{g['pady']}px;"
            sticky = g.get("sticky", "")
            sticky_set = set(sticky)
            if "we" in sticky or "ew" in sticky:
                s += "justify-self:stretch;"
            elif "w" in sticky_set:
                s += "justify-self:start;"
            elif "e" in sticky_set:
                s += "justify-self:end;"
            elif "c" in sticky_set:
                s += "justify-self:center;"
            if "ns" in sticky:
                s += "align-self:stretch;"
            elif "n" in sticky_set:
                s += "align-self:start;"
            elif "s" in sticky_set:
                s += "align-self:end;"
            elif "c" in sticky_set:
                s += "align-self:center;"
            style += s
        elif self._layout_mode == "place":
            p = li
            style += f"position:absolute;left:{p.get('x', 0)}px;top:{p.get('y', 0)}px;"
            if p.get("width") is not None:
                style += f"width:{p['width']}px;"
            if p.get("height") is not None:
                style += f"height:{p['height']}px;"
        style += self._render_style_css()
        return style

    def _render_children(self) -> str:
        parts: list[str] = []
        for child in self._children:
            if child._destroyed:
                continue
            parts.append(child._render())
        return "".join(parts)

    def _render_children_js(self) -> str:
        parts: list[str] = []
        for child in self._children:
            if child._destroyed:
                continue
            js = child._render_js()
            if js:
                parts.append(js)
            base_js = child._render_key_bindings_js() + child._render_tooltip_js()
            if base_js:
                parts.append(base_js)
            parts.append(child._render_children_js())
        return "".join(parts)

    def _collect_widgets(self, depth: int = 0) -> list[tuple[int, Widget]]:
        result: list[tuple[int, Widget]] = [(depth, self)]
        for child in self._children:
            if child._destroyed:
                continue
            result.extend(child._collect_widgets(depth + 1))
        return result
