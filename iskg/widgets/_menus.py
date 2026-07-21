from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..base import Widget


class MenuItem:
    """An item within a Menu."""

    def __init__(
        self,
        text: str,
        command: Callable | None = None,
        shortcut: str = "",
        icon: str = "",
    ) -> None:
        self.text = text
        self.command = command
        self.shortcut = shortcut
        self.icon = icon
        self.submenu: Menu | None = None


class Menu:
    """A dropdown menu for the main menu bar."""

    _counter: int = 0

    def __init__(self, text: str = "") -> None:
        Menu._counter += 1
        self._id: str = f"iskg-m{Menu._counter}"
        self.text = text
        self.items: list[MenuItem | None] = []

    def add_item(
        self,
        text: str,
        command: Callable | None = None,
        shortcut: str = "",
        icon: str = "",
    ) -> MenuItem:
        item = MenuItem(text, command, shortcut, icon)
        self.items.append(item)
        return item

    def add_separator(self) -> None:
        self.items.append(None)

    def add_menu(self, text: str) -> Menu:
        sub = Menu(text)
        item = MenuItem(text)
        item.submenu = sub
        self.items.append(item)
        return sub


class MenuBar(Widget):
    """A main menu bar with dropdown menus."""

    def __init__(
        self,
        parent: Widget | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._menus: list[Menu] = []

    def add_menu(self, text: str) -> Menu:
        m = Menu(text)
        self._menus.append(m)
        return m

    def _render_menu_dd(self, menu: Menu, top_level_text: str | None = None) -> str:
        mn_attr = f' data-mn="{top_level_text}"' if top_level_text else ""
        parts = []
        for item in menu.items:
            if item is None:
                parts.append('<div class="iskg-menu-sep"></div>')
            else:
                cls = "iskg-menu-item"
                attrs = ""
                txt = item.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                sc = f'<span class="iskg-menu-sc">{item.shortcut}</span>' if item.shortcut else ""
                ico = f'<span class="iskg-menu-ico">{item.icon}</span>' if item.icon else ""
                if item.submenu:
                    cls += " iskg-menu-sub"
                    attrs = f' data-sub="{item.submenu._id}"'
                    parts.append(
                        f'<div class="{cls}"{attrs}>{ico}<span class="iskg-menu-txt">{txt}</span>▸{sc}'
                        f"{self._render_menu_dd(item.submenu)}</div>"
                    )
                else:
                    parts.append(
                        f'<div class="{cls}" data-cmd="1">{ico}<span class="iskg-menu-txt">{txt}</span>{sc}</div>'
                    )
        return f'<div id="{menu._id}" class="iskg-menu-dd"{mn_attr}>{"".join(parts)}</div>'

    def _render(self) -> str:
        style = self._render_style()
        items_html = "".join(
            f'<div class="iskg-menubar-item" data-m="{m._id}">{m.text}</div>' for m in self._menus
        )
        dds_html = "".join(self._render_menu_dd(m, top_level_text=m.text) for m in self._menus)
        return f'<div id="{self._id}" class="iskg-menubar" style="{style}position:relative;">{items_html}{dds_html}</div>'

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var openDD=null;
  var hideTimer=null;
  function hideAll(){{
    if(hideTimer){{clearTimeout(hideTimer);hideTimer=null;}}
    el.querySelectorAll(".iskg-menu-dd").forEach(function(d){{d.style.display="none";}});
    openDD=null;
  }}
  function scheduleHide(){{
    if(hideTimer)clearTimeout(hideTimer);
    hideTimer=setTimeout(function(){{
      hideAll();
      hideTimer=null;
    }},200);
  }}
  function cancelHide(){{
    if(hideTimer){{clearTimeout(hideTimer);hideTimer=null;}}
  }}
  el.querySelectorAll(".iskg-menubar-item").forEach(function(h){{
    var dd=document.getElementById(h.getAttribute("data-m"));
    h.onclick=function(e){{
      e.stopPropagation();
      if(!dd)return;
      if(openDD===dd){{hideAll();return;}}
      hideAll();
      dd.style.display="block";
      openDD=dd;
    }};
    h.onmouseenter=function(){{
      cancelHide();
      if(dd&&dd!==openDD){{
        hideAll();
        dd.style.display="block";
        openDD=dd;
      }}
    }};
    h.onmouseleave=function(){{
      if(dd&&dd.style.display==="block")scheduleHide();
    }};
    if(dd){{
      dd.onmouseenter=cancelHide;
      dd.onmouseleave=scheduleHide;
    }}
  }});
  el.querySelectorAll(".iskg-menu-dd").forEach(function(dd){{
    dd.onmouseenter=cancelHide;
    dd.onmouseleave=scheduleHide;
  }});
  el.querySelectorAll(".iskg-menu-item").forEach(function(it){{
    it.onclick=function(e){{
      e.stopPropagation();
      if(this.getAttribute("data-sub")){{
        var sub=document.getElementById(this.getAttribute("data-sub"));
        if(sub)sub.style.display=sub.style.display==="block"?"none":"block";
        return;
      }}
      if(this.getAttribute("data-cmd")){{
        var path=[];var cur=this;
        while(cur&&cur!=el){{
          var mn=cur.getAttribute("data-mn");
          if(mn)path.unshift(mn);
          if(!cur.classList.contains("iskg-menu-dd")){{
            var t=cur.querySelector(".iskg-menu-txt");
            if(t)path.unshift(t.innerText);
          }}
          cur=cur.parentElement;
        }}
        hideAll();
        iskg_bridge_event("{self._id}","command",path.join("/"));
      }}
    }};
    it.onmouseenter=function(e){{
      cancelHide();
      var sub=this.getAttribute("data-sub");
      if(sub){{
        var subEl=document.getElementById(sub);
        if(subEl)subEl.style.display="block";
      }}
    }};
    it.onmouseleave=function(){{
      var sub=this.getAttribute("data-sub");
      if(sub)scheduleHide();
    }};
  }});
  document.addEventListener("click",function(){{hideAll();}});
}})();'''

    def _render_update_js(self) -> str:
        return ""

    def _find_command(self, path_parts: list[str]) -> Callable | None:
        for m in self._menus:
            if path_parts and m.text == path_parts[0]:
                return self._walk_items(m.items, path_parts[1:])
        return None

    def _walk_items(self, items: list[MenuItem | None], parts: list[str]) -> Callable | None:
        if not parts:
            return None
        for item in items:
            if item is None:
                continue
            if item.text == parts[0]:
                if len(parts) == 1:
                    return item.command
                if item.submenu:
                    return self._walk_items(item.submenu.items, parts[1:])
        return None

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "command" and event_data:
            cmd = self._find_command(event_data.split("/"))
            if cmd:
                cmd()
        super()._handle_bridge_event(event_name, event_data)
