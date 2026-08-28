"""Full calendar widget (vs. DatePicker which is just a text input).

Renders an actual month grid with navigation, day selection, and
optional range mode. Inspired by Qt's ``QCalendarWidget``.
"""

from __future__ import annotations

import calendar
import contextlib
import datetime as _dt
from collections.abc import Callable
from typing import Any

from ..base import Widget


def _date_to_dict(d: _dt.date) -> dict[str, int]:
    return {"y": d.year, "m": d.month, "d": d.day}


def _dict_to_date(d: dict[str, int]) -> _dt.date:
    return _dt.date(d["y"], d["m"], d["d"])


class Calendar(Widget):
    """A full month-grid calendar widget with prev/next navigation.

    Args:
        parent: parent widget.
        date: initial date (default today).
        first_day: ``0`` = Monday, ``6`` = Sunday. Default ``0``.
        command: optional ``(date) -> None`` callback fired on day
            click.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        date: _dt.date | None = None,
        first_day: int = 0,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["date"] = date or _dt.date.today()
        self._config_dict["view_year"] = (date or _dt.date.today()).year
        self._config_dict["view_month"] = (date or _dt.date.today()).month
        self._config_dict["first_day"] = first_day
        if command is not None:
            self._config_dict["command"] = command

    @property
    def date(self) -> _dt.date:
        d = self._config_dict.get("date")
        if isinstance(d, dict):
            return _dict_to_date(d)
        if isinstance(d, _dt.date):
            return d
        # Fallback: today.
        return _dt.date.today()

    @date.setter
    def date(self, v: _dt.date) -> None:
        self._config_dict["date"] = v
        self._config_dict["view_year"] = v.year
        self._config_dict["view_month"] = v.month
        self._sync()

    def next_month(self) -> None:
        y, m = self._config_dict["view_year"], self._config_dict["view_month"]
        if m == 12:
            self._config_dict["view_year"] = y + 1
            self._config_dict["view_month"] = 1
        else:
            self._config_dict["view_month"] = m + 1
        self._sync()

    def prev_month(self) -> None:
        y, m = self._config_dict["view_year"], self._config_dict["view_month"]
        if m == 1:
            self._config_dict["view_year"] = y - 1
            self._config_dict["view_month"] = 12
        else:
            self._config_dict["view_month"] = m - 1
        self._sync()

    def next_year(self) -> None:
        self._config_dict["view_year"] += 1
        self._sync()

    def prev_year(self) -> None:
        self._config_dict["view_year"] -= 1
        self._sync()

    def _render(self) -> str:
        y = self._config_dict["view_year"]
        m = self._config_dict["view_month"]
        first_day = self._config_dict["first_day"]
        sel = self.date
        attrs = self._render_attrs()
        cal = calendar.Calendar(firstweekday=first_day)
        weeks = list(cal.monthdayscalendar(y, m))
        # Day-of-week headers, starting from first_day
        dow_names = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        headers = "".join(
            f'<div class="iskg-cal-dow">{dow_names[(first_day + i) % 7]}</div>' for i in range(7)
        )
        cells = ""
        for week in weeks:
            for i, d in enumerate(week):
                if d == 0:
                    cells += '<div class="iskg-cal-day empty"></div>'
                    continue
                cls = "iskg-cal-day"
                if (y, m, d) == (sel.year, sel.month, sel.day):
                    cls += " selected"
                elif (i == 5) or (i == 6):
                    cls += " weekend"
                cells += f'<div class="{cls}" data-day="{d}">{d}</div>'
        month_name = [
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
        ][m - 1]
        return (
            f'<div id="{self._id}" class="iskg-calendar" {attrs}>'
            f'<div class="iskg-cal-head">'
            f'<button class="iskg-cal-prev-y">\u00ab</button>'
            f'<button class="iskg-cal-prev">\u2039</button>'
            f'<span class="iskg-cal-title">{month_name} {y}</span>'
            f'<button class="iskg-cal-next">\u203a</button>'
            f'<button class="iskg-cal-next-y">\u00bb</button>'
            f"</div>"
            f'<div class="iskg-cal-grid">{headers}{cells}</div>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  function send(action){{iskg_bridge_event("{self._id}",action,"");}}
  el.querySelector(".iskg-cal-prev").onclick=function(){{send("prev");}};
  el.querySelector(".iskg-cal-next").onclick=function(){{send("next");}};
  el.querySelector(".iskg-cal-prev-y").onclick=function(){{send("prev_year");}};
  el.querySelector(".iskg-cal-next-y").onclick=function(){{send("next_year");}};
  el.querySelectorAll(".iskg-cal-day:not(.empty)").forEach(function(d){{
    d.onclick=function(){{
      el.querySelectorAll(".iskg-cal-day.selected").forEach(function(s){{s.classList.remove("selected");}});
      this.classList.add("selected");
      iskg_bridge_event("{self._id}","select",this.dataset.day);
    }};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "prev":
            self.prev_month()
        elif event_name == "next":
            self.next_month()
        elif event_name == "prev_year":
            self.prev_year()
        elif event_name == "next_year":
            self.next_year()
        elif event_name == "select":
            try:
                day = int(event_data)
                y, m = self._config_dict["view_year"], self._config_dict["view_month"]
                new = _dt.date(y, m, day)
                self._config_dict["date"] = new
                cmd = self._config_dict.get("command")
                if cmd is not None:
                    with contextlib.suppress(Exception):
                        cmd(new)
                self._sync()
            except (ValueError, TypeError):
                pass
        else:
            super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        y = self._config_dict["view_year"]
        m = self._config_dict["view_month"]
        sel_y = self.date.year
        sel_m = self.date.month
        sel_d = self.date.day
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.querySelector(".iskg-cal-title").innerText=["January","February","March","April","May","June","July","August","September","October","November","December"][{m - 1}]+" "+{y};
el.querySelectorAll(".iskg-cal-day").forEach(function(d){{
  d.classList.toggle("selected",parseInt(d.dataset.day)===parseInt({sel_d})&&{y}==={sel_y}&&{m}==={sel_m});
}});}}'''


class TimePicker(Widget):
    """Spinbox-style hour/minute/second time picker.

    Args:
        parent: parent widget.
        time: initial time (default ``now``).
        show_seconds: if ``True`` show seconds field.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        time: _dt.time | None = None,
        show_seconds: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["time"] = time or _dt.datetime.now().time()
        self._config_dict["show_seconds"] = show_seconds

    @property
    def time(self) -> _dt.time:
        t = self._config_dict.get("time")
        if isinstance(t, _dt.time):
            return t
        return _dt.datetime.now().time()

    @time.setter
    def time(self, v: _dt.time) -> None:
        self._config_dict["time"] = v
        self._sync()

    def _render(self) -> str:
        t = self._config_dict.get("time", _dt.time(0, 0))
        show_s = self._config_dict.get("show_seconds", True)
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-timepicker" {attrs}>'
            f'<input class="iskg-tp-hour" type="number" min="0" max="23" value="{t.hour}" />'
            f"<span>:</span>"
            f'<input class="iskg-tp-min" type="number" min="0" max="59" value="{t.minute}" />'
            + (
                f"<span>:</span>"
                f'<input class="iskg-tp-sec" type="number" min="0" max="59" value="{t.second}" />'
                if show_s
                else ""
            )
            + "</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  function commit(){{
    var h=parseInt(el.querySelector(".iskg-tp-hour").value)||0;
    var m=parseInt(el.querySelector(".iskg-tp-min").value)||0;
    var s=parseInt((el.querySelector(".iskg-tp-sec")||{{value:0}}).value)||0;
    iskg_bridge_event("{self._id}","change",h+","+m+","+s);
  }}
  el.querySelectorAll("input").forEach(function(i){{i.onchange=commit;}});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            try:
                h, m, s = (int(x) for x in str(event_data).split(","))
                self._config_dict["time"] = _dt.time(h, m, s)
                self._sync()
            except (ValueError, TypeError):
                pass
        else:
            super()._handle_bridge_event(event_name, event_data)


class DateTimePicker(Widget):
    """Combined date and time picker."""

    def __init__(
        self,
        parent: Widget | None = None,
        datetime: _dt.datetime | None = None,
        show_seconds: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["datetime"] = datetime or _dt.datetime.now()
        self._config_dict["show_seconds"] = show_seconds

    @property
    def datetime(self) -> _dt.datetime:
        d = self._config_dict.get("datetime")
        if isinstance(d, _dt.datetime):
            return d
        return _dt.datetime.now()

    @datetime.setter
    def datetime(self, v: _dt.datetime) -> None:
        self._config_dict["datetime"] = v
        self._sync()

    def _render(self) -> str:
        from ._datetime import DatePicker

        date_widget = DatePicker(date=self.datetime.date())
        time_widget = TimePicker(
            time=self.datetime.time(),
            show_seconds=self._config_dict.get("show_seconds", True),
        )
        return (
            f'<div id="{self._id}" class="iskg-datetimepicker" '
            f"{self._render_attrs()}>"
            f'<div class="iskg-dtp-date">{date_widget._render()}</div>'
            f'<div class="iskg-dtp-time">{time_widget._render()}</div>'
            f"</div>"
        )
