from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import Any

from ..base import Widget


class ListBox(Widget):
    """A selectable list of items."""

    _ARIA_ROLE = "listbox"

    def __init__(
        self,
        parent: Widget | None = None,
        items: list[str] | None = None,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["items"] = items or []
        self._config_dict["selected_index"] = -1
        if command is not None:
            self._config_dict["command"] = command

    def insert(self, idx: int, item: str) -> None:
        items = self._config_dict["items"]
        items.insert(idx, item)
        sel = self._config_dict.get("selected_index", -1)
        if idx <= sel:
            self._config_dict["selected_index"] = sel + 1
        self._sync()

    def append(self, item: str) -> None:
        self._config_dict["items"].append(item)
        self._sync()

    def delete(self, idx: int) -> None:
        items = self._config_dict["items"]
        if 0 <= idx < len(items):
            items.pop(idx)
            sel = self._config_dict.get("selected_index", -1)
            if idx < sel:
                self._config_dict["selected_index"] = sel - 1
            elif idx == sel:
                self._config_dict["selected_index"] = -1
            self._sync()

    def clear(self) -> None:
        self._config_dict["items"] = []
        self._config_dict["selected_index"] = -1
        self._sync()

    @property
    def items(self) -> list[str]:
        return self._config_dict.get("items", [])

    @items.setter
    def items(self, vals: list[str]) -> None:
        self._config_dict["items"] = list(vals)
        self._config_dict["selected_index"] = -1
        self._sync()

    @property
    def selected_index(self) -> int:
        return self._config_dict.get("selected_index", -1)

    @selected_index.setter
    def selected_index(self, idx: int) -> None:
        if -1 <= idx < len(self._config_dict.get("items", [])):
            self._config_dict["selected_index"] = int(idx)
            self._sync()

    @property
    def enabled(self) -> bool:
        return not self._config_dict.get("disabled", False)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_state("normal" if value else "disabled")

    def _render(self) -> str:
        items = self._config_dict.get("items", [])
        sel = self._config_dict.get("selected_index", -1)
        style = self._render_style()
        attrs = self._render_attrs()
        width = self._config_dict.get("width", 150)
        height = self._config_dict.get("height", 120)
        item_html = ""
        for i, item in enumerate(items):
            cls = "iskg-listbox-item selected" if i == sel else "iskg-listbox-item"
            item_html += f'<div class="{cls}" data-idx="{i}">{item}</div>'
        return f'<div id="{self._id}" class="iskg-listbox" style="{style}width:{width}px;height:{height}px;" {attrs}>{item_html}</div>'

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").addEventListener("click",function(e){{
  var item=e.target.closest(".iskg-listbox-item");
  if(item){{
    this.querySelectorAll(".iskg-listbox-item").forEach(function(x){{x.classList.remove("selected");}});
    item.classList.add("selected");
    var idx=item.dataset.idx;
    var txt=item.innerText;
    iskg_bridge_event("{self._id}","change",idx+":"+txt);
  }}
}});'''

    def _default_takefocus(self) -> bool:
        return True

    def _handle_bridge_event(self, event_name, event_data):
        if event_name == "change":
            try:
                idx_str = str(event_data or "")
                if ":" in idx_str:
                    idx_str, _ = idx_str.split(":", 1)
                idx = int(idx_str)
                items = self._config_dict.get("items", [])
                if -1 <= idx < len(items):
                    self._config_dict["selected_index"] = idx
            except (ValueError, TypeError):
                pass
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        items = self._config_dict.get("items", [])
        sel = self._config_dict.get("selected_index", -1)
        escaped = json.dumps(items)
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.innerHTML={escaped}.map(function(x,i){{
  return '<div class=\"iskg-listbox-item'+(i==={sel}?" selected":"")+'\" data-idx="+i+'">"+x+"</div>";
}}).join("");}}'''


class DataGrid(Widget):
    """A sortable data table with typed cells.

    Each column can be typed via ``column_types`` (a list of
    ``"text"``, ``"number"``, ``"bool"``, ``"check"``, ``"choice"``,
    ``"date"``). When types are set, cells render with appropriate
    input/format and emit richer events.

    Args:
        parent: parent widget.
        columns: list of column header labels.
        column_types: list of cell types (one per column). Default: all text.
        rows: list of rows, each row is a list of cell values.
        choices: dict ``{col_index: [values]}`` for ``"choice"`` columns.
        editable: if ``True``, all cells become inline-editable. Default: ``False``.
        width: viewport width in px.
        height: viewport height in px.
        command: optional ``(row_idx, col_idx, value)`` callback.
    """

    _ARIA_ROLE = "grid"

    def __init__(
        self,
        parent: Widget | None = None,
        columns: list[str] | None = None,
        rows: list[list[str]] | None = None,
        column_types: list[str] | None = None,
        choices: dict[int, list[str]] | None = None,
        editable: bool = False,
        width: int = 300,
        height: int = 200,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["columns"] = columns or []
        self._config_dict["rows"] = rows or []
        self._config_dict["column_types"] = column_types or ["text"] * len(columns or [])
        self._config_dict["choices"] = dict(choices or {})
        self._config_dict["editable"] = editable
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["selected_row"] = -1
        self._config_dict["selected_col"] = -1
        if command is not None:
            self._config_dict["command"] = command

    @property
    def columns(self) -> list[str]:
        return self._config_dict.get("columns", [])

    @columns.setter
    def columns(self, v: list[str]) -> None:
        self._config_dict["columns"] = list(v or [])
        ct = self._config_dict.get("column_types", [])
        if len(ct) < len(v):
            self._config_dict["column_types"] = ct + ["text"] * (len(v) - len(ct))
        self._config_dict["selected_row"] = -1
        self._sync()

    @property
    def column_types(self) -> list[str]:
        return list(self._config_dict.get("column_types", []))

    @column_types.setter
    def column_types(self, v: list[str]) -> None:
        self._config_dict["column_types"] = list(v or [])
        self._sync()

    @property
    def rows(self) -> list[list[str]]:
        return self._config_dict.get("rows", [])

    @rows.setter
    def rows(self, v: list[list[str]]) -> None:
        self._config_dict["rows"] = list(v or [])
        self._config_dict["selected_row"] = -1
        self._sync()

    @property
    def selected_row(self) -> int:
        return self._config_dict.get("selected_row", -1)

    @selected_row.setter
    def selected_row(self, idx: int) -> None:
        if -1 <= idx < len(self._config_dict.get("rows", [])):
            self._config_dict["selected_row"] = int(idx)
            self._sync()

    @property
    def selected_col(self) -> int:
        return self._config_dict.get("selected_col", -1)

    @selected_col.setter
    def selected_col(self, idx: int) -> None:
        self._config_dict["selected_col"] = int(idx)
        self._sync()

    @property
    def editable(self) -> bool:
        return self._config_dict.get("editable", False)

    @editable.setter
    def editable(self, v: bool) -> None:
        self._config_dict["editable"] = bool(v)
        self._sync()

    @property
    def choices(self) -> dict[int, list[str]]:
        return dict(self._config_dict.get("choices", {}))

    @choices.setter
    def choices(self, v: dict[int, list[str]]) -> None:
        self._config_dict["choices"] = dict(v or {})
        self._sync()

    def append_row(self, row: list[str]) -> None:
        cols = self._config_dict.get("columns", [])
        if cols and len(row) < len(cols):
            row = list(row) + [""] * (len(cols) - len(row))
        self._config_dict["rows"].append(list(row))
        self._sync()

    def remove_row(self, idx: int) -> None:
        rows = self._config_dict.get("rows", [])
        if 0 <= idx < len(rows):
            rows.pop(idx)
            sel = self._config_dict.get("selected_row", -1)
            if idx < sel:
                self._config_dict["selected_row"] = sel - 1
            elif idx == sel:
                self._config_dict["selected_row"] = -1
            self._sync()

    def set_cell(self, row: int, col: int, value: str) -> None:
        rows = self._config_dict.get("rows", [])
        if 0 <= row < len(rows) and 0 <= col < len(rows[row]):
            rows[row][col] = value
            self._sync()

    def get_cell(self, row: int, col: int) -> str:
        rows = self._config_dict.get("rows", [])
        if 0 <= row < len(rows) and 0 <= col < len(rows[row]):
            return rows[row][col]
        return ""

    def clear(self) -> None:
        self._config_dict["rows"] = []
        self._config_dict["selected_row"] = -1
        self._config_dict["selected_col"] = -1
        self._sync()

    @property
    def enabled(self) -> bool:
        return not self._config_dict.get("disabled", False)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_state("normal" if value else "disabled")

    def _format_cell(self, value: str, ctype: str) -> str:
        """Render a cell value for display in a TD (HTML-escaped)."""
        import html as _html

        v = _html.escape("" if value is None else str(value))
        if ctype == "bool":
            checked = "checked" if str(value).lower() in ("true", "1", "yes") else ""
            return (
                f'<input type="checkbox" class="iskg-dg-bool" {checked} '
                f'data-row="{{R}}" data-col="{{C}}" disabled/>'
            )
        if ctype == "check":
            checked = "checked" if str(value).lower() in ("true", "1", "yes") else ""
            return f'<span class="iskg-dg-check {checked}">\u2713</span>'
        if ctype == "number":
            return f'<span class="iskg-dg-num">{v}</span>'
        if ctype == "choice":
            return f'<span class="iskg-dg-choice">{v} \u25be</span>'
        return v

    def _render(self) -> str:
        cols = self._config_dict.get("columns", [])
        rows = self._config_dict.get("rows", [])
        ctypes = self._config_dict.get("column_types", []) or ["text"] * len(cols)
        sel_r = self._config_dict.get("selected_row", -1)
        sel_c = self._config_dict.get("selected_col", -1)
        width = self._config_dict.get("width", 300)
        height = self._config_dict.get("height", 200)
        editable = self._config_dict.get("editable", False)
        style = self._render_style()
        attrs = self._render_attrs()
        ths = "".join(
            f'<th data-col="{i}">{c} <span class="arrow"></span></th>' for i, c in enumerate(cols)
        )
        trs = ""
        for ri, row in enumerate(rows):
            tr_cls = "even" if ri % 2 == 0 else "odd"
            if ri == sel_r:
                tr_cls += " selected"
            tds = ""
            for ci, val in enumerate(row):
                ctype = ctypes[ci] if ci < len(ctypes) else "text"
                td_cls = "iskg-dg-td"
                if ri == sel_r and ci == sel_c:
                    td_cls += " focused"
                # Real row/col injected by the JS (the {R}/{C} sentinels
                # are rewritten client-side so that checkbox/choice editors
                # know which cell they belong to).
                rendered = self._format_cell(val, ctype)
                rendered = rendered.replace("{R}", str(ri)).replace("{C}", str(ci))
                tds += f'<td class="{td_cls}" data-col="{ci}">{rendered}</td>'
            trs += f'<tr class="{tr_cls}" data-row="{ri}">{tds}</tr>'
        edit_attr = "true" if editable else "false"
        return (
            f'<div id="{self._id}" class="iskg-datagrid" '
            f'data-editable="{edit_attr}" style="{style}width:{width}px;'
            f'height:{height}px;" {attrs}>'
            f"<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>"
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var ths=el.querySelectorAll("th");
  var tbody=el.querySelector("tbody");
  var sortCol=-1,asc=true;
  ths.forEach(function(th,i){{
    th.onclick=function(){{
      if(sortCol==i)asc=!asc;
      else{{sortCol=i;asc=true;}}
      var rows=Array.from(tbody.querySelectorAll("tr"));
      rows.sort(function(a,b){{
        var va=a.children[i]?a.children[i].innerText:"",
            vb=b.children[i]?b.children[i].innerText:"";
        var na=parseFloat(va), nb=parseFloat(vb);
        if(!isNaN(na)&&!isNaN(nb)&&String(na)==va&&String(nb)==vb){{return asc?na-nb:nb-na;}}
        if(va<vb)return asc?-1:1;
        if(va>vb)return asc?1:-1;
        return 0;
      }});
      rows.forEach(function(r){{tbody.appendChild(r);}});
      ths.forEach(function(t){{t.querySelector(".arrow").innerText="";}});
      th.querySelector(".arrow").innerText=asc?"\\u25b2":"\\u25bc";
    }};
  }});
  var editable=el.getAttribute("data-editable")==="true";
  el.querySelectorAll("tr").forEach(function(r){{
    r.querySelectorAll("td").forEach(function(td){{
      td.onclick=function(e){{
        e.stopPropagation();
        var row=parseInt(r.dataset.row);
        var col=parseInt(td.dataset.col);
        el.querySelectorAll("td.focused").forEach(function(c){{c.classList.remove("focused");}});
        el.querySelectorAll("tr.selected").forEach(function(s){{s.classList.remove("selected");}});
        r.classList.add("selected");
        td.classList.add("focused");
        iskg_bridge_event("{self._id}","select",row+","+col);
        if(editable&&!td.querySelector("input.iskg-dg-bool")){{
          var orig=td.innerText;
          td.innerHTML='<input type="text" class="iskg-dg-edit" value="'+orig+'"/>';
          var inp=td.querySelector("input");
          inp.focus();inp.select();
          var commit=function(){{
            var v=inp.value;
            td.innerText=v;
            iskg_bridge_event("{self._id}","celledit",row+","+col+":"+v);
          }};
          inp.onblur=commit;
          inp.onkeydown=function(ev){{
            if(ev.key==="Enter"){{commit();}}
            else if(ev.key==="Escape"){{td.innerText=orig;}}
          }};
        }}
      }};
    }});
  }});
  el.querySelectorAll(".iskg-dg-bool").forEach(function(b){{
    b.addEventListener("click",function(e){{
      e.stopPropagation();
      this.checked=!this.checked;
      var row=parseInt(b.dataset.row),col=parseInt(b.dataset.col);
      iskg_bridge_event("{self._id}","celledit",row+","+col+":"+(this.checked?"true":"false"));
    }});
  }});
}});'''

    def _default_takefocus(self) -> bool:
        return True

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "select":
            try:
                parts = str(event_data or "").split(",", 1)
                self._config_dict["selected_row"] = int(parts[0])
                if len(parts) > 1:
                    self._config_dict["selected_col"] = int(parts[1])
            except (ValueError, TypeError):
                pass
        elif event_name == "celledit":
            try:
                payload = str(event_data or "")
                coords, _, value = payload.partition(":")
                r_str, _, c_str = coords.partition(",")
                r, c = int(r_str), int(c_str)
                rows = self._config_dict.get("rows", [])
                if 0 <= r < len(rows) and 0 <= c < len(rows[r]):
                    rows[r][c] = value
                    cmd = self._config_dict.get("command")
                    if cmd is not None:
                        with contextlib.suppress(Exception):
                            cmd(r, c, value)
            except (ValueError, TypeError):
                pass
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        rows = self._config_dict.get("rows", [])
        ctypes = self._config_dict.get("column_types", []) or ["text"] * len(
            self._config_dict.get("columns", [])
        )
        sel_r = self._config_dict.get("selected_row", -1)
        sel_c = self._config_dict.get("selected_col", -1)
        trs = ""
        for ri, row in enumerate(rows):
            cls = "even" if ri % 2 == 0 else "odd"
            if ri == sel_r:
                cls += " selected"
            tds = ""
            for ci, val in enumerate(row):
                ctype = ctypes[ci] if ci < len(ctypes) else "text"
                td_cls = "iskg-dg-td"
                if ri == sel_r and ci == sel_c:
                    td_cls += " focused"
                rendered = self._format_cell(val, ctype)
                rendered = rendered.replace("{R}", str(ri)).replace("{C}", str(ci))
                tds += f'<td class="{td_cls}" data-col="{ci}">{rendered}</td>'
            trs += f'<tr class="{cls}" data-row="{ri}">{tds}</tr>'
        escaped = json.dumps(trs)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var tb=el.querySelector("tbody");tb.innerHTML={escaped};
var editable=el.getAttribute("data-editable")==="true";
el.querySelectorAll("tr").forEach(function(r){{r.querySelectorAll("td").forEach(function(td){{
td.onclick=function(e){{e.stopPropagation();
var row=parseInt(r.dataset.row);var col=parseInt(td.dataset.col);
el.querySelectorAll("td.focused").forEach(function(c){{c.classList.remove("focused");}});
el.querySelectorAll("tr.selected").forEach(function(s){{s.classList.remove("selected");}});
r.classList.add("selected");td.classList.add("focused");
iskg_bridge_event("{self._id}","select",row+","+col);
if(editable&&!td.querySelector("input.iskg-dg-bool")){{
var orig=td.innerText;td.innerHTML='<input type="text" class="iskg-dg-edit" value="'+orig+'"/>';
var inp=td.querySelector("input");inp.focus();inp.select();
var commit=function(){{var v=inp.value;td.innerText=v;
iskg_bridge_event("{self._id}","celledit",row+","+col+":"+v);}};
inp.onblur=commit;
inp.onkeydown=function(ev){{if(ev.key==="Enter")commit();else if(ev.key==="Escape")td.innerText=orig;}};
}}}};}});}});
el.querySelectorAll(".iskg-dg-bool").forEach(function(b){{
b.addEventListener("click",function(e){{e.stopPropagation();
this.checked=!this.checked;
var row=parseInt(b.dataset.row),col=parseInt(b.dataset.col);
iskg_bridge_event("{self._id}","celledit",row+","+col+":"+(this.checked?"true":"false"));
}});}});}}'''


class TreeView(Widget):
    """A hierarchical tree view widget."""

    _ARIA_ROLE = "tree"

    def __init__(
        self,
        parent: Widget | None = None,
        items: list | None = None,
        width: int = 200,
        height: int = 200,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["items"] = items or []
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["selected_path"] = ""
        if command is not None:
            self._config_dict["command"] = command

    @property
    def items(self) -> list:
        return list(self._config_dict.get("items", []))

    @items.setter
    def items(self, v: list) -> None:
        self._config_dict["items"] = list(v or [])
        self._config_dict["selected_path"] = ""
        self._sync()

    @property
    def selected_path(self) -> str:
        return self._config_dict.get("selected_path", "")

    @selected_path.setter
    def selected_path(self, v: str) -> None:
        self._config_dict["selected_path"] = str(v)
        self._sync()

    def add(self, *args, **kwargs):
        # Override Widget.add to accept either a Widget (legacy) or a
        # tree-node spec (dict/string). Use ``add_node`` for explicit
        # tree-entry addition.
        if args and isinstance(args[0], (dict, str)):
            return self.add_node(*args, **kwargs)
        return Widget.add(self, *args, **kwargs)

    def add_node(self, item, parent_path=None) -> None:
        if isinstance(item, str):
            item = {"text": item}
        item = dict(item)
        item.setdefault("text", "")
        item.setdefault("children", [])
        items = self._config_dict["items"]
        if parent_path is None:
            items.append(item)
        else:
            parent = self._find_node(items, parent_path)
            if parent is not None:
                parent.setdefault("children", []).append(item)
            else:
                items.append(item)
        self._sync()

    def remove(self, path: str) -> bool:
        items = self._config_dict["items"]
        node, parent_list = self._find_node_with_parent(items, path)
        if parent_list is not None and node is not None:
            parent_list.remove(node)
            self._sync()
            return True
        return False

    def clear(self) -> None:
        self._config_dict["items"] = []
        self._config_dict["selected_path"] = ""
        self._sync()

    def _find_node(self, items, path):
        keys = [k for k in path.split("/") if k]
        if not keys:
            return None
        for item in items:
            if item.get("text") == keys[0]:
                if len(keys) == 1:
                    return item
                return self._find_node(item.get("children", []), "/".join(keys[1:]))
        return None

    def _find_node_with_parent(self, items, path):
        keys = [k for k in path.split("/") if k]
        if not keys:
            return None, None
        for i, item in enumerate(items):
            if item.get("text") == keys[0]:
                if len(keys) == 1:
                    return item, items
                return self._find_node_with_parent(item.get("children", []), "/".join(keys[1:]))
        return None, None

    @property
    def enabled(self) -> bool:
        return not self._config_dict.get("disabled", False)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_state("normal" if value else "disabled")

    def _render(self) -> str:
        items = self._config_dict.get("items", [])
        sel = self._config_dict.get("selected_path", "")
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 200)
        style = self._render_style()

        def render_items(items_list, depth: int = 0, parent_path: str = "") -> str:
            parts = []
            for item in items_list:
                if isinstance(item, str):
                    item = {"text": item}
                text = item.get("text", "")
                children = item.get("children", [])
                if not isinstance(children, list):
                    children = []
                open_state = item.get("open", False)
                full_path = f"{parent_path}/{text}" if parent_path else text
                icon = item.get("icon", "&#128193;" if children else "&#128196;")
                toggle = ""
                child_html = ""
                if children:
                    toggle = f'<span class="iskg-tree-toggle">{"&#9660;" if open_state else "&#9658;"}</span>'
                    child_html = f'<ul class="iskg-tree-children{" open" if open_state else ""}">{render_items(children, depth + 1, full_path)}</ul>'
                is_selected = full_path == sel
                node_cls = "iskg-tree-node"
                if is_selected:
                    node_cls += " selected"
                parts.append(f"""<li>
  <div class="{node_cls}" data-path="{full_path}">
    {toggle}
    <span class="iskg-tree-icon">{icon}</span>
    <span class="iskg-tree-text">{text}</span>
  </div>
  {child_html}
</li>""")
            return "".join(parts)

        attrs = self._render_attrs()
        inner = render_items(items)
        return f'''<div id="{self._id}" class="iskg-tree" style="{style}width:{width}px;height:{height}px;" {attrs}>
  <ul>{inner}</ul>
</div>'''

    def _default_takefocus(self) -> bool:
        return True

    def _handle_bridge_event(self, event_name, event_data):
        if event_name == "select":
            self._config_dict["selected_path"] = str(event_data or "")
        super()._handle_bridge_event(event_name, event_data)

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  el.querySelectorAll(".iskg-tree-toggle").forEach(function(tog){{
    tog.onclick=function(e){{
      e.stopPropagation();
      var li=this.closest("li");
      var children=li&&li.querySelector(":scope > .iskg-tree-children");
      if(children){{
        children.classList.toggle("open");
        this.innerHTML=children.classList.contains("open")?"&#9660;":"&#9658;";
      }}
    }};
  }});
      el.querySelectorAll(".iskg-tree-node").forEach(function(node){{
        node.onclick=function(){{
          el.querySelectorAll(".iskg-tree-node.selected").forEach(function(s){{s.classList.remove("selected");}});
          this.classList.add("selected");
          var path=[];
          var cur=this;
          while(cur&&cur!=el){{
            var txt=cur.querySelector(".iskg-tree-text");
            if(txt)path.unshift(txt.innerText);
            cur=cur.parentElement?.parentElement?.parentElement?.querySelector(":scope > .iskg-tree-node")||null;
          }}
          iskg_bridge_event("{self._id}","select",path.join("/"));
        }};
      }});
}})();'''


class DropTarget(Widget):
    """A drag-and-drop target area."""

    _ARIA_ROLE = "button"

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "Drop files here",
        width: int = 200,
        height: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 100)
        style = self._render_style()
        attrs = self._render_attrs()
        return f'''<div id="{self._id}" class="iskg-droptarget" style="{style}width:{width}px;height:{height}px;" {attrs}>
  <div class="iskg-droptarget-icon">⬇</div>
  <div class="iskg-droptarget-text">{text}</div>
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  el.ondragover=function(e){{e.preventDefault();this.classList.add("dragover");}};
  el.ondragleave=function(){{this.classList.remove("dragover");}};
  el.ondrop=function(e){{
    e.preventDefault();
    this.classList.remove("dragover");
    var files=[];
    for(var i=0;i<e.dataTransfer.files.length;i++){{
      files.push(e.dataTransfer.files[i].name);
    }}
    iskg_bridge_event("{self._id}","drop",files.join(","));
  }};
}})();'''
