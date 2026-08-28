"""Property grid, command palette, markdown viewer, graphics view, undo stack.

- :class:`PropertyGrid` — wxPropertyGrid-style editor of object properties.
- :class:`CommandPalette` — VSCode-style Ctrl+Shift+P launcher.
- :class:`MarkdownViewer` — read-only Markdown renderer.
- :class:`GraphicsView` — QGraphicsView equivalent with selectable items.
"""

from __future__ import annotations

import contextlib
import html as _html
import re
from collections.abc import Callable
from typing import Any

from ..base import Widget

# ─── PropertyGrid ───────────────────────────────────────────────────────


# Map common Python types to property editors
_TYPE_EDITORS = {
    int: "int",
    float: "float",
    bool: "bool",
    str: "text",
    list: "list",
}


class PropertyGrid(Widget):
    """A grid of (name, value) rows that edit properties of an object.

    Supports a small type-driven editor set: ``int``, ``float``,
    ``bool``, ``str``, ``list``, ``choice``, ``color``.

    Args:
        parent: parent widget.
        target: the object whose attributes are edited (can be set later
            via :attr:`target`).
        properties: optional list of property names to show. If ``None``,
            every public attribute is enumerated.
        types: optional ``{name: editor_kind}`` overrides.
        choices: optional ``{name: [values]}`` for choice editors.
        command: optional ``(name, value) -> None`` callback after a
            successful edit.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        target: Any = None,
        properties: list[str] | None = None,
        types: dict[str, str] | None = None,
        choices: dict[str, list[str]] | None = None,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._target = target
        self._config_dict["properties"] = list(properties or [])
        self._config_dict["types"] = dict(types or {})
        self._config_dict["choices"] = dict(choices or {})
        if command is not None:
            self._config_dict["command"] = command

    @property
    def target(self) -> Any:
        return self._target

    @target.setter
    def target(self, v: Any) -> None:
        self._target = v
        self._sync()

    def _kind_for(self, name: str, value: Any) -> str:
        if name in self._config_dict["types"]:
            return self._config_dict["types"][name]
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "text"
        if isinstance(value, list):
            return "list"
        return "text"

    def _row_html(self, name: str, value: Any) -> str:
        kind = self._kind_for(name, value)
        if kind == "bool":
            v = "true" if value else "false"
            chk = "checked" if value else ""
            return (
                f'<div class="iskg-pg-row" data-name="{name}" data-kind="bool">'
                f'<span class="iskg-pg-name">{name}</span>'
                f'<label class="iskg-pg-bool">'
                f'<input type="checkbox" {chk}/> {v}</label></div>'
            )
        if kind == "choice":
            opts = self._config_dict["choices"].get(name, [])
            options = "".join(
                f'<option value="{o}"{"selected" if o == value else ""}>{o}</option>' for o in opts
            )
            return (
                f'<div class="iskg-pg-row" data-name="{name}" data-kind="choice">'
                f'<span class="iskg-pg-name">{name}</span>'
                f'<select class="iskg-pg-edit">{options}</select></div>'
            )
        v_str = "" if value is None else str(value)
        return (
            f'<div class="iskg-pg-row" data-name="{name}" data-kind="{kind}">'
            f'<span class="iskg-pg-name">{name}</span>'
            f'<input class="iskg-pg-edit" type="text" value="{_html.escape(v_str)}" />'
            f"</div>"
        )

    def _render(self) -> str:
        attrs = self._render_attrs()
        if self._target is None:
            return f'<div id="{self._id}" class="iskg-propertygrid" {attrs}></div>'
        props = self._config_dict.get("properties") or [
            a
            for a in dir(self._target)
            if not a.startswith("_") and not callable(getattr(self._target, a, None))
        ]
        rows = "".join(self._row_html(p, getattr(self._target, p, None)) for p in props)
        return f'<div id="{self._id}" class="iskg-propertygrid" {attrs}>{rows}</div>'

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-pg-row").forEach(function(row){{
    var name=row.dataset.name;
    var kind=row.dataset.kind;
    function commit(v){{iskg_bridge_event("{self._id}","set",name+":"+v);}}
    if(kind==="bool"){{
      var cb=row.querySelector("input");
      cb.onchange=function(){{commit(cb.checked?"true":"false");}};
    }} else if(kind==="choice"){{
      var sel=row.querySelector("select");
      sel.onchange=function(){{commit(sel.value);}};
    }} else {{
      var inp=row.querySelector(".iskg-pg-edit");
      inp.onchange=function(){{commit(inp.value);}};
    }}
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "set" and self._target is not None:
            try:
                name, _, raw = str(event_data or "").partition(":")
                if not name:
                    return
                kind = self._kind_for(name, getattr(self._target, name, None))
                # Coerce
                if kind == "int":
                    v = int(raw)
                elif kind == "float":
                    v = float(raw)
                elif kind == "bool":
                    v = raw == "true"
                else:
                    v = raw
                setattr(self._target, name, v)
                cmd = self._config_dict.get("command")
                if cmd is not None:
                    with contextlib.suppress(Exception):
                        cmd(name, v)
            except (ValueError, TypeError):
                pass
        else:
            super()._handle_bridge_event(event_name, event_data)


# ─── CommandPalette (VSCode-style) ─────────────────────────────────────


class CommandPalette(Widget):
    """A keyboard-driven command launcher (Ctrl+Shift+P style).

    Args:
        parent: parent widget.
        commands: list of ``(id, label, shortcut, callback)`` tuples.
        placeholder: input placeholder text.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        commands: list[tuple[str, str, str, Callable]] | None = None,
        placeholder: str = "Type a command…",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._commands = list(commands or [])
        self._config_dict["placeholder"] = placeholder
        self._config_dict["open"] = False
        self._config_dict["query"] = ""
        self._selected = 0

    def add_command(self, id: str, label: str, shortcut: str, callback: Callable) -> None:
        self._commands.append((id, label, shortcut, callback))
        self._sync()

    def open_palette(self) -> None:
        self._config_dict["open"] = True
        self._config_dict["query"] = ""
        self._selected = 0
        self._sync()

    def close_palette(self) -> None:
        self._config_dict["open"] = False
        self._sync()

    def _filtered(self) -> list[tuple[str, str, str, Callable]]:
        q = self._config_dict.get("query", "").lower()
        if not q:
            return list(self._commands)
        return [c for c in self._commands if q in c[1].lower() or q in c[0].lower()]

    def _render(self) -> str:
        style = self._render_style()
        attrs = self._render_attrs()
        cmds = self._filtered()
        items = "".join(
            f'<div class="iskg-cmdpalette-item{" selected" if i == self._selected else ""}" '
            f'data-idx="{i}">'
            f'<span class="iskg-cmdpalette-name">{_html.escape(c[1])}</span>'
            f'<span class="iskg-cmdpalette-sc">{_html.escape(c[2])}</span>'
            f"</div>"
            for i, c in enumerate(cmds)
        )
        if not items:
            items = '<div class="iskg-cmdpalette-item"><span>No matches</span></div>'
        display = "flex" if self._config_dict.get("open", False) else "none"
        return (
            f'<div id="{self._id}" class="iskg-cmdpalette-overlay" '
            f'style="display:{display};" {attrs}>'
            f'<div class="iskg-cmdpalette" style="{style}">'
            f'<input class="iskg-cmdpalette-input" '
            f'placeholder="{_html.escape(self._config_dict["placeholder"])}" '
            f'value="{_html.escape(self._config_dict.get("query", ""))}" />'
            f'<div class="iskg-cmdpalette-list">{items}</div>'
            f"</div></div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  var inp=el.querySelector(".iskg-cmdpalette-input");
  var list=el.querySelector(".iskg-cmdpalette-list");
  function select(idx){{
    list.querySelectorAll(".iskg-cmdpalette-item").forEach(function(it){{
      it.classList.toggle("selected",parseInt(it.dataset.idx)===idx);
    }});
  }}
  function commit(idx){{
    var item=list.querySelector('[data-idx="'+idx+'"]');
    if(item)iskg_bridge_event("{self._id}","run",String(idx));
  }}
  inp.oninput=function(){{iskg_bridge_event("{self._id}","query",inp.value);}};
  inp.onkeydown=function(e){{
    if(e.key==="ArrowDown"){{e.preventDefault();iskg_bridge_event("{self._id}","down","");}}
    else if(e.key==="ArrowUp"){{e.preventDefault();iskg_bridge_event("{self._id}","up","");}}
    else if(e.key==="Enter"){{iskg_bridge_event("{self._id}","enter","");}}
    else if(e.key==="Escape"){{iskg_bridge_event("{self._id}","close","");}}
  }};
  list.querySelectorAll(".iskg-cmdpalette-item").forEach(function(item){{
    item.onclick=function(){{commit(parseInt(item.dataset.idx));}};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "query":
            self._config_dict["query"] = str(event_data or "")
            self._selected = 0
            self._sync()
        elif event_name == "down":
            n = len(self._filtered())
            if n:
                self._selected = (self._selected + 1) % n
                self._sync()
        elif event_name == "up":
            n = len(self._filtered())
            if n:
                self._selected = (self._selected - 1) % n
                self._sync()
        elif event_name == "enter":
            cmds = self._filtered()
            if 0 <= self._selected < len(cmds):
                cb = cmds[self._selected][3]
                with contextlib.suppress(Exception):
                    cb()
                self.close_palette()
        elif event_name == "close":
            self.close_palette()
        elif event_name == "run":
            try:
                idx = int(event_data)
                cmds = self._filtered()
                if 0 <= idx < len(cmds):
                    cb = cmds[idx][3]
                    with contextlib.suppress(Exception):
                        cb()
                    self.close_palette()
            except (ValueError, TypeError):
                pass
        else:
            super()._handle_bridge_event(event_name, event_data)


# ─── MarkdownViewer ────────────────────────────────────────────────────


# Lightweight Markdown subset: headings, bold, italic, code, lists, links.
_MD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^######\s+(.+?)$", re.MULTILINE), r"<h6>\1</h6>"),
    (re.compile(r"^#####\s+(.+?)$", re.MULTILINE), r"<h5>\1</h5>"),
    (re.compile(r"^####\s+(.+?)$", re.MULTILINE), r"<h4>\1</h4>"),
    (re.compile(r"^###\s+(.+?)$", re.MULTILINE), r"<h3>\1</h3>"),
    (re.compile(r"^##\s+(.+?)$", re.MULTILINE), r"<h2>\1</h2>"),
    (re.compile(r"^#\s+(.+?)$", re.MULTILINE), r"<h1>\1</h1>"),
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"__(.+?)__"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
    (re.compile(r"^>\s+(.+?)$", re.MULTILINE), r"<blockquote>\1</blockquote>"),
    (re.compile(r"^---$", re.MULTILINE), r"<hr>"),
    (re.compile(r"^[-*]\s+(.+?)$", re.MULTILINE), r"<li>\1</li>"),
    (re.compile(r"^\d+\.\s+(.+?)$", re.MULTILINE), r"<li>\1</li>"),
]


def render_markdown(text: str) -> str:
    """Convert a small subset of Markdown to HTML.

    Supports: ATX headings (``#``-``######``), bold, italic, inline
    code, links, blockquotes, horizontal rules, and unordered/ordered
    lists. Not a full CommonMark implementation.
    """
    if not text:
        return ""
    html = _html.escape(text)
    for pat, repl in _MD_PATTERNS:
        html = pat.sub(repl, html)
    # Wrap consecutive <li> in <ul>
    html = re.sub(r"((?:<li>.*?</li>\s*)+)", r"<ul>\1</ul>", html, flags=re.DOTALL)
    # Paragraphs: split on blank lines
    parts: list[str] = []
    buf: list[str] = []
    for line in html.split("\n"):
        if not line.strip():
            if buf:
                parts.append("<p>" + " ".join(buf) + "</p>")
                buf = []
        else:
            buf.append(line)
    if buf:
        parts.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(parts)


class MarkdownViewer(Widget):
    """Read-only Markdown viewer."""

    def __init__(
        self,
        parent: Widget | None = None,
        markdown: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["markdown"] = markdown

    @property
    def markdown(self) -> str:
        return self._config_dict.get("markdown", "")

    @markdown.setter
    def markdown(self, v: str) -> None:
        self._config_dict["markdown"] = str(v)
        self._sync()

    def _render(self) -> str:
        md = self._config_dict.get("markdown", "")
        body = render_markdown(md)
        attrs = self._render_attrs()
        return f'<div id="{self._id}" class="iskg-markdown" {attrs}>{body}</div>'


# ─── GraphicsView (QGraphicsView equivalent) ───────────────────────────


class GraphicsView(Widget):
    """A canvas with positioned, hit-testable items.

    Items are dicts with ``x``, ``y``, ``w``, ``h``, ``label``,
    ``fill``, ``kind`` (``"rect"`` / ``"ellipse"`` / ``"text"``).
    Click events select items and emit ``"select"``.

    Args:
        parent: parent widget.
        width: viewport width.
        height: viewport height.
        command: optional ``(item_id) -> None`` callback.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        width: int = 400,
        height: int = 300,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["selected"] = ""
        self._items: list[dict] = []
        if command is not None:
            self._config_dict["command"] = command

    def add_item(self, **kwargs) -> str:
        """Add an item and return its id.

        Common kwargs: ``id``, ``x``, ``y``, ``w``, ``h``, ``label``,
        ``fill``, ``kind``.
        """
        item_id = kwargs.pop("id", f"item-{len(self._items)}")
        item = {"id": item_id, "kind": "rect", "fill": "var(--cyan)", **kwargs}
        self._items.append(item)
        self._sync()
        return item_id

    def remove_item(self, item_id: str) -> bool:
        for i, it in enumerate(self._items):
            if it["id"] == item_id:
                self._items.pop(i)
                self._sync()
                return True
        return False

    def clear(self) -> None:
        self._items.clear()
        self._config_dict["selected"] = ""
        self._sync()

    def _render(self) -> str:
        width = self._config_dict.get("width", 400)
        height = self._config_dict.get("height", 300)
        attrs = self._render_attrs()
        sel = self._config_dict.get("selected", "")
        items_html = ""
        for it in self._items:
            cls = "iskg-graphics-item"
            if it["id"] == sel:
                cls += " selected"
            x, y, w, h = it.get("x", 0), it.get("y", 0), it.get("w", 30), it.get("h", 30)
            kind = it.get("kind", "rect")
            label = it.get("label", it["id"])
            fill = it.get("fill", "var(--cyan)")
            if kind == "ellipse":
                body = f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" fill="{fill}" />'
            elif kind == "text":
                body = (
                    f'<text x="{x}" y="{y + h}" font-size="{int(h * 0.6)}" fill="var(--text)">'
                    f"{_html.escape(label)}</text>"
                )
            else:
                body = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" />'
            items_html += (
                f'<g class="{cls}" data-id="{it["id"]}">{body}'
                f"<title>{_html.escape(label)}</title></g>"
            )
        return (
            f'<div id="{self._id}" class="iskg-graphics" '
            f'style="width:{width}px;height:{height}px;" {attrs}>'
            f'<svg width="{width}" height="{height}">{items_html}</svg></div>'
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-graphics-item").forEach(function(g){{
    g.onclick=function(){{iskg_bridge_event("{self._id}","select",g.dataset.id);}};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "select":
            self._config_dict["selected"] = str(event_data or "")
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(self._config_dict["selected"])
            self._sync()
        else:
            super()._handle_bridge_event(event_name, event_data)
