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
    """A rectangular container widget for grouping children.

    Config options (via kwargs or .config()):

        text (str): Header text shown above children.
        container (bool): If True the outer div becomes ``display:flex;flex-direction:column``
            so the inner wrapper can fill it via ``flex:1``.  Default ``True``.
        direction (str): ``"auto"`` (detect from children's ``side``),
            ``"row"``, or ``"column"``.  Default ``"auto"``.
        gap (int): Gap between children in pixels.  Default ``3``.
        skip_hidden (bool): If True, hidden children are omitted from the HTML.
            If False, they are rendered with ``display:none``. Default ``True``.
        height_mode (str): ``"flex"`` (wrapper uses ``flex:1``, needs ``container=True``),
            ``"percent"`` (wrapper uses ``height:100%``), or ``"auto"``.
            Default ``"flex"``.
    """

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
        if weight == 0 and minsize == 0:
            self._grid_column_weights.pop(column, None)
        else:
            self._grid_column_weights[column] = (weight, minsize)
        self._sync()

    def grid_rowconfigure(self, row: int, weight: float = 0, minsize: int = 0) -> None:
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

    def _pack_direction(self) -> str:
        direction = self._get_cfg("direction", "auto")
        if direction == "row":
            return "row"
        if direction == "column":
            return "column"
        for child in self._children:
            if child._destroyed:
                continue
            side = child._layout_info.get("side", "top") if child._layout_mode == "pack" else "top"
            if side in ("left", "right"):
                return "row"
        return "column"

    def _wrapper_height_style(self) -> str:
        mode = self._get_cfg("height-mode", "flex")
        if mode == "percent":
            return "height:100%;"
        if mode == "flex":
            return "flex:1;"
        return ""

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        style = self._render_style()
        propagate = self._get_cfg("propagate", True)
        if isinstance(propagate, str):
            style += f"overflow:{propagate};"
        elif not propagate:
            style += "overflow:hidden;"
        else:
            style += "overflow:auto;"

        header = ""
        if text:
            header = f'<div class="iskg-frame-header"><span class="hdr-dot"></span> {text}</div>'

        has_grid = any(c._layout_mode == "grid" for c in self._children if not c._destroyed)

        children_html = ""
        skip_hidden = self._get_cfg("skip-hidden", True)
        for child in self._children:
            if child._destroyed:
                continue
            if skip_hidden and child._config_dict.get("hidden"):
                continue
            children_html += child._render()

        if not children_html:
            children_html = ""
        elif has_grid:
            ncols = max(1, self._max_grid_span("column"))
            nrows = max(1, self._max_grid_span("row"))
            cols = _grid_template(self._grid_column_weights, ncols, "1fr", "auto")
            rows = _grid_template(self._grid_row_weights, nrows, "auto", "auto")
            gap = self._get_cfg("gap", 3)
            children_html = f'<div class="iskg-grid" style="display:grid;gap:{gap}px;grid-template-columns:{cols};grid-template-rows:{rows};min-height:0;min-width:0;">{children_html}</div>'
        else:
            gap = self._get_cfg("gap", 3)
            hstyle = self._wrapper_height_style()
            children_html = f'<div style="display:flex;flex-direction:{self._pack_direction()};gap:{gap}px;min-height:0;min-width:0;{hstyle}">{children_html}</div>'

        container = self._get_cfg("container", True)
        if container:
            h_mode = self._get_cfg("height-mode", "flex")
            h_fill = "flex:1;" if h_mode == "flex" and "flex" not in self._config_dict else ""
            style += f"display:flex;flex-direction:column;min-height:0;{h_fill}"

        return f'''<div id="{self._id}" class="iskg-frame" style="{style}">
{header}{children_html}</div>'''


class ScrolledFrame(Frame):
    """A frame with scrollbars when content overflows.

    Args:
        parent: parent widget.
        width: viewport width in pixels (auto if omitted).
        height: viewport height in pixels (auto if omitted).
        scroll: ``"vertical"`` (default), ``"horizontal"``, or ``"both"``.
        autoscroll: if True, auto-scrolls to bottom on content change
                    (useful for log viewers).
        scrollbar_overflow: custom overflow CSS override (e.g. ``"overflow-y:auto;scrollbar-gutter:stable;"``).
    """

    def __init__(
        self,
        parent: Widget | None = None,
        width: int | None = None,
        height: int | None = None,
        scroll: str = "vertical",
        autoscroll: bool = False,
        scrollbar_overflow: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["_scroll"] = scroll
        self._config_dict["_autoscroll"] = autoscroll
        self._config_dict["_scrollbar_overflow"] = scrollbar_overflow
        if width is not None:
            self._config_dict["width"] = width
        if height is not None:
            self._config_dict["height"] = height

    def _overflow_css(self) -> str:
        custom = self._config_dict.get("_scrollbar_overflow")
        if custom:
            return custom
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
            child._render() for child in self._children if not child._destroyed
        )
        return f'<div id="{self._id}" class="iskg-scrollframe" style="{style}">{header}{children_html}</div>'

    def _render_js(self) -> str:
        if self._config_dict.get("_autoscroll"):
            return f'var el=document.getElementById("{self._id}");if(el){{new ResizeObserver(function(){{el.scrollTop=el.scrollHeight;}}).observe(el);}}'
        return super()._render_js()


class PanedWindow(Widget):
    """A container with resizable panes separated by draggable dividers.

    Supports any number of child panes. Each pane gets equal space initially;
    drag the sashes to resize adjacent panes.

    Args:
        parent: parent widget.
        orient: ``"horizontal"`` (left/right panes) or ``"vertical"`` (top/bottom).
        sash_pos: initial divider position as fraction (0.0–1.0, default 0.5).
            Only used when there are exactly 2 panes.
        minsize: minimum pane size in pixels (default 30).
        sash_width: sash thickness in pixels (default 5).
    """

    def __init__(
        self,
        parent: Widget | None = None,
        orient: str = "horizontal",
        sash_pos: float = 0.5,
        minsize: int = 30,
        sash_width: int = 5,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["_orient"] = orient
        self._config_dict["_sash_pos"] = sash_pos
        self._config_dict["_minsize"] = minsize
        self._config_dict["_sash_width"] = sash_width

    def sash_pos(self, pos: float) -> None:
        self._config_dict["_sash_pos"] = max(0.0, min(1.0, pos))
        self._sync()

    def _render(self) -> str:
        orient = self._config_dict.get("_orient", "horizontal")
        minsize = self._config_dict.get("_minsize", 30)
        sash_width = self._config_dict.get("_sash_width", 5)
        style = self._render_style()

        if orient == "horizontal":
            flex_dir = "flex-direction:row;"
            sash_cursor = "cursor:col-resize;"
            size_prop = "width"
            sash_style = f"width:{sash_width}px;"
        else:
            flex_dir = "flex-direction:column;"
            sash_cursor = "cursor:row-resize;"
            size_prop = "height"
            sash_style = f"height:{sash_width}px;"

        panes: list[Widget] = []
        for child in self._children:
            if not child._destroyed and not child._config_dict.get("hidden"):
                panes.append(child)

        n = len(panes)
        if n == 0:
            return f'<div id="{self._id}" class="iskg-panedwindow" style="{style}{flex_dir}display:flex;flex:1;min-height:0;min-width:0;"></div>'

        children_html = ""
        for idx, pane in enumerate(panes):
            children_html += f'<div style="display:flex;flex-direction:column;flex:1;min-{size_prop}:{minsize}px;">{pane._render()}</div>'
            if idx < n - 1:
                children_html += f'<div id="{self._id}-sash-{idx}" class="iskg-sash" style="{sash_cursor}{sash_style}background:var(--border);flex-shrink:0;"></div>'

        return f'<div id="{self._id}" class="iskg-panedwindow" style="{style}{flex_dir}display:flex;flex:1;min-height:0;min-width:0;">{children_html}</div>'

    def _render_js(self) -> str:
        orient = self._config_dict.get("_orient", "horizontal")
        pw_id = self._id
        panes: list[Widget] = []
        for child in self._children:
            if not child._destroyed and not child._config_dict.get("hidden"):
                panes.append(child)
        n = len(panes)
        if n < 2:
            return ""
        is_h = "true" if orient == "horizontal" else "false"
        js = f"(function(){{var pw=document.getElementById('{pw_id}');if(!pw)return;var isHoriz={is_h};"
        for i in range(n - 1):
            left_idx = i * 2
            right_idx = (i + 1) * 2
            js += f"""
(function(){{
var sash=document.getElementById('{pw_id}-sash-{i}');
if(!sash)return;
var down=false;
sash.onmousedown=function(e){{down=true;e.preventDefault();document.body.style.userSelect='none';}};
document.addEventListener('mousemove',function(e){{
if(!down)return;
var rect=pw.getBoundingClientRect();
var p=isHoriz?(e.clientX-rect.left)/rect.width:(e.clientY-rect.top)/rect.height;
p=Math.max(0.05,Math.min(0.95,p));
var c=pw.children;
if(c.length>{right_idx}){{
c[{left_idx}].style.flex=p;
c[{right_idx}].style.flex=1-p;
}}
}});
document.addEventListener('mouseup',function(){{down=false;document.body.style.userSelect='';}});
}})();"""
        js += "})();"
        return js


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
        self.add(widget)
        return widget

    def _render(self) -> str:
        style = self._render_style()
        tabs_html = ""
        pages_html = ""
        for i, tab in enumerate(self._tabs):
            active = " active" if i == 0 else ""
            tabs_html += f'<div class="iskg-tab{active}" data-idx="{i}">{tab["title"]}</div>'
            page_style = (
                "display:block;overflow:auto;" if i == 0 else "display:none;overflow:auto;"
            )
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
        kwargs.setdefault("width" if orient == "horizontal" else "height", "95%")
        super().__init__(parent, **kwargs)
        self._config_dict["orient"] = orient

    def _render(self) -> str:
        orient = self._config_dict.get("orient", "horizontal")
        cls = "iskg-vsep" if orient == "vertical" else "iskg-hsep"
        style = self._render_style()
        return f'<hr class="{cls}" id="{self._id}" style="{style}"/>'


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
    """A scrollbar widget for scrolling content.

    Config options (via kwargs or .config()):
        orient (str): ``"vertical"`` or ``"horizontal"``.
        value (float): Scroll position as percentage (0-100).
        thumb_size (int): Thumb size in pixels. Default 20.
        step (int): Scroll step in percentage points. Default 5.
    """

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
        thumb_size = self._get_cfg("thumb-size", 20)
        if orient == "vertical":
            height = self._config_dict.get("height", 100)
            cls = "iskg-scrollbar iskg-scrollbar-vert"
            return f'''<div id="{self._id}" class="{cls}" style="{style}height:{height}px;">
  <div class="iskg-scrollbar-thumb" style="top:{val}%;height:{thumb_size}px;"></div>
</div>'''
        else:
            width = self._config_dict.get("width", 100)
            cls = "iskg-scrollbar iskg-scrollbar-horiz"
            return f'''<div id="{self._id}" class="{cls}" style="{style}width:{width}px;">
  <div class="iskg-scrollbar-thumb" style="left:{val}%;width:{thumb_size}px;"></div>
</div>'''

    def _render_js(self) -> str:
        orient = self._config_dict.get("orient", "vertical")
        is_vert = orient == "vertical"
        pos_prop = "top" if is_vert else "left"
        size_prop = "height" if is_vert else "width"
        thumb_size = self._get_cfg("thumb-size", 20)
        step = self._get_cfg("step", 5)
        return f'''var el=document.getElementById("{self._id}");
var thumb=el.querySelector(".iskg-scrollbar-thumb");
el.onwheel=function(e){{
  e.preventDefault();
  var v=parseFloat(thumb.style.{pos_prop})||0;
  var step={step};
  v+=(e.deltaY>0?step:-step);
  var maxV=100-({thumb_size}/el.{size_prop}*100);
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
