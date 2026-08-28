"""Additional picker widgets: FontPicker, DirectoryPicker, ImagePicker,
SearchCtrl, Carousel, Avatar, Badge, Spinner, ProgressCircle, Toast.
"""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Callable
from typing import Any

from ..base import Widget

# ─── FontPicker ─────────────────────────────────────────────────────────


# A curated list of fonts the picker can show. The actual font is
# applied via the CSS ``font-family`` property.
_FONT_FAMILIES = [
    "Inter",
    "Segoe UI",
    "Roboto",
    "Open Sans",
    "Lato",
    "Montserrat",
    "Source Code Pro",
    "JetBrains Mono",
    "Fira Code",
    "Cascadia Code",
    "Space Mono",
    "IBM Plex Sans",
    "IBM Plex Mono",
    "Manrope",
    "Nunito",
    "Poppins",
    "Raleway",
    "Ubuntu",
    "Helvetica Neue",
    "Arial",
    "Georgia",
    "Times New Roman",
    "Courier New",
]


class FontPicker(Widget):
    """A combo + preview that lets the user pick a font family.

    Args:
        parent: parent widget.
        font_family: initial font family (default ``"Inter"``).
        preview_text: text shown in the preview.
        command: optional ``(family) -> None`` callback.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        font_family: str = "Inter",
        preview_text: str = "The quick brown fox jumps over the lazy dog",
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["font_family"] = font_family
        self._config_dict["preview_text"] = preview_text
        self._config_dict["fonts"] = list(_FONT_FAMILIES)
        if command is not None:
            self._config_dict["command"] = command

    @property
    def font_family(self) -> str:
        return self._config_dict.get("font_family", "Inter")

    @font_family.setter
    def font_family(self, v: str) -> None:
        self._config_dict["font_family"] = str(v)
        self._sync()

    @property
    def preview_text(self) -> str:
        return self._config_dict.get("preview_text", "")

    @preview_text.setter
    def preview_text(self, v: str) -> None:
        self._config_dict["preview_text"] = str(v)
        self._sync()

    def _render(self) -> str:
        family = self._config_dict.get("font_family", "Inter")
        text = self._config_dict.get("preview_text", "")
        fonts = self._config_dict.get("fonts", _FONT_FAMILIES)
        style = self._render_style()
        attrs = self._render_attrs()
        opts = "".join(
            f'<option value="{f}"{"selected" if f == family else ""}>{f}</option>' for f in fonts
        )
        return (
            f'<div id="{self._id}" class="iskg-fontpicker" style="{style}" {attrs}>'
            f'<select class="iskg-fp-select">{opts}</select>'
            f'<div class="iskg-fp-preview" '
            f"style=\"font-family:'{family}',sans-serif;\">{text}</div>"
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var sel=el.querySelector(".iskg-fp-select");
  var prev=el.querySelector(".iskg-fp-preview");
  sel.onchange=function(){{
    var f=sel.value;
    prev.style.fontFamily="'"'"'+f+'"'"'+',sans-serif';
    iskg_bridge_event("{self._id}","change",f);
  }};
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            self._config_dict["font_family"] = str(event_data or "")
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(self._config_dict["font_family"])
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        family = self._config_dict.get("font_family", "Inter")
        return f'''var el=document.getElementById("{self._id}");
if(el){{var sel=el.querySelector(".iskg-fp-select");if(sel)sel.value={json.dumps(family)};
var prev=el.querySelector(".iskg-fp-preview");
if(prev)prev.style.fontFamily='\"'+{json.dumps(family)}+'\"'+',sans-serif';}}'''


# ─── DirectoryPicker ────────────────────────────────────────────────────


class DirectoryPicker(Widget):
    """An inline directory picker with a path display + Browse button.

    Args:
        parent: parent widget.
        root: starting directory (``~`` expanded).
        width: viewport width in px.
        command: optional ``(path) -> None`` callback.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        root: str = "~",
        width: int = 300,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["root"] = os.path.expanduser(str(root))
        self._config_dict["width"] = width
        self._config_dict["path"] = self._config_dict["root"]
        if command is not None:
            self._config_dict["command"] = command

    @property
    def path(self) -> str:
        return self._config_dict.get("path", "")

    @path.setter
    def path(self, v: str) -> None:
        self._config_dict["path"] = str(v)
        self._sync()

    def browse(self) -> None:
        """Open the system directory chooser (pywebview-backed)."""
        if self._app and self._app._window:
            with contextlib.suppress(Exception):
                result = self._app._window.create_directory_dialog(
                    directory=self._config_dict.get("path", "")
                )
                if result:
                    self._config_dict["path"] = result
                    self._sync()
                    cmd = self._config_dict.get("command")
                    if cmd is not None:
                        with contextlib.suppress(Exception):
                            cmd(result)

    def _render(self) -> str:
        path = self._config_dict.get("path", "")
        style = self._render_style()
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-dirpicker" style="{style}" {attrs}>'
            f'<input class="iskg-dp-path" type="text" value="{path}" readonly />'
            f'<button class="iskg-dp-browse">Browse</button>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var btn=el.querySelector(".iskg-dp-browse");
  if(btn)btn.onclick=function(){{iskg_bridge_event("{self._id}","browse","");}};
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "browse":
            self.browse()
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        path = self._config_dict.get("path", "")
        return f'''var el=document.getElementById("{self._id}");
if(el){{var i=el.querySelector(".iskg-dp-path");if(i)i.value={json.dumps(path)};}}'''


# ─── ImagePicker ────────────────────────────────────────────────────────


class ImagePicker(Widget):
    """Inline image preview + Browse to pick a new file."""

    def __init__(
        self,
        parent: Widget | None = None,
        src: str = "",
        width: int = 240,
        height: int = 180,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["src"] = src
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        if command is not None:
            self._config_dict["command"] = command

    @property
    def src(self) -> str:
        return self._config_dict.get("src", "")

    @src.setter
    def src(self, v: str) -> None:
        self._config_dict["src"] = str(v)
        self._sync()

    def browse(self) -> None:
        if self._app and self._app._window:
            with contextlib.suppress(Exception):
                fns = self._app._window.create_file_dialog(
                    file_types=("Images (*.png;*.jpg;*.jpeg;*.gif;*.webp)",)
                )
                if fns and fns[0]:
                    self._config_dict["src"] = fns[0]
                    self._sync()
                    cmd = self._config_dict.get("command")
                    if cmd is not None:
                        with contextlib.suppress(Exception):
                            cmd(fns[0])

    def _render(self) -> str:
        src = self._config_dict.get("src", "")
        style = self._render_style()
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-imagepicker" style="{style}" {attrs}>'
            f'<img src="{src}" class="iskg-ip-img" />'
            f'<button class="iskg-ip-browse">Browse…</button>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var b=el.querySelector(".iskg-ip-browse");
  if(b)b.onclick=function(){{iskg_bridge_event("{self._id}","browse","");}};
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "browse":
            self.browse()
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        src = self._config_dict.get("src", "")
        return f'''var el=document.getElementById("{self._id}");
if(el){{var img=el.querySelector(".iskg-ip-img");if(img)img.src={json.dumps(src)};}}'''


# ─── SearchCtrl ─────────────────────────────────────────────────────────


class SearchCtrl(Widget):
    """Composite search input with a search button and a clear (×) button.

    Args:
        parent: parent widget.
        placeholder: placeholder text.
        command: optional ``(query) -> None`` callback fired on each
            keystroke (debounced) and on Enter.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        placeholder: str = "Search…",
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["placeholder"] = placeholder
        self._config_dict["text"] = ""
        if command is not None:
            self._config_dict["command"] = command

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, v: str) -> None:
        self._config_dict["text"] = str(v)
        self._sync()

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        placeholder = self._config_dict.get("placeholder", "")
        style = self._render_style()
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-searchctrl" style="{style}" {attrs}>'
            f'<span class="iskg-sc-icon">\U0001f50d</span>'
            f'<input class="iskg-sc-input" type="text" '
            f'value="{text}" placeholder="{placeholder}" />'
            f'<button class="iskg-sc-clear">\u2715</button>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var inp=el.querySelector(".iskg-sc-input");
  var clr=el.querySelector(".iskg-sc-clear");
  var t;
  inp.oninput=function(){{clearTimeout(t);var v=inp.value;
    t=setTimeout(function(){{iskg_bridge_event("{self._id}","change",v);}},120);
  }};
  inp.onkeydown=function(e){{if(e.key==="Enter"){{clearTimeout(t);iskg_bridge_event("{self._id}","submit",inp.value);}}}};
  if(clr)clr.onclick=function(){{inp.value="";iskg_bridge_event("{self._id}","clear","");}};
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name in ("change", "submit", "clear"):
            self._config_dict["text"] = str(event_data or "")
            cmd = self._config_dict.get("command")
            if cmd is not None and event_name != "clear":
                with contextlib.suppress(Exception):
                    cmd(self._config_dict["text"])
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        text = self._config_dict.get("text", "")
        return f'''var el=document.getElementById("{self._id}");
if(el){{var i=el.querySelector(".iskg-sc-input");if(i)i.value={json.dumps(text)};}}'''


# ─── Carousel ──────────────────────────────────────────────────────────


class Carousel(Widget):
    """A paginated scrolling widget with prev/next buttons and dots.

    Args:
        parent: parent widget.
        items: list of widgets (or strings, which become ``<div>``s).
        loop: if ``True`` wrap around at the ends.
        autoplay_ms: auto-advance interval in ms (``0`` disables).
        command: optional ``(index) -> None`` callback when the page
            changes.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        items: list[Any] | None = None,
        loop: bool = True,
        autoplay_ms: int = 0,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._items: list[Any] = list(items or [])
        self._config_dict["loop"] = loop
        self._config_dict["autoplay_ms"] = autoplay_ms
        self._config_dict["current"] = 0
        if command is not None:
            self._config_dict["command"] = command

    def add_item(self, item: Any) -> None:
        self._items.append(item)
        self._sync()

    def clear(self) -> None:
        self._items.clear()
        self._config_dict["current"] = 0
        self._sync()

    def next(self) -> None:
        n = len(self._items)
        if n == 0:
            return
        cur = self._config_dict.get("current", 0)
        if cur + 1 < n:
            self._config_dict["current"] = cur + 1
        elif self._config_dict.get("loop", True):
            self._config_dict["current"] = 0
        self._sync()

    def prev(self) -> None:
        n = len(self._items)
        if n == 0:
            return
        cur = self._config_dict.get("current", 0)
        if cur > 0:
            self._config_dict["current"] = cur - 1
        elif self._config_dict.get("loop", True):
            self._config_dict["current"] = n - 1
        self._sync()

    def _render(self) -> str:
        cur = self._config_dict.get("current", 0)
        n = len(self._items)
        style = self._render_style()
        attrs = self._render_attrs()
        items_html = "".join(
            f'<div class="iskg-carousel-item">{(item._render() if hasattr(item, "_render") else str(item))}</div>'
            for item in self._items
        )
        dots = "".join(
            f'<span class="iskg-carousel-dot{" active" if i == cur else ""}" data-idx="{i}"></span>'
            for i in range(max(n, 1))
        )
        return (
            f'<div id="{self._id}" class="iskg-carousel" style="{style}" {attrs}>'
            f'<div class="iskg-carousel-track" style="transform:translateX(-{cur * 100}%);">'
            f"{items_html}</div>"
            f'<button class="iskg-carousel-nav iskg-carousel-prev">\u2039</button>'
            f'<button class="iskg-carousel-nav iskg-carousel-next">\u203a</button>'
            f'<div class="iskg-carousel-dots">{dots}</div>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  var prev=el.querySelector(".iskg-carousel-prev");
  var next=el.querySelector(".iskg-carousel-next");
  if(prev)prev.onclick=function(){{iskg_bridge_event("{self._id}","prev","");}};
  if(next)next.onclick=function(){{iskg_bridge_event("{self._id}","next","");}};
  el.querySelectorAll(".iskg-carousel-dot").forEach(function(d){{
    d.onclick=function(){{iskg_bridge_event("{self._id}","goto",d.dataset.idx);}};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "next":
            self.next()
        elif event_name == "prev":
            self.prev()
        elif event_name == "goto":
            with contextlib.suppress(ValueError):
                self._config_dict["current"] = int(event_data)
                self._sync()
        cmd = self._config_dict.get("command")
        if cmd is not None:
            with contextlib.suppress(Exception):
                cmd(self._config_dict.get("current", 0))
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        cur = self._config_dict.get("current", 0)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var t=el.querySelector(".iskg-carousel-track");
if(t)t.style.transform="translateX(-" + {cur * 100} + "%)";
el.querySelectorAll(".iskg-carousel-dot").forEach(function(d,i){{
d.classList.toggle("active",i==={cur});
}});}}'''


# ─── Avatar / Badge / Spinner / ProgressCircle ─────────────────────────


class Avatar(Widget):
    """A circular avatar with image (or initials fallback)."""

    def __init__(
        self,
        parent: Widget | None = None,
        src: str = "",
        initials: str = "?",
        size: int = 32,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["src"] = src
        self._config_dict["initials"] = initials
        self._config_dict["size"] = size

    @property
    def src(self) -> str:
        return self._config_dict.get("src", "")

    @src.setter
    def src(self, v: str) -> None:
        self._config_dict["src"] = str(v)
        self._sync()

    def _render(self) -> str:
        src = self._config_dict.get("src", "")
        initials = self._config_dict.get("initials", "?")
        size = self._config_dict.get("size", 32)
        attrs = self._render_attrs()
        body = (
            f'<img src="{src}" />'
            if src
            else f'<span class="iskg-avatar-initials">{initials}</span>'
        )
        return (
            f'<div id="{self._id}" class="iskg-avatar" '
            f'style="width:{size}px;height:{size}px;font-size:{int(size * 0.4)}px;" {attrs}>'
            f"{body}</div>"
        )

    def _render_update_js(self) -> str:
        src = self._config_dict.get("src", "")
        return f'''var el=document.getElementById("{self._id}");
if(el){{var i=el.querySelector("img");if(i)i.src={json.dumps(src)};}}'''


class Badge(Widget):
    """A small inline badge with a color variant."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        variant: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        if variant not in ("default", "success", "warn", "error"):
            variant = "default"
        self._config_dict["variant"] = variant

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, v: str) -> None:
        self._config_dict["text"] = str(v)
        self._sync()

    @property
    def variant(self) -> str:
        return self._config_dict.get("variant", "default")

    @variant.setter
    def variant(self, v: str) -> None:
        if v not in ("default", "success", "warn", "error"):
            v = "default"
        self._config_dict["variant"] = v
        self._sync()

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        variant = self._config_dict.get("variant", "default")
        attrs = self._render_attrs()
        return f'<span id="{self._id}" class="iskg-badge {variant}" {attrs}>{text}</span>'


class Spinner(Widget):
    """An animated circular loading spinner."""

    def __init__(
        self,
        parent: Widget | None = None,
        size: int = 18,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["size"] = size

    def _render(self) -> str:
        size = self._config_dict.get("size", 18)
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-spinner" '
            f'style="width:{size}px;height:{size}px;" {attrs}></div>'
        )


class ProgressCircle(Widget):
    """A circular progress indicator (determinate)."""

    def __init__(
        self,
        parent: Widget | None = None,
        value: float = 0.0,
        size: int = 60,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["value"] = value
        self._config_dict["size"] = size

    @property
    def value(self) -> float:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: float) -> None:
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self) -> str:
        size = self._config_dict.get("size", 60)
        value = max(0.0, min(1.0, self._config_dict.get("value", 0)))
        attrs = self._render_attrs()
        r = size // 2 - 4
        circ = 2 * 3.14159 * r
        offset = circ * (1 - value)
        return (
            f'<div id="{self._id}" class="iskg-progress-circle" '
            f'style="width:{size}px;height:{size}px;" {attrs}>'
            f'<svg viewBox="0 0 {size} {size}">'
            f'<circle class="iskg-progress-circle-bg" cx="{size // 2}" cy="{size // 2}" r="{r}" />'
            f'<circle class="iskg-progress-circle-fg" cx="{size // 2}" cy="{size // 2}" r="{r}" '
            f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}" />'
            f"</svg>"
            f'<span class="iskg-progress-circle-text">{int(value * 100)}%</span>'
            f"</div>"
        )

    def _render_update_js(self) -> str:
        size = self._config_dict.get("size", 60)
        value = max(0.0, min(1.0, self._config_dict.get("value", 0)))
        r = size // 2 - 4
        circ = 2 * 3.14159 * r
        offset = circ * (1 - value)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var c=el.querySelector(".iskg-progress-circle-fg");
if(c){{c.setAttribute("stroke-dasharray","{circ:.2f}");
c.setAttribute("stroke-dashoffset","{offset:.2f}");}}
var t=el.querySelector(".iskg-progress-circle-text");
if(t)t.innerText="{int(value * 100)}%";}}'''


# ─── Toast (non-modal notification) ────────────────────────────────────


class Toast:
    """Non-modal transient notification.

    Usage::

        Toast.show(app, "Saved!", variant="success", duration=2000)

    The toast is rendered via ``app.inject_js`` so it overlays any
    running window.
    """

    _counter = 0

    @classmethod
    def show(
        cls,
        app: Any,
        text: str,
        *,
        variant: str = "default",
        duration_ms: int = 3000,
    ) -> None:
        """Show a toast on ``app`` for ``duration_ms`` milliseconds."""
        if variant not in ("default", "success", "warn", "error"):
            variant = "default"
        cls._counter += 1
        toast_id = f"iskg-toast-{cls._counter}"
        app.inject_js(
            f"""
(function(){{
  var t=document.createElement('div');
  t.id='{toast_id}';
  t.className='iskg-toast {variant}';
  t.innerHTML='<span>{text}</span>';
  document.body.appendChild(t);
  setTimeout(function(){{t.style.animation='iskg-fadeOut 0.25s ease-in';setTimeout(function(){{t.remove();}},260);}},{duration_ms});
}})();
"""
        )
