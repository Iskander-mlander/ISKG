from __future__ import annotations

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

    def insert(self, idx: int, item: str) -> None:
        items = self._config_dict["items"]
        items.insert(idx, item)
        self._sync()

    def append(self, item: str) -> None:
        self._config_dict["items"].append(item)
        self._sync()

    def delete(self, idx: int) -> None:
        items = self._config_dict["items"]
        if 0 <= idx < len(items):
            items.pop(idx)
            self._sync()

    def clear(self) -> None:
        self._config_dict["items"] = []
        self._sync()

    @property
    def items(self) -> list[str]:
        return self._config_dict.get("items", [])

    @items.setter
    def items(self, vals: list[str]) -> None:
        self._config_dict["items"] = list(vals)
        self._sync()

    def _render(self) -> str:
        items = self._config_dict.get("items", [])
        style = self._render_style()
        attrs = self._render_attrs()
        width = self._config_dict.get("width", 150)
        height = self._config_dict.get("height", 120)
        item_html = ""
        for i, item in enumerate(items):
            item_html += f'<div class="iskg-listbox-item" data-idx="{i}">{item}</div>'
        return f'<div id="{self._id}" class="iskg-listbox" style="{style}width:{width}px;height:{height}px;" {attrs}>{item_html}</div>'

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").addEventListener("click",function(e){{
  var item=e.target.closest(".iskg-listbox-item");
  if(item){{
    this.querySelectorAll(".iskg-listbox-item").forEach(function(x){{x.classList.remove("selected");}});
    item.classList.add("selected");
    iskg_bridge_event("{self._id}","change",item.dataset.idx);
  }}
}});'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        items = self._config_dict.get("items", [])
        escaped = json.dumps(items)
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.innerHTML={escaped}.map(function(x,i){{
  return '<div class=\"iskg-listbox-item\" data-idx=\"'+i+'\">'+x+'</div>';
}}).join("");}}'''


class DataGrid(Widget):
    """A sortable data table with columns and rows."""

    _ARIA_ROLE = "grid"

    def __init__(
        self,
        parent: Widget | None = None,
        columns: list[str] | None = None,
        rows: list[list[str]] | None = None,
        width: int = 300,
        height: int = 200,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["columns"] = columns or []
        self._config_dict["rows"] = rows or []
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    @property
    def rows(self) -> list[list[str]]:
        return self._config_dict.get("rows", [])

    @rows.setter
    def rows(self, v: list[list[str]]) -> None:
        self._config_dict["rows"] = v
        self._sync()

    def _render(self) -> str:
        cols = self._config_dict.get("columns", [])
        rows = self._config_dict.get("rows", [])
        width = self._config_dict.get("width", 300)
        height = self._config_dict.get("height", 200)
        style = self._render_style()
        attrs = self._render_attrs()
        ths = "".join(
            f'<th data-col="{i}">{c} <span class="arrow"></span></th>' for i, c in enumerate(cols)
        )
        trs = ""
        for ri, row in enumerate(rows):
            cls = "even" if ri % 2 == 0 else "odd"
            tds = "".join(f"<td>{v}</td>" for v in row)
            trs += f'<tr class="{cls}" data-row="{ri}">{tds}</tr>'
        return f'''<div id="{self._id}" class="iskg-datagrid" style="{style}width:{width}px;height:{height}px;" {attrs}>
  <table>
    <thead><tr>{ths}</tr></thead>
    <tbody>{trs}</tbody>
  </table>
</div>'''

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
        var va=a.children[i].innerText,vb=b.children[i].innerText;
        if(va<vb)return asc?-1:1;
        if(va>vb)return asc?1:-1;
        return 0;
      }});
      rows.forEach(function(r){{tbody.appendChild(r);}});
      ths.forEach(function(t){{t.querySelector(".arrow").innerText="";}});
      th.querySelector(".arrow").innerText=asc?"\\u25b2":"\\u25bc";
    }};
  }});
  el.querySelectorAll("tr").forEach(function(r){{
    r.onclick=function(){{
      el.querySelectorAll("tr.selected").forEach(function(s){{s.classList.remove("selected");}});
      this.classList.add("selected");
      iskg_bridge_event("{self._id}","select",this.dataset.row);
    }};
  }});
}})();'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        rows = self._config_dict.get("rows", [])
        trs = ""
        for ri, row in enumerate(rows):
            cls = "even" if ri % 2 == 0 else "odd"
            tds = "".join(f"<td>{v}</td>" for v in row)
            trs += f'<tr class="{cls}" data-row="{ri}">{tds}</tr>'
        escaped = json.dumps(trs)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var tb=el.querySelector("tbody");tb.innerHTML={escaped};
tb.querySelectorAll("tr").forEach(function(r){{r.onclick=function(){{
tb.querySelectorAll("tr.selected").forEach(function(s){{s.classList.remove("selected");}});
this.classList.add("selected");
iskg_bridge_event("{self._id}","select",this.dataset.row);
}};}});}}'''


class TreeView(Widget):
    """A hierarchical tree view widget."""

    _ARIA_ROLE = "tree"

    def __init__(
        self,
        parent: Widget | None = None,
        items: list | None = None,
        width: int = 200,
        height: int = 200,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["items"] = items or []
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    def _render(self) -> str:
        items = self._config_dict.get("items", [])
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 200)
        style = self._render_style()

        def render_items(items_list: list[Any], depth: int = 0) -> str:
            parts = []
            for item in items_list:
                if isinstance(item, str):
                    item = {"text": item}
                text = item.get("text", "")
                children = item.get("children", [])
                if not isinstance(children, list):
                    children = []
                open_state = item.get("open", False)
                icon = item.get("icon", "&#128193;" if children else "&#128196;")
                toggle = ""
                child_html = ""
                if children:
                    toggle = f'<span class="iskg-tree-toggle">{"&#9660;" if open_state else "&#9658;"}</span>'
                    child_html = f'<ul class="iskg-tree-children{" open" if open_state else ""}">{render_items(children, depth + 1)}</ul>'
                parts.append(f"""<li>
  <div class="iskg-tree-node">
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
