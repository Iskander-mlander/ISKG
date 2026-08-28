"""Color, file browser, modal, tab, range slider, toast widgets.

A focused set of widgets that fill common gaps in the basic toolkit
without bloating the public API.
"""

from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import Any

from ..base import Widget

# ─── ColorPicker ────────────────────────────────────────────────────────


def _hex_to_rgb(hex_: str) -> tuple[int, int, int]:
    hex_ = hex_.lstrip("#")
    if len(hex_) == 3:
        hex_ = "".join(c * 2 for c in hex_)
    return int(hex_[0:2], 16), int(hex_[2:4], 16), int(hex_[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{int(r) & 0xFF:02x}{int(g) & 0xFF:02x}{int(b) & 0xFF:02x}"


def _rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r_, g_, b_), min(r_, g_, b_)
    df = mx - mn
    if df == 0:
        h = 0
    elif mx == r_:
        h = ((g_ - b_) / df) % 6
    elif mx == g_:
        h = (b_ - r_) / df + 2
    else:
        h = (r_ - g_) / df + 4
    h *= 60
    s = 0 if mx == 0 else df / mx
    v = mx
    return h, s, v


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    c = v * s
    h_ = (h % 360) / 60
    x = c * (1 - abs(h_ % 2 - 1))
    if h_ < 1:
        r, g, b = c, x, 0
    elif h_ < 2:
        r, g, b = x, c, 0
    elif h_ < 3:
        r, g, b = 0, c, x
    elif h_ < 4:
        r, g, b = 0, x, c
    elif h_ < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    m = v - c
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


class ColorPicker(Widget):
    """A color picker with HSV swatch, RGB/HEX inputs and a ``color`` property.

    Args:
        parent: parent widget.
        color: initial color (hex string, ``#rrggbb``).
        command: optional callback invoked when the color changes.
        kwargs: forwarded to :class:`~iskg.base.Widget`.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        color: str = "#22d3ee",
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["color"] = color
        if command is not None:
            self._config_dict["command"] = command

    @property
    def color(self) -> str:
        return self._config_dict.get("color", "#22d3ee")

    @color.setter
    def color(self, value: str) -> None:
        if not value.startswith("#"):
            value = f"#{value}"
        self._config_dict["color"] = value
        self._sync()

    def _render(self) -> str:
        style = self._render_style()
        attrs = self._render_attrs()
        c = self.color
        return f'''<div id="{self._id}" class="iskg-colorpicker" style="{style}" {attrs}>
  <div class="iskg-cp-swatch" id="{self._id}-sw" style="background:{c};"></div>
  <input id="{self._id}-hex" class="iskg-cp-hex" type="text" value="{c}" maxlength="7" />
  <div class="iskg-cp-sliders">
    <label>R <input type="range" min="0" max="255" id="{self._id}-r" value="{_hex_to_rgb(c)[0]}"></label>
    <label>G <input type="range" min="0" max="255" id="{self._id}-g" value="{_hex_to_rgb(c)[1]}"></label>
    <label>B <input type="range" min="0" max="255" id="{self._id}-b" value="{_hex_to_rgb(c)[2]}"></label>
  </div>
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var id="{self._id}";
  var sw=document.getElementById(id+"-sw");
  var hex=document.getElementById(id+"-hex");
  var rIn=document.getElementById(id+"-r");
  var gIn=document.getElementById(id+"-g");
  var bIn=document.getElementById(id+"-b");
  function set(c){{
    sw.style.background=c;
    hex.value=c;
    var p=c.replace("#","");
    rIn.value=parseInt(p.substr(0,2),16);
    gIn.value=parseInt(p.substr(2,2),16);
    bIn.value=parseInt(p.substr(4,2),16);
    iskg_bridge_event(id,"change",c);
  }}
  hex.addEventListener("change",function(){{
    var v=hex.value.trim();
    if(!v.startsWith("#"))v="#"+v;
    if(/^#[0-9a-fA-F]{{6}}$/.test(v))set(v);
  }});
  function rgb(){{
    var r=+rIn.value, g=+gIn.value, b=+bIn.value;
    var h=((r<16?"0":"")+r.toString(16))+((g<16?"0":"")+g.toString(16))+((b<16?"0":"")+b.toString(16));
    set("#"+h);
  }}
  rIn.addEventListener("input",rgb);
  gIn.addEventListener("input",rgb);
  bIn.addEventListener("input",rgb);
  sw.addEventListener("click",function(){{
    var c=sw.style.background;
    iskg_bridge_event(id,"click",c);
  }});
  window._iskg_colorpicker_{{id}}=set;
}})();'''

    def _render_update_js(self) -> str:
        c = self.color
        r, g, b = _hex_to_rgb(c)
        return f'''var id="{self._id}";
var sw=document.getElementById(id+"-sw");
var hex=document.getElementById(id+"-hex");
var rIn=document.getElementById(id+"-r");
var gIn=document.getElementById(id+"-g");
var bIn=document.getElementById(id+"-b");
if(sw)sw.style.background={json.dumps(c)};
if(hex)hex.value={json.dumps(c)};
if(rIn)rIn.value={r};
if(gIn)gIn.value={g};
if(bIn)bIn.value={b};'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            val = str(event_data or "")
            if not val.startswith("#"):
                val = f"#{val}"
            self._config_dict["color"] = val
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(val)
        super()._handle_bridge_event(event_name, event_data)


# ─── Modal ──────────────────────────────────────────────────────────────


class Modal(Widget):
    """An overlay dialog with a backdrop and a centered content frame.

    Use :meth:`show` and :meth:`hide` to control visibility. Optionally
    fires a ``"close"`` event when the user clicks the backdrop or the
    close button.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        title: str = "",
        width: int = 400,
        height: int = 300,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["title"] = title
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["visible"] = False
        self._children: list[Widget] = []
        self._on_close: Callable | None = None

    def add(self, child: Widget) -> Widget:  # type: ignore[override]
        # Modal manages its own children list, independent of the standard
        # Widget.add() tree.
        if child not in self._children:
            self._children.append(child)
            child._parent = self
        self._sync()
        return child

    def show(self) -> None:
        self._config_dict["visible"] = True
        self._sync()

    def hide(self) -> None:
        self._config_dict["visible"] = False
        self._sync()

    @property
    def visible(self) -> bool:
        return bool(self._config_dict.get("visible", False))

    @visible.setter
    def visible(self, value: bool) -> None:
        if value:
            self.show()
        else:
            self.hide()

    def on_close(self, callback: Callable) -> None:
        self._on_close = callback

    def _render(self) -> str:
        style = self._render_style()
        attrs = self._render_attrs()
        width = self._config_dict.get("width", 400)
        height = self._config_dict.get("height", 300)
        title = self._config_dict.get("title", "")
        visible = self._config_dict.get("visible", False)
        display = "block" if visible else "none"
        children_html = "".join(c._render() for c in self._children if not c._destroyed)
        title_html = f'<div class="iskg-modal-title">{title}</div>' if title else ""
        return f'''<div id="{self._id}" class="iskg-modal" style="display:{display};" {attrs}>
  <div class="iskg-modal-backdrop" id="{self._id}-backdrop"></div>
  <div class="iskg-modal-frame" style="width:{width}px;height:{height}px;{style}">
    {title_html}
    <button class="iskg-modal-close" id="{self._id}-close">×</button>
    <div class="iskg-modal-body">{children_html}</div>
  </div>
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var id="{self._id}";
  var close=document.getElementById(id+"-close");
  var back=document.getElementById(id+"-backdrop");
  function hide(){{
    var m=document.getElementById(id);
    if(m)m.style.display="none";
    iskg_bridge_event(id,"close","");
  }}
  if(close)close.onclick=hide;
  if(back)back.onclick=hide;
  window._iskg_modal_hide_{{id}}=hide;
}})();'''

    def _render_update_js(self) -> str:
        visible = self._config_dict.get("visible", False)
        return f'var m=document.getElementById("{self._id}");if(m)m.style.display={json.dumps("block" if visible else "none")};'

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "close":
            self.hide()
            if self._on_close is not None:
                with contextlib.suppress(Exception):
                    self._on_close()
        super()._handle_bridge_event(event_name, event_data)


# ─── TabBar ─────────────────────────────────────────────────────────────


class TabBar(Widget):
    """A lightweight tab bar that lives outside a Notebook (e.g. as view
    switcher in a header). Use :meth:`add_tab` and the ``current_tab``
    property to drive the active tab. Fires a ``"change"`` event with the
    new index when the user clicks a tab.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._tabs: list[str] = []
        self._config_dict["active"] = 0

    def add_tab(self, title: str) -> int:
        self._tabs.append(title)
        self._sync()
        return len(self._tabs) - 1

    def remove_tab(self, idx: int) -> bool:
        if 0 <= idx < len(self._tabs):
            self._tabs.pop(idx)
            self._config_dict["active"] = max(
                0, min(self._config_dict["active"], len(self._tabs) - 1)
            )
            self._sync()
            return True
        return False

    @property
    def current_tab(self) -> int:
        return self._config_dict.get("active", 0)

    @current_tab.setter
    def current_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._tabs):
            self._config_dict["active"] = idx
            self._sync()

    @property
    def tab_count(self) -> int:
        return len(self._tabs)

    def _render(self) -> str:
        style = self._render_style()
        attrs = self._render_attrs()
        active = self._config_dict.get("active", 0)
        tabs_html = "".join(
            f'<div class="iskg-tab{" active" if i == active else ""}" data-idx="{i}">{t}</div>'
            for i, t in enumerate(self._tabs)
        )
        return (
            f'<div id="{self._id}" class="iskg-tabbar" style="{style}" {attrs}>{tabs_html}</div>'
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-tab").forEach(function(t){{
    t.onclick=function(){{
      el.querySelectorAll(".iskg-tab").forEach(function(x){{x.classList.remove("active");}});
      this.classList.add("active");
      iskg_bridge_event("{self._id}","change",this.getAttribute("data-idx"));
    }};
  }});
}})();'''


# ─── RangeSlider ─────────────────────────────────────────────────────────


class RangeSlider(Widget):
    """A range slider with two handles (low/high).

    Args:
        parent: parent widget.
        low: initial low value.
        high: initial high value.
        from_: minimum allowed value.
        to: maximum allowed value.
        command: optional callback fired with ``(low, high)`` on change.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        low: float = 25,
        high: float = 75,
        from_: float = 0,
        to: float = 100,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["low"] = min(low, high)
        self._config_dict["high"] = max(low, high)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        if command is not None:
            self._config_dict["command"] = command

    @property
    def low(self) -> float:
        return self._config_dict.get("low", 0)

    @low.setter
    def low(self, v: float) -> None:
        v = float(v)
        if v > self.high:
            v = self.high
        self._config_dict["low"] = v
        self._sync()

    @property
    def high(self) -> float:
        return self._config_dict.get("high", 100)

    @high.setter
    def high(self, v: float) -> None:
        v = float(v)
        if v < self.low:
            v = self.low
        self._config_dict["high"] = v
        self._sync()

    @property
    def range(self) -> tuple[float, float]:
        return self.low, self.high

    @range.setter
    def range(self, value: tuple[float, float]) -> None:
        lo, hi = min(value), max(value)
        self._config_dict["low"] = float(lo)
        self._config_dict["high"] = float(hi)
        self._sync()

    def _render(self) -> str:
        lo = self._config_dict.get("low", 0)
        hi = self._config_dict.get("high", 100)
        min_ = self._config_dict.get("from", 0)
        max_ = self._config_dict.get("to", 100)
        style = self._render_style()
        width = self._config_dict.get("width", 200)
        attrs = self._render_attrs()
        rng = max(1, max_ - min_)
        lp = (lo - min_) / rng * 100
        hp = (hi - min_) / rng * 100
        return f'''<div id="{self._id}" class="iskg-rangeslider" style="{style}width:{width}px;" {attrs}>
  <div class="iskg-rs-track"><div class="iskg-rs-fill" style="left:{lp}%;width:{hp - lp}%;"></div></div>
  <input type="range" class="iskg-rs-low" id="{self._id}-low" min="{min_}" max="{max_}" value="{lo}">
  <input type="range" class="iskg-rs-high" id="{self._id}-high" min="{min_}" max="{max_}" value="{hi}">
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var id="{self._id}";
  var low=document.getElementById(id+"-low");
  var high=document.getElementById(id+"-high");
  function emit(){{
    var lo=+low.value, hi=+high.value;
    if(lo>hi){{lo=hi;low.value=lo;}}
    var fill=document.querySelector("#"+id+" .iskg-rs-fill");
    var min_=+low.min, max_=+low.max;
    var lp=(lo-min_)/(max_-min_)*100;
    var hp=(hi-min_)/(max_-min_)*100;
    if(fill){{fill.style.left=lp+"%";fill.style.width=(hp-lp)+"%";}}
    iskg_bridge_event(id,"change",lo+","+hi);
  }}
  low.oninput=emit;
  high.oninput=emit;
}})();'''

    def _render_update_js(self) -> str:
        lo = self.low
        hi = self.high
        min_ = self._config_dict.get("from", 0)
        max_ = self._config_dict.get("to", 100)
        rng = max(1, max_ - min_)
        lp = (lo - min_) / rng * 100
        hp = (hi - min_) / rng * 100
        return f'''var id="{self._id}";
var low=document.getElementById(id+"-low");
var high=document.getElementById(id+"-high");
if(low)low.value={lo};
if(high)high.value={hi};
var fill=document.querySelector("#"+id+" .iskg-rs-fill");
if(fill){{fill.style.left={lp}+"%";fill.style.width={hp - lp}+"%";}}'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            try:
                lo_s, hi_s = str(event_data or "").split(",", 1)
                self._config_dict["low"] = float(lo_s)
                self._config_dict["high"] = float(hi_s)
            except (ValueError, TypeError):
                pass
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(self.low, self.high)
        super()._handle_bridge_event(event_name, event_data)
