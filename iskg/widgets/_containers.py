from __future__ import annotations

from typing import Any

from ..base import Widget


def _grid_template(
    weights: dict[int, tuple[float, int]],
    count: int,
    default_unit: str = "1fr",
    auto_unit: str = "auto",
) -> str:
    if not weights:
        return f"repeat({count},{default_unit})"
    parts: list[str] = []
    for i in range(count):
        entry = weights.get(i)
        if entry is not None:
            w, ms = entry
            if ms:
                parts.append(f"minmax({ms}px,{w}fr)" if w > 0 else f"minmax({ms}px,auto)")
            else:
                parts.append(f"{w}fr" if w > 0 else auto_unit)
        else:
            parts.append(auto_unit)
    return " ".join(parts)


class Frame(Widget):
    """A rectangular container widget for grouping children."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._pack_layout = None
        self._grid_layout = None
        self._grid_column_weights: dict[int, tuple[float, int]] = {}
        self._grid_row_weights: dict[int, tuple[float, int]] = {}

    def grid_columnconfigure(self, column: int, weight: float = 0, minsize: int = 0) -> None:
        """Configure a grid column's weight and minimum size.

        Args:
            column: column index (0-based).
            weight: relative weight for distributing extra space (0 = auto).
            minsize: minimum column width in pixels (0 = none).

        When both *weight* and *minsize* are 0 the column is removed
        from the explicit config and treated as ``auto``.
        """
        if weight == 0 and minsize == 0:
            self._grid_column_weights.pop(column, None)
        else:
            self._grid_column_weights[column] = (weight, minsize)
        self._sync()

    def grid_rowconfigure(self, row: int, weight: float = 0, minsize: int = 0) -> None:
        """Configure a grid row's weight and minimum size.

        Args:
            row: row index (0-based).
            weight: relative weight for distributing extra space (0 = auto).
            minsize: minimum row height in pixels (0 = none).
        """
        if weight == 0 and minsize == 0:
            self._grid_row_weights.pop(row, None)
        else:
            self._grid_row_weights[row] = (weight, minsize)
        self._sync()

    def pack_propagate(self, flag: bool) -> None:
        self._config_dict["propagate"] = flag
        self._sync()

    def _max_grid_span(self, attr: str) -> int:
        m = 0
        for child in self._children:
            if child._destroyed:
                continue
            if child._layout_mode == "grid":
                start = child._layout_info.get(attr, 0)
                span = child._layout_info.get(f"{attr}span", 1)
                m = max(m, start + span)
        return m

    def _detect_layout(self) -> str:
        if any(c._layout_mode == "grid" for c in self._children if not c._destroyed):
            return "grid"
        return "pack"

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        style = self._render_style()
        flex = self._config_dict.get("flex", "")
        if flex:
            style += f"flex:{flex};"
        min_h = self._config_dict.get("min_height", "")
        if min_h:
            style += f"min-height:{min_h}px;overflow:auto;"

        propagate = self._config_dict.get("propagate", True)
        if not propagate:
            style += "overflow:hidden;"

        header = ""
        if text:
            header = f'<div class="iskg-frame-header"><span class="hdr-dot"></span> {text}</div>'

        has_grid = any(c._layout_mode == "grid" for c in self._children if not c._destroyed)

        children_html = ""
        for child in self._children:
            if not child._destroyed:
                if child._config_dict.get("hidden"):
                    continue
                children_html += child._render()

        if not children_html:
            children_html = ""
        elif has_grid:
            ncols = max(1, self._max_grid_span("column"))
            nrows = max(1, self._max_grid_span("row"))
            cols = _grid_template(self._grid_column_weights, ncols, "1fr", "auto")
            rows = _grid_template(self._grid_row_weights, nrows, "auto", "auto")
            children_html = f'<div class="iskg-grid" style="display:grid;gap:3px;grid-template-columns:{cols};grid-template-rows:{rows};min-height:0;min-width:0;">{children_html}</div>'
        else:
            children_html = f'<div style="display:flex;flex-wrap:wrap;gap:3px;min-height:0;min-width:0;">{children_html}</div>'

        return f'''<div id="{self._id}" class="iskg-frame" style="{style}">
{header}{children_html}</div>'''

    def _render_update_js(self) -> str:
        js = []
        propagate = self._config_dict.get("propagate", True)
        if not propagate:
            js.append(
                f'var e=document.getElementById("{self._id}");if(e)e.style.overflow="hidden";'
            )
        return ";".join(js) if js else ""


class ScrolledFrame(Frame):
    """A frame with scrollbars when content overflows.

    Args:
        parent: parent widget.
        width: viewport width in pixels (auto if omitted).
        height: viewport height in pixels (auto if omitted).
        scroll: ``"vertical"`` (default), ``"horizontal"``, or ``"both"``.
        autoscroll: if True, auto-scrolls to bottom on content change
                    (useful for log viewers).
    """

    def __init__(
        self,
        parent: Widget | None = None,
        width: int | None = None,
        height: int | None = None,
        scroll: str = "vertical",
        autoscroll: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["_scroll"] = scroll
        self._config_dict["_autoscroll"] = autoscroll
        if width is not None:
            self._config_dict["width"] = width
        if height is not None:
            self._config_dict["height"] = height

    def _overflow_css(self) -> str:
        s = self._config_dict.get("_scroll", "vertical")
        m: dict[str, str] = {
            "vertical": "overflow-y:auto;overflow-x:hidden;",
            "horizontal": "overflow-x:auto;overflow-y:hidden;",
            "both": "overflow:auto;",
        }
        return m.get(s, "overflow-y:auto;overflow-x:hidden;")

    def _render(self) -> str:
        style = self._render_style() + self._overflow_css()
        text = self._config_dict.get("text", "")
        header = ""
        if text:
            header = f'<div class="iskg-frame-header"><span class="hdr-dot"></span> {text}</div>'
        children_html = "".join(
            child._render()
            for child in self._children
            if not child._destroyed and not child._config_dict.get("hidden")
        )
        return f'<div id="{self._id}" class="iskg-scrollframe" style="{style}">{header}{children_html}</div>'

    def _render_js(self) -> str:
        if self._config_dict.get("_autoscroll"):
            return f'''var el=document.getElementById("{self._id}");
if(el){{new ResizeObserver(function(){{el.scrollTop=el.scrollHeight;}}).observe(el);}}'''
        return super()._render_js()


class PanedWindow(Widget):
    """A container with two resizable panes separated by a draggable divider.

    Args:
        parent: parent widget.
        orient: ``"horizontal"`` (left/right panes) or ``"vertical"`` (top/bottom).
        sash_pos: initial divider position as fraction (0.0–1.0, default 0.5).
        minsize: minimum pane size in pixels (default 30).
    """

    def __init__(
        self,
        parent: Widget | None = None,
        orient: str = "horizontal",
        sash_pos: float = 0.5,
        minsize: int = 30,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["_orient"] = orient
        self._config_dict["_sash_pos"] = sash_pos
        self._config_dict["_minsize"] = minsize

    def sash_pos(self, pos: float) -> None:
        self._config_dict["_sash_pos"] = max(0.0, min(1.0, pos))
        self._sync()

    def _render(self) -> str:
        orient = self._config_dict.get("_orient", "horizontal")
        pos = self._config_dict.get("_sash_pos", 0.5)
        minsize = self._config_dict.get("_minsize", 30)
        style = self._render_style()

        if orient == "horizontal":
            flex_dir = "flex-direction:row;"
            sash_cursor = "cursor:col-resize;"
            sash_style = "width:5px;"
        else:
            flex_dir = "flex-direction:column;"
            sash_cursor = "cursor:row-resize;"
            sash_style = "height:5px;"

        children_html = ""
        pane1_style = f"flex:{pos};min-{'width' if orient == 'horizontal' else 'height'}:{minsize}px;overflow:hidden;"
        pane2_style = f"flex:{1 - pos};min-{'width' if orient == 'horizontal' else 'height'}:{minsize}px;overflow:hidden;"

        panes: list[Widget] = []
        for child in self._children:
            if not child._destroyed and not child._config_dict.get("hidden"):
                panes.append(child)

        if len(panes) >= 1:
            children_html += f'<div style="{pane1_style}">{panes[0]._render()}</div>'
        if len(panes) >= 2:
            children_html += f'<div id="{self._id}-sash" class="iskg-sash" style="{sash_cursor}{sash_style}background:var(--border);flex-shrink:0;"></div>'
            children_html += f'<div style="{pane2_style}">{panes[1]._render()}</div>'

        return f'<div id="{self._id}" class="iskg-panedwindow" style="{style}{flex_dir}display:flex;min-height:0;min-width:0;">{children_html}</div>'

    def _render_js(self) -> str:
        orient = self._config_dict.get("_orient", "horizontal")
        is_horiz = "true" if orient == "horizontal" else "false"
        return f'''(function(){{
var pw=document.getElementById("{self._id}");
var sash=document.getElementById("{self._id}-sash");
if(!sash||!pw)return;
var isHoriz={is_horiz};
var down=false;
sash.onmousedown=function(e){{down=true;e.preventDefault();document.body.style.userSelect="none";}};
document.addEventListener("mousemove",function(e){{
  if(!down)return;
  var rect=pw.getBoundingClientRect();
  var p=isHoriz?(e.clientX-rect.left)/rect.width:(e.clientY-rect.top)/rect.height;
  p=Math.max(0.05,Math.min(0.95,p));
  var panes=pw.children;
  if(panes.length>=2){{
    panes[0].style.flex=p;
    panes[2].style.flex=1-p;
  }}
}});
document.addEventListener("mouseup",function(){{down=false;document.body.style.userSelect="";}});
}})();'''


class Notebook(Widget):
    """A tabbed container widget."""

    def __init__(
        self,
        parent: Widget | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._tabs: list[dict] = []

    def add_tab(self, title: str, widget: Widget) -> Widget:
        self._tabs.append({"title": title, "widget": widget})
        widget._parent = self
        self._children.append(widget)
        return widget

    def _render(self) -> str:
        style = self._render_style()
        tabs_html = ""
        pages_html = ""
        for i, tab in enumerate(self._tabs):
            active = " active" if i == 0 else ""
            tabs_html += f'<div class="iskg-tab{active}" data-idx="{i}">{tab["title"]}</div>'
            page_style = "display:block;" if i == 0 else "display:none;"
            pages_html += f'<div class="iskg-tabpage" id="{self._id}-page-{i}" style="{page_style}">{tab["widget"]._render()}</div>'
        return f'''<div id="{self._id}" class="iskg-notebook" style="{style}">
  <div class="iskg-tabbar">{tabs_html}</div>
  {pages_html}
</div>'''

    def _render_js(self) -> str:
        return f'''var tb=document.getElementById("{self._id}");
if(tb){{
  var tabs=tb.querySelectorAll(".iskg-tab");
  for(var i=0;i<tabs.length;i++){{(function(idx){{
    tabs[idx].onclick=function(){{
      tb.querySelectorAll(".iskg-tab").forEach(function(t){{t.classList.remove("active");}});
      this.classList.add("active");
      tb.querySelectorAll(".iskg-tabpage").forEach(function(p){{p.style.display="none";}});
      var pg=document.getElementById("{self._id}-page-"+idx);
      if(pg)pg.style.display="block";
      iskg_bridge_event("{self._id}","change",idx.toString());
    }};
  }})(i);}}
}};'''


class Separator(Widget):
    """A horizontal or vertical visual separator line."""

    def __init__(
        self,
        parent: Widget | None = None,
        orient: str = "horizontal",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["orient"] = orient

    def _render(self) -> str:
        orient = self._config_dict.get("orient", "horizontal")
        cls = "iskg-vsep" if orient == "vertical" else "iskg-hsep"
        style = self._render_style()
        if orient == "vertical":
            height = self._config_dict.get("height", 50)
            return f'<hr class="{cls}" id="{self._id}" style="{style}height:{height}px;"/>'
        width = self._config_dict.get("width", "100%")
        return f'<hr class="{cls}" id="{self._id}" style="{style}width:{width}px;"/>'


class Spacer(Widget):
    """An invisible spacer widget for layout."""

    def __init__(
        self,
        parent: Widget | None = None,
        width: int = 0,
        height: int = 0,
        expand: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["expand"] = expand

    def _render(self) -> str:
        style = self._render_style()
        w = self._config_dict.get("width", 0)
        h = self._config_dict.get("height", 0)
        exp = self._config_dict.get("expand", False)
        w_s = f"width:{w}px;" if w else ""
        h_s = f"height:{h}px;" if h else ""
        e_s = "flex:1;min-height:0;min-width:0;" if exp else ""
        return f'<div id="{self._id}" class="iskg-spacer" style="{style}{w_s}{h_s}{e_s}"></div>'


class ScrollBar(Widget):
    """A scrollbar widget for scrolling content."""

    def __init__(
        self,
        parent: Widget | None = None,
        orient: str = "vertical",
        value: float = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["orient"] = orient
        self._config_dict["value"] = value

    def _render(self) -> str:
        orient = self._config_dict.get("orient", "vertical")
        val = self._config_dict.get("value", 0)
        style = self._render_style()
        if orient == "vertical":
            height = self._config_dict.get("height", 100)
            cls = "iskg-scrollbar iskg-scrollbar-vert"
            return f'''<div id="{self._id}" class="{cls}" style="{style}height:{height}px;">
  <div class="iskg-scrollbar-thumb" style="top:{val}%;height:20px;"></div>
</div>'''
        else:
            width = self._config_dict.get("width", 100)
            cls = "iskg-scrollbar iskg-scrollbar-horiz"
            return f'''<div id="{self._id}" class="{cls}" style="{style}width:{width}px;">
  <div class="iskg-scrollbar-thumb" style="left:{val}%;width:20px;"></div>
</div>'''

    def _render_js(self) -> str:
        orient = self._config_dict.get("orient", "vertical")
        is_vert = orient == "vertical"
        pos_prop = "top" if is_vert else "left"
        size_prop = "height" if is_vert else "width"
        return f'''var el=document.getElementById("{self._id}");
var thumb=el.querySelector(".iskg-scrollbar-thumb");
el.onwheel=function(e){{
  e.preventDefault();
  var v=parseFloat(thumb.style.{pos_prop})||0;
  var step=5;
  v+=(e.deltaY>0?step:-step);
  var maxV=100-(20/el.{size_prop}*100);
  v=Math.max(0,Math.min(maxV,v));
  thumb.style.{pos_prop}=v+"%";
  iskg_bridge_event("{self._id}","change",v.toString());
}};'''

    def _render_update_js(self) -> str:
        orient = self._config_dict.get("orient", "vertical")
        val = self._config_dict.get("value", 0)
        pos_prop = "top" if orient == "vertical" else "left"
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-scrollbar-thumb").style.{pos_prop}="{val}%";'''
