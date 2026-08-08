"""Clock and DatePicker widgets for HUD-style displays."""

from __future__ import annotations

import json
from datetime import date as _date
from typing import Any

from ..base import Widget

_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
_WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def _month_grid(year: int, month: int, selected_iso: str) -> str:
    """Build the day-cell grid HTML for a given month (Sunday-first)."""
    first = _date(year, month, 1)
    start = (first.weekday() + 1) % 7
    days = 31 if month == 12 else (_date(year, month + 1, 1) - _date(year, month, 1)).days
    cells = ""
    for _ in range(start):
        cells += '<span class="iskg-dp-day empty"></span>'
    for day in range(1, days + 1):
        iso = f"{year}-{month:02d}-{day:02d}"
        cls = "iskg-dp-day iskg-dp-selected" if iso == selected_iso else "iskg-dp-day"
        cells += f'<span class="{cls}" data-iso="{iso}">{day}</span>'
    wd = "".join(f'<span class="iskg-dp-dow">{w}</span>' for w in _WEEKDAYS)
    return (
        f'<div class="iskg-dp-head">'
        f'<button class="iskg-dp-nav" data-nav="-1">&#9664;</button>'
        f'<span class="iskg-dp-title">{_MONTHS[month - 1]} {year}</span>'
        f'<button class="iskg-dp-nav" data-nav="1">&#9654;</button>'
        f'</div><div class="iskg-dp-grid">{wd}{cells}</div>'
    )


class Clock(Widget):
    """A live ticking digital clock (HH:MM:SS or HH:MM).

    The clock updates itself in the browser. Optional ``command`` fires on
    every tick.

    Args:
        parent: parent widget (optional).
        seconds: show seconds (default ``True``).
        military: 24-hour format (default ``True``). ``False`` renders a
            12-hour clock with an AM/PM suffix.
        command: optional callback invoked on every tick.
        kwargs: forwarded to :class:`~iskg.base.Widget`.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        seconds: bool = True,
        military: bool = True,
        command: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["seconds"] = seconds
        self._config_dict["military"] = military
        if command is not None:
            self._config_dict["command"] = command

    def _render(self) -> str:
        style = self._render_style()
        attrs = self._render_attrs()
        return f'<span id="{self._id}" class="iskg-clock" style="{style}" {attrs}>--:--:--</span>'

    def _render_js(self) -> str:
        secs = "true" if self._config_dict.get("seconds", True) else "false"
        mil = "true" if self._config_dict.get("military", True) else "false"
        cmd = "true" if self._config_dict.get("command") else "false"
        return f"""(function(){{
var el=document.getElementById("{self._id}");
if(!el)return;
function pad(n){{return n<10?"0"+n:""+n;}}
function tick(){{
  var now=new Date();
  var h=now.getHours(), ampm="";
  if({mil}==false){{
    ampm=h<12?" AM":" PM";h=h%12;if(h==0)h=12;
  }}
  var t=pad(h)+":"+pad(now.getMinutes());
  if({secs})t+=":"+pad(now.getSeconds());
  el.innerText=t+ampm;
  if({cmd})iskg_bridge_event("{self._id}","tick",t);
}}
tick();
setInterval(tick,1000);
}})();"""


class DatePicker(Widget):
    """A compact calendar popup for selecting a date.

    Clicking the field opens a month grid with previous/next navigation;
    clicking a day updates the field and fires a ``"change"`` event with the
    ISO date string (``YYYY-MM-DD``) plus optional ``command``.

    Args:
        parent: parent widget (optional).
        width: field width in px.
        date: initial date; defaults to today.
        command: optional callback invoked on selection.
        format_: strftime-style format for the field label.
        kwargs: forwarded to :class:`~iskg.base.Widget`.
    """

    _ARIA_ROLE = "combobox"

    def __init__(
        self,
        parent: Widget | None = None,
        width: int = 120,
        date: _date | None = None,
        command: Any = None,
        format_: str = "%Y-%m-%d",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["date"] = date or _date.today()
        self._config_dict["format"] = format_
        if command is not None:
            self._config_dict["command"] = command

    @property
    def value(self) -> _date:
        """The currently selected date."""
        return self._config_dict.get("date", _date.today())

    @value.setter
    def value(self, d: _date) -> None:
        self._config_dict["date"] = d
        self._sync()

    @property
    def iso(self) -> str:
        """The selected date as an ISO string (``YYYY-MM-DD``)."""
        return self.value.isoformat()

    def _render(self) -> str:
        width = int(self._config_dict.get("width", 120))
        style = self._render_style()
        attrs = self._render_attrs()
        d = self.value
        fmt = self._config_dict.get("format", "%Y-%m-%d")
        return (
            f'<div id="{self._id}" class="iskg-datepicker" style="{style}width:{width}px;" {attrs}>'
            f'<span class="iskg-datepicker-field">{d.strftime(fmt)} &#9662;</span>'
            f'<div class="iskg-datepicker-popup" style="display:none;"></div>'
            f"</div>"
        )

    def _render_js(self) -> str:
        owner = self._id
        return f"""(function(){{\nvar el=document.getElementById("{owner}");\nif(!el)return;\nvar field=el.querySelector(".iskg-datepicker-field");\nvar popup=el.querySelector(".iskg-datepicker-popup");\nfunction placePop(){{\n  var r=el.getBoundingClientRect();\n  /* fixed positioning escapes any ancestor with overflow:hidden or a\n     stacking scope, so the calendar always overlays surrounding widgets. */\n  popup.style.position="fixed";\n  popup.style.top=(r.bottom)+"px";\n  popup.style.left=(r.left)+"px";\n}}\nfunction closePop(){{\n  popup.style.display="none";\n  popup.style.position="";popup.style.top="";popup.style.left="";\n}}\nfunction openPop(){{\n  placePop();\n  popup.style.display="block";\n  iskg_bridge_event("{owner}","open","");\n}}\nfield.onclick=function(e){{e.stopPropagation();\n  if(popup.style.display==="block"){{closePop();return;}}\n  openPop();\n}};\npopup.addEventListener("click",function(e){{\n  var nav=e.target.closest(".iskg-dp-nav");\n  if(nav){{iskg_bridge_event("{owner}","nav",nav.getAttribute("data-nav"));e.stopPropagation();return;}}\n  var day=e.target.closest(".iskg-dp-day");\n  if(day&&day.getAttribute("data-iso")){{\n    iskg_bridge_event("{owner}","select",day.getAttribute("data-iso"));\n  }}\n}});\nwindow.addEventListener("resize",function(){{if(popup.style.display==="block")placePop();}});\ndocument.addEventListener("click",function(e){{\n  if(!el.contains(e.target))closePop();\n}});\n}}());"""

    def _render_update_js(self) -> str:
        d = self.value
        fmt = self._config_dict.get("format", "%Y-%m-%d")
        return (
            f'var el=document.getElementById("{self._id}");'
            f'if(el)el.querySelector(".iskg-datepicker-field").innerText="{d.strftime(fmt)} \\u25be";'
        )

    def _apply_popup_js(self) -> str:
        d = self.value
        summary = _month_grid(d.year, d.month, d.isoformat())
        return (
            f'var el=document.getElementById("{self._id}");'
            f'if(el){{var p=el.querySelector(".iskg-datepicker-popup");'
            f"p.innerHTML={json.dumps(summary)};}}"
        )

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> str | None:
        if event_name == "open":
            if self._app and self._app._running:
                self._eval_js(self._apply_popup_js())
        elif event_name == "nav":
            if self._app and self._app._running:
                d = self.value
                delta = int(event_data or 0)
                new_index = d.month + delta
                years = d.year
                months = (new_index - 1) % 12 + 1
                years += (new_index - 1) // 12
                day = min(d.day, 28)
                try:
                    target = _date(years, months, day)
                except ValueError:
                    target = _date(years, months, 1)
                self._config_dict["date"] = target
                self._eval_js(self._apply_popup_js())
        elif event_name == "select" and self._app and self._app._running:
            from datetime import datetime

            try:
                chosen = datetime.strptime(str(event_data), "%Y-%m-%d").date()
            except ValueError:
                chosen = self.value
            self._config_dict["date"] = chosen
            self._sync()
            self._eval_js(
                f'var el=document.getElementById("{self._id}");'
                'if(el)el.querySelector(".iskg-datepicker-popup").style.display="none";'
            )
            cmd = self._config_dict.get("command")
            if cmd:
                cmd(chosen)
        return super()._handle_bridge_event(event_name, event_data)
