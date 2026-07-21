import json

_counter = [0]


def _new_id():
    _counter[0] += 1
    return f"iw{_counter[0]}"


_CONFIG_TO_CSS = [
    ("padding", "padding", True),
    ("bg", "background", False),
    ("background", "background", False),
    ("fg", "color", False),
    ("foreground", "color", False),
    ("font-size", "font-size", True),
    ("font-family", "font-family", False),
    ("border-color", "border-color", False),
    ("border-width", "border-width", True),
    ("border-radius", "border-radius", True),
    ("opacity", "opacity", False),
    ("text-align", "text-align", False),
    ("margin", "margin", True),
]


class Widget:
    def __init__(self, parent=None, **kwargs):
        self._id = _new_id()
        self._parent = None
        self._children = []
        self._config_dict = {}
        self._layout_mode = None
        self._layout_info = {}
        self._bindings = {}
        self._destroyed = False
        self._app = None

        for k, v in kwargs.items():
            self._config_dict[k.replace("_", "-")] = v

        if parent is not None:
            parent.add(self)

    @property
    def widget_id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def app(self):
        if self._app:
            return self._app
        if self._parent:
            return self._parent.app
        return None

    def add(self, child):
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

    def remove(self, child):
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def pack(self, side="top", fill="none", expand=False, padx=0, pady=0, anchor="nw"):
        self._layout_mode = "pack"
        self._layout_info = {
            "side": side,
            "fill": fill,
            "expand": expand,
            "padx": padx,
            "pady": pady,
            "anchor": anchor,
        }
        return self

    def grid(self, row=0, column=0, rowspan=1, columnspan=1, sticky="", padx=0, pady=0):
        self._layout_mode = "grid"
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

    def place(self, x=0, y=0, width=None, height=None, anchor="nw"):
        self._layout_mode = "place"
        self._layout_info = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "anchor": anchor,
        }
        return self

    def config(self, **kwargs):
        for k, v in kwargs.items():
            self._config_dict[k.replace("_", "-")] = v
        self._sync()
        return self

    def cget(self, key):
        return self._config_dict.get(key.replace("_", "-"))

    def bind(self, event, callback):
        self._bindings[event] = callback

    def unbind(self, event):
        self._bindings.pop(event, None)

    def _handle_bridge_event(self, event_name, event_data):
        cb = self._bindings.get(event_name)
        if cb:
            cb(event_data)
        cmd = self._config_dict.get("command")
        if cmd and event_name in ("click", "change"):
            cmd()

    def destroy(self):
        self._destroyed = True
        for child in list(self._children):
            child.destroy()
        if self._parent:
            self._parent.remove(self)
        if self._app:
            self._app._widget_destroyed(self._id)

    def _sync(self):
        if self._app and self._app._running:
            parts = []
            js = self._render_update_js()
            if js:
                parts.append(js)
            style_js = self._render_style_update_js()
            if style_js:
                parts.append(style_js)
            if parts:
                self._app._eval_js(";".join(parts))

    def _render(self) -> str:
        return ""

    def _render_js(self) -> str:
        return ""

    def _render_update_js(self) -> str:
        return ""

    def _render_style_css(self):
        css = ""
        for cfg_key, css_prop, is_px in _CONFIG_TO_CSS:
            val = self._config_dict.get(cfg_key)
            if val is not None and val != "":
                if isinstance(val, (int, float)) and is_px:
                    css += f"{css_prop}:{val}px;"
                else:
                    css += f"{css_prop}:{val};"
        return css

    def _render_style_update_js(self):
        css = self._render_style_css()
        if css:
            return f'iskg_set_style("{self._id}",{json.dumps(css)});'
        return ""

    def _render_style(self):
        li = self._layout_info
        style = ""
        if self._layout_mode == "pack":
            if li.get("expand"):
                style += "flex:1;min-height:0;min-width:0;"
            if li.get("fill") in ("x", "both"):
                style += "width:100%;"
            if li.get("fill") in ("y", "both"):
                style += "height:100%;"
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
            if "w" in sticky:
                s += "justify-self:start;"
            if "e" in sticky:
                s += "justify-self:end;"
            if "n" in sticky:
                s += "align-self:start;"
            if "s" in sticky:
                s += "align-self:end;"
            if "we" in sticky:
                s += "justify-self:stretch;"
            if "ns" in sticky:
                s += "align-self:stretch;"
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

    def _render_children(self):
        parts = []
        for child in self._children:
            if child._destroyed:
                continue
            parts.append(child._render())
        return "".join(parts)

    def _render_children_js(self):
        parts = []
        for child in self._children:
            if child._destroyed:
                continue
            js = child._render_js()
            if js:
                parts.append(js)
            parts.append(child._render_children_js())
        return "".join(parts)

    def _collect_widgets(self, depth=0):
        result = [(depth, self)]
        for child in self._children:
            if child._destroyed:
                continue
            result.extend(child._collect_widgets(depth + 1))
        return result
