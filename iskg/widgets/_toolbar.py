"""Toolbar (movable, customizable), MDI subwindows, SystemTray, and UndoStack.

- :class:`ToolBar` — horizontal toolbar with toggleable buttons.
- :class:`MdiArea` — multi-document interface (overlapping subwindows).
- :class:`MdiSubWindow` — a movable/closable child window.
- :class:`SystemTray` — a notification-area icon with menu.
- :class:`UndoStack` / :class:`UndoCommand` — QUndoStack-style undo/redo.
"""

from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import Any

from ..base import Widget

# ─── ToolBar ────────────────────────────────────────────────────────────


class ToolBar(Widget):
    """A horizontal toolbar with toggleable buttons.

    Buttons are registered with :meth:`add_action` and emitted as
    ``"action"`` events. The toolbar can be made floatable.

    Args:
        parent: parent widget.
        floating: if ``True`` the toolbar can be dragged free.
        command: optional callback ``(action_id) -> None``.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        floating: bool = False,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["floating"] = floating
        self._config_dict["active_id"] = ""
        self._actions: list[dict] = []
        if command is not None:
            self._config_dict["command"] = command

    def add_action(
        self,
        id: str,
        label: str,
        *,
        icon: str = "",
        checkable: bool = False,
        tooltip: str = "",
    ) -> None:
        """Add a button. ``id`` is the unique key emitted on click."""
        self._actions.append(
            {
                "id": id,
                "label": label,
                "icon": icon,
                "checkable": checkable,
                "tooltip": tooltip,
            }
        )
        self._sync()

    def add_separator(self) -> None:
        self._actions.append({"separator": True})
        self._sync()

    def set_active(self, id: str) -> None:
        """Set the currently-checked action (radio-style)."""
        self._config_dict["active_id"] = id
        self._sync()

    def clear(self) -> None:
        self._actions.clear()
        self._config_dict["active_id"] = ""
        self._sync()

    def _render(self) -> str:
        attrs = self._render_attrs()
        parts: list[str] = []
        for a in self._actions:
            if a.get("separator"):
                parts.append('<span class="iskg-toolbar-sep"></span>')
                continue
            cls = "iskg-toolbar-btn"
            if a.get("checkable") and self._config_dict.get("active_id") == a["id"]:
                cls += " active"
            tt = f' title="{a.get("tooltip", "")}"' if a.get("tooltip") else ""
            ico = f'<span class="iskg-toolbar-ico">{a["icon"]}</span>' if a.get("icon") else ""
            parts.append(
                f'<button class="{cls}" data-id="{a["id"]}"{tt}>{ico}'
                f'<span class="iskg-toolbar-lbl">{a["label"]}</span></button>'
            )
        return f'<div id="{self._id}" class="iskg-toolbar" {attrs}>' + "".join(parts) + "</div>"

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  el.querySelectorAll(".iskg-toolbar-btn").forEach(function(b){{
    b.onclick=function(){{
      var id=b.dataset.id;
      iskg_bridge_event("{self._id}","action",id);
    }};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "action":
            aid = str(event_data or "")
            self._config_dict["active_id"] = aid
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(aid)
            self._sync()
        else:
            super()._handle_bridge_event(event_name, event_data)


# ─── MDI (Multi-Document Interface) ─────────────────────────────────────


class MdiSubWindow(Widget):
    """A movable, resizable, closable subwindow inside an :class:`MdiArea`.

    Args:
        parent: the parent :class:`MdiArea`.
        title: title-bar text.
        content: child widget shown inside the subwindow body.
        x, y: initial position in px (relative to the MDI area).
        width, height: initial size in px.
        closable: if ``True`` a × button is shown.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        title: str = "SubWindow",
        content: Widget | None = None,
        x: int = 40,
        y: int = 40,
        width: int = 360,
        height: int = 240,
        closable: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["title"] = title
        self._config_dict["x"] = x
        self._config_dict["y"] = y
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["closable"] = closable
        self._config_dict["open"] = True
        self._content = content
        if content is not None:
            content._parent = self

    @property
    def title(self) -> str:
        return self._config_dict.get("title", "")

    @title.setter
    def title(self, v: str) -> None:
        self._config_dict["title"] = str(v)
        self._sync()

    def close(self) -> None:
        self._config_dict["open"] = False
        self._sync()

    def _render(self) -> str:
        title = self._config_dict.get("title", "")
        x, y = self._config_dict.get("x", 0), self._config_dict.get("y", 0)
        w, h = self._config_dict.get("width", 360), self._config_dict.get("height", 240)
        attrs = self._render_attrs()
        display = "block" if self._config_dict.get("open", True) else "none"
        closable = self._config_dict.get("closable", True)
        close_btn = '<span class="iskg-mdi-close">\u2715</span>' if closable else ""
        body = self._content._render() if self._content is not None else ""
        return (
            f'<div id="{self._id}" class="iskg-mdi-sub" '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:{display};" {attrs}>'
            f'<div class="iskg-mdi-titlebar">'
            f'<span class="title">{title}</span>{close_btn}</div>'
            f'<div class="iskg-mdi-body">{body}</div>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  var bar=el.querySelector(".iskg-mdi-titlebar");
  var close=el.querySelector(".iskg-mdi-close");
  if(bar){{
    var dragging=false, ox=0, oy=0;
    bar.onmousedown=function(e){{
      dragging=true;ox=e.clientX-parseInt(el.style.left);oy=e.clientY-parseInt(el.style.top);
      document.body.style.userSelect="none";
    }};
    document.addEventListener("mousemove",function(e){{
      if(dragging){{el.style.left=(e.clientX-ox)+"px";el.style.top=(e.clientY-oy)+"px";
        iskg_bridge_event("{self._id}","move",e.clientX-ox+","+e.clientY-oy);}}
    }});
    document.addEventListener("mouseup",function(){{dragging=false;document.body.style.userSelect="";}});
  }}
  if(close)close.onclick=function(){{iskg_bridge_event("{self._id}","close","");}};
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "close":
            self.close()
        elif event_name == "move":
            try:
                x, y = (int(v) for v in str(event_data).split(","))
                self._config_dict["x"] = x
                self._config_dict["y"] = y
            except (ValueError, TypeError):
                pass
        else:
            super()._handle_bridge_event(event_name, event_data)


class MdiArea(Widget):
    """An area containing movable :class:`MdiSubWindow` children.

    Args:
        parent: parent widget.
        command: optional ``(action, subwindow_id) -> None`` callback
            fired on close events.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._subs: list[MdiSubWindow] = []
        if command is not None:
            self._config_dict["command"] = command

    def add_subwindow(self, sub: MdiSubWindow) -> MdiSubWindow:
        sub._parent = self
        self._subs.append(sub)
        self._sync()
        return sub

    def close_all(self) -> None:
        for s in self._subs:
            s.close()
        self._sync()

    def tile(self) -> None:
        n = len(self._subs)
        if n == 0:
            return
        cols = 1
        while cols * cols < n:
            cols += 1
        rows = (n + cols - 1) // cols
        w = self._config_dict.get("width", 600) // cols
        h = self._config_dict.get("height", 400) // rows
        for i, s in enumerate(self._subs):
            r, c = i // cols, i % cols
            s._config_dict["x"] = c * w
            s._config_dict["y"] = r * h
            s._config_dict["width"] = w
            s._config_dict["height"] = h
        self._sync()

    def cascade(self) -> None:
        for i, s in enumerate(self._subs):
            s._config_dict["x"] = 20 + i * 24
            s._config_dict["y"] = 20 + i * 24
        self._sync()

    def _render(self) -> str:
        attrs = self._render_attrs()
        subs_html = "".join(s._render() for s in self._subs)
        return f'<div id="{self._id}" class="iskg-mdi-area" {attrs}>{subs_html}</div>'

    def _render_js(self) -> str:
        # Sub-windows render their own JS already.
        return ""

    def _render_update_js(self) -> str:
        return ""


# ─── SystemTray (notification-area icon) ───────────────────────────────


class SystemTray:
    """Application notification-area / system-tray icon.

    Usage::

        tray = SystemTray(app, "MyApp", icon="")
        tray.set_tooltip("MyApp is running")
        tray.notify("Hello", "World")
    """

    def __init__(self, app: Any, name: str, icon: str = "") -> None:
        self.app = app
        self.name = name
        self._icon = icon
        self._tooltip = name
        self._menu_items: list[dict] = []

    def set_icon(self, icon: str) -> None:
        self._icon = icon

    def set_tooltip(self, text: str) -> None:
        self._tooltip = text

    def add_menu_item(self, label: str, callback: Callable) -> None:
        self._menu_items.append({"label": label, "callback": callback})

    def show(self) -> None:
        """Inject the tray icon into the running window."""
        items_js = json.dumps(
            [
                {
                    "label": item["label"],
                    "id": f"tray-{i}",
                }
                for i, item in enumerate(self._menu_items)
            ]
        )
        js = f"""
(function(){{
  var t=document.createElement('div');
  t.id='iskg-tray-{id(self)}';
  t.className='iskg-tray';
  t.innerHTML='<span class="iskg-tray-icon">{self._icon or "●"}</span><span class="iskg-tray-tooltip">{self._tooltip}</span>';
  t.oncontextmenu=function(e){{
    e.preventDefault();
    iskg_open_contextmenu(t.id, {items_js});
  }};
  t.onclick=function(){{iskg_bridge_event('iskg-tray-{id(self)}', 'click', '');}};
  document.body.appendChild(t);
}})();
"""
        self.app.inject_js(js)

    def hide(self) -> None:
        self.app.execute_js(
            f"var t=document.getElementById('iskg-tray-{id(self)}');if(t)t.remove();"
        )

    def notify(self, title: str, message: str) -> None:
        self.app.execute_js(
            f"if(window.Notification)new Notification({json.dumps(title)},"
            f"{{body:{json.dumps(message)}}})"
        )


# ─── Undo/Redo ──────────────────────────────────────────────────────────


class UndoCommand:
    """Base class for undoable actions (Qt ``QUndoCommand`` equivalent).

    Subclasses should override :meth:`undo` and :meth:`redo`.
    """

    def __init__(self, text: str = "") -> None:
        self._text = text
        self._undone = False

    @property
    def text(self) -> str:
        return self._text

    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        raise NotImplementedError


class SetAttrCommand(UndoCommand):
    """Convenience command to undo/redo a single attribute set."""

    def __init__(self, widget: Any, attr: str, new_value: Any) -> None:
        super().__init__(f"Set {attr}")
        self._widget = widget
        self._attr = attr
        self._new = new_value
        self._old = getattr(widget, attr, None)

    def undo(self) -> None:
        setattr(self._widget, self._attr, self._old)

    def redo(self) -> None:
        setattr(self._widget, self._attr, self._new)


class UndoStack:
    """A stack of :class:`UndoCommand` instances with undo/redo.

    Example::

        stack = UndoStack()
        stack.push(SetAttrCommand(entry, "text", "new"))
        stack.undo()  # restores old text
        stack.redo()
    """

    def __init__(self) -> None:
        self._undo: list[UndoCommand] = []
        self._redo: list[UndoCommand] = []
        self._on_change: Callable[[UndoStack], None] | None = None

    def push(self, command: UndoCommand) -> None:
        if self._redo:
            self._redo.clear()
        self._undo.append(command)
        command.redo()
        self._emit()

    def undo(self) -> bool:
        if not self._undo:
            return False
        cmd = self._undo.pop()
        cmd.undo()
        self._redo.append(cmd)
        self._emit()
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        cmd = self._redo.pop()
        cmd.redo()
        self._undo.append(cmd)
        self._emit()
        return True

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()
        self._emit()

    def on_change(self, callback: Callable[[UndoStack], None]) -> None:
        self._on_change = callback

    def _emit(self) -> None:
        if self._on_change is not None:
            with contextlib.suppress(Exception):
                self._on_change(self)

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    @property
    def undo_text(self) -> str:
        return self._undo[-1].text if self._undo else ""

    @property
    def redo_text(self) -> str:
        return self._redo[-1].text if self._redo else ""
