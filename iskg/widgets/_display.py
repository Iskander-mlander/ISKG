from __future__ import annotations

from typing import Any

from ..base import Widget


class Label(Widget):
    """A static text label."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        wraplength: int | None = None,
        anchor: str = "",
        justify: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = (
            self._textvariable.get() if self._textvariable is not None else text
        )
        if wraplength is not None:
            self._config_dict["wraplength"] = wraplength
        if anchor:
            self._config_dict["anchor"] = anchor
        if justify:
            self._config_dict["justify"] = justify

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value: str) -> None:
        self._config_dict["text"] = str(value)
        self._sync()

    @property
    def wraplength(self) -> int | None:
        return self._config_dict.get("wraplength")

    @wraplength.setter
    def wraplength(self, value: int | None) -> None:
        if value is not None:
            self._config_dict["wraplength"] = value
        else:
            self._config_dict.pop("wraplength", None)
        self._sync()

    @property
    def anchor(self) -> str:
        return self._config_dict.get("anchor", "")

    @anchor.setter
    def anchor(self, value: str) -> None:
        self._config_dict["anchor"] = value
        self._sync()

    @property
    def justify(self) -> str:
        return self._config_dict.get("justify", "")

    @justify.setter
    def justify(self, value: str) -> None:
        self._config_dict["justify"] = value
        self._sync()

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cls = "iskg-label"
        color = self._config_dict.get("color", "")
        if color:
            cls += f" {color}"
        style = self._render_style()
        wl = self._config_dict.get("wraplength")
        if wl is not None:
            style += f"max-width:{wl}px;"
        anc = self._config_dict.get("anchor", "") or self._config_dict.get("justify", "")
        if anc == "center":
            style += "text-align:center;"
        elif anc == "e" or anc == "right":
            style += "text-align:right;"
        elif anc == "w" or anc == "left":
            style += "text-align:left;"
        return f'<span id="{self._id}" class="{cls}" style="{style}">{escaped}</span>'

    def _var_updated(self, var: Any) -> None:
        if var is self._textvariable:
            self._config_dict["text"] = var.get()
            self._sync()

    def _render_update_js(self) -> str:
        text = self._config_dict.get("text", "")
        escaped = text.replace("\\", "\\\\").replace("'", "\\'")
        return f'iskg_set_text("{self._id}","{escaped}");'


class ProgressBar(Widget):
    """A progress bar widget."""

    def __init__(
        self,
        parent: Widget | None = None,
        value: float = 0,
        max_: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["value"] = value
        self._config_dict["max"] = max_

    @property
    def value(self) -> float:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: float) -> None:
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self) -> str:
        val = self._config_dict.get("value", 0)
        mx = self._config_dict.get("max", 100)
        pct = min(100, max(0, (val / mx * 100))) if mx > 0 else 0
        show_text = self._config_dict.get("show_text", False)
        style = self._render_style()
        width = self._config_dict.get("width", 200)
        text_html = ""
        if show_text:
            text_html = f'<span class="iskg-progress-text">{int(pct)}%</span>'
        return f'''<div class="iskg-progress-wrap" id="{self._id}" style="{style}width:{width}px;">
  <div class="iskg-progress-fill" id="{self._id}-fill" style="width:{pct}%"></div>
  {text_html}
</div>'''

    def _render_update_js(self) -> str:
        val = self._config_dict.get("value", 0)
        mx = self._config_dict.get("max", 100)
        pct = min(100, max(0, (val / mx * 100))) if mx > 0 else 0
        return f'''var el=document.getElementById("{self._id}-fill");
if(el)el.style.width="{pct}%";
var t=document.getElementById("{self._id}").querySelector(".iskg-progress-text");
if(t)t.innerText="{int(pct)}%";'''


class LEDDisplay(Widget):
    """A seven-segment LED-style digital display."""

    def __init__(
        self,
        parent: Widget | None = None,
        value: Any = 0,
        digits: int = 4,
        color: str = "green",
        label: str = "",
        height: int = 32,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["value"] = value
        self._config_dict["digits"] = digits
        self._config_dict["color"] = color
        self._config_dict["label"] = label
        self._config_dict["height"] = height

    @property
    def value(self) -> Any:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: Any) -> None:
        self._config_dict["value"] = v
        self._sync()

    def _render(self) -> str:
        digits = self._config_dict.get("digits", 4)
        val = self._config_dict.get("value", 0)
        color = self._config_dict.get("color", "green")
        label = self._config_dict.get("label", "")
        height = self._config_dict.get("height", 32)
        style = self._render_style()
        disp = str(val).rjust(digits, "0")[:digits]
        font_size = max(12, height - 10)
        padt = (height - font_size) // 2
        lbl_html = f'<div class="iskg-led-label">{label}</div>' if label else ""
        return f'''<div id="{self._id}" class="iskg-led-wrap" style="{style}">
  {lbl_html}
  <div class="iskg-led-digits iskg-led-{color}" style="font-size:{font_size}px;height:{height}px;line-height:{height - padt * 2}px;padding:{padt}px 8px;">
    {disp}
  </div>
</div>'''

    def _render_update_js(self) -> str:
        digits = self._config_dict.get("digits", 4)
        val = self._config_dict.get("value", 0)
        disp = str(val).rjust(digits, "0")[:digits]
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-led-digits").innerText="{disp}";'''


class IndicatorLED(Widget):
    """A small colored indicator light."""

    def __init__(
        self,
        parent: Widget | None = None,
        color: str = "green",
        size: int = 8,
        active: bool = True,
        label: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["color"] = color
        self._config_dict["size"] = size
        self._config_dict["active"] = active
        self._config_dict["label"] = label

    @property
    def active(self) -> bool:
        return self._config_dict.get("active", True)

    @active.setter
    def active(self, v: bool) -> None:
        self._config_dict["active"] = bool(v)
        self._sync()

    def _render(self) -> str:
        size = self._config_dict.get("size", 8)
        color = self._config_dict.get("color", "green")
        active = self._config_dict.get("active", True)
        label = self._config_dict.get("label", "")
        style = self._render_style()
        col_map = {
            "green": "#4ade80",
            "red": "#ef4444",
            "amber": "#f59e0b",
            "cyan": "#22d3ee",
            "blue": "#60a5fa",
        }
        col = col_map.get(color, "#4ade80")
        on_cls = "iskg-indicator-on" if active else "iskg-indicator-off"
        shadow = f"0 0 {size}px {col}" if active else "none"
        lbl_html = f'<span class="iskg-indicator-label">{label}</span>' if label else ""
        return f'''<div id="{self._id}" class="iskg-indicator" style="{style}">
  <span class="iskg-indicator-dot {on_cls}" style="width:{size}px;height:{size}px;background:{col};box-shadow:{shadow};"></span>
  {lbl_html}
</div>'''

    def _render_update_js(self) -> str:
        active = self._config_dict.get("active", True)
        on_cls = "iskg-indicator-on" if active else "iskg-indicator-off"
        return f'''var el=document.getElementById("{self._id}");
if(el){{var d=el.querySelector(".iskg-indicator-dot");
d.className="iskg-indicator-dot {on_cls}";}}'''


class RadialGauge(Widget):
    """A radial gauge dial for displaying values."""

    def __init__(
        self,
        parent: Widget | None = None,
        from_: int = 0,
        to: int = 100,
        value: float = 50,
        size: int = 100,
        label: str = "",
        units: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["size"] = size
        self._config_dict["label"] = label
        self._config_dict["units"] = units

    @property
    def value(self) -> float:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: float) -> None:
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self) -> str:
        size = self._config_dict.get("size", 100)
        label = self._config_dict.get("label", "")
        units = self._config_dict.get("units", "")
        style = self._render_style()
        lbl_html = (
            f'<div class="iskg-gauge-label">{label}{" " + units if units else ""}</div>'
            if label or units
            else ""
        )
        return f'''<div id="{self._id}" class="iskg-gauge-wrap" style="{style}width:{size}px;">
  <canvas id="{self._id}-cv" class="iskg-gauge-canvas" width="{size}" height="{size + 20}"></canvas>
  {lbl_html}
</div>'''

    def _render_js(self) -> str:
        size = self._config_dict.get("size", 100)
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 50)
        cx, cy = size // 2, size // 2 + 5
        r = cx - 10
        return f'''(function(){{
  var cv=document.getElementById("{self._id}-cv");
  var ctx=cv.getContext("2d");
  var cx={cx},cy={cy},r={r},lo={lo},hi={hi},val={val};
  var arcStart=135,arcSweep=270;
  function draw(v){{
    ctx.clearRect(0,0,cv.width,cv.height);
    var p=(v-lo)/(hi-lo);
    var endA=arcStart+p*arcSweep;
    ctx.strokeStyle="#1a2636"; ctx.lineWidth=12;
    ctx.beginPath();
    ctx.arc(cx,cy,r,(-arcStart-arcSweep)*Math.PI/180,-arcStart*Math.PI/180);
    ctx.stroke();
    var grad=ctx.createLinearGradient(0,0,cv.width,0);
    grad.addColorStop(0,"#4ade80"); grad.addColorStop(0.5,"#f59e0b"); grad.addColorStop(1,"#ef4444");
    ctx.strokeStyle=grad; ctx.lineWidth=10;
    ctx.shadowColor="#22d3ee"; ctx.shadowBlur=8;
    ctx.beginPath();
    ctx.arc(cx,cy,r,-endA*Math.PI/180,-arcStart*Math.PI/180);
    ctx.stroke();
    ctx.shadowBlur=0;
    for(var i=0;i<=10;i++){{
      var a=(arcStart+i/10*arcSweep)*Math.PI/180;
      var len=i%5==0?8:4;
      ctx.strokeStyle=i%5==0?"#c8d6e5":"#4a5a6a";
      ctx.lineWidth=i%5==0?1.5:1;
      ctx.beginPath();
      ctx.moveTo(cx+(r-2)*Math.cos(-a),cy+(r-2)*Math.sin(-a));
      ctx.lineTo(cx+(r-len)*Math.cos(-a),cy+(r-len)*Math.sin(-a));
      ctx.stroke();
    }}
    ctx.fillStyle="#c8d6e5";
    ctx.font="bold "+Math.round({size}/8)+"px 'Share Tech Mono',monospace";
    ctx.textAlign="center"; ctx.textBaseline="middle";
    ctx.fillText(Math.round(v),cx,cy+r*0.6);
  }}
  draw(val);
  window.iskg_gauge_{self._id}=draw;
}})();'''

    def _render_update_js(self) -> str:
        val = self._config_dict.get("value", 0)
        return f"var fn=window.iskg_gauge_{self._id};if(fn)fn({val});"


class StatusBar(Widget):
    """A status bar with multiple sections."""

    def __init__(
        self,
        parent: Widget | None = None,
        sections: list | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["sections"] = sections or []

    def _render(self) -> str:
        sections = self._config_dict.get("sections", [])
        style = self._render_style()
        parts = []
        for sec in sections:
            if isinstance(sec, dict):
                text = sec.get("text", "")
                color = sec.get("color", "")
                style_attr = f"color:var(--{color})" if color else ""
                parts.append(
                    f'<span class="iskg-statusbar-section" style="{style_attr}">{text}</span>'
                )
            else:
                parts.append(f'<span class="iskg-statusbar-section">{sec}</span>')
        inner = "".join(parts)
        return f'''<div id="{self._id}" class="iskg-statusbar" style="{style}">
  {inner}
</div>'''

    def _render_update_js(self) -> str:
        return ""


class IconLabel(Widget):
    """A label with an inline icon."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        icon: str = "",
        icon_size: int = 14,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["icon"] = icon
        self._config_dict["icon_size"] = icon_size

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        icon = self._config_dict.get("icon", "")
        icon_size = self._config_dict.get("icon_size", 14)
        style = self._render_style()
        icon_html = ""
        if icon:
            if icon.startswith("<"):
                icon_html = f'<span class="iskg-icon" style="width:{icon_size}px;height:{icon_size}px;">{icon}</span>'
            else:
                icon_html = f'<span class="iskg-icon" style="font-size:{icon_size}px;width:{icon_size}px;height:{icon_size}px;">{icon}</span>'
        return f'''<span id="{self._id}" class="iskg-iconlabel" style="{style}">
  {icon_html}
  <span>{text}</span>
</span>'''


class ImageBox(Widget):
    """A widget that displays an image."""

    def __init__(
        self,
        parent: Widget | None = None,
        src: str = "",
        width: int = 100,
        height: int = 100,
        fit: str = "contain",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["src"] = src
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["fit"] = fit

    def _render(self) -> str:
        src = self._config_dict.get("src", "")
        width = self._config_dict.get("width", 100)
        height = self._config_dict.get("height", 100)
        fit = self._config_dict.get("fit", "contain")
        style = self._render_style()
        return f'''<div id="{self._id}" class="iskg-imagebox" style="{style}width:{width}px;height:{height}px;">
  <img src="{src}" style="object-fit:{fit};"/>
</div>'''
