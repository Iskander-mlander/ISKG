"""File-system widgets (browse + pick)."""

from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from typing import Any

from ..base import Widget


def _scan_dir(path: str) -> list[dict]:
    """Return a list of file/dir entries for the JS tree."""
    if not os.path.isdir(path):
        return []
    out: list[dict] = []
    try:
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            try:
                is_dir = os.path.isdir(full)
            except OSError:
                continue
            out.append({"name": name, "path": full, "is_dir": is_dir})
    except (PermissionError, OSError):
        pass
    return out


class FileBrowser(Widget):
    """A read-only file-system tree browser.

    Click a directory to expand it. Click a file to fire a ``"select"``
    event with its full path.

    Args:
        parent: parent widget.
        root: directory to start from. ``~`` is expanded.
        width: viewport width in px.
        height: viewport height in px.
        command: optional callback fired with the selected path.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        root: str = "~",
        width: int = 320,
        height: int = 240,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["root"] = os.path.expanduser(root)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["selected_path"] = ""
        # Pre-build the initial tree snapshot.
        self._tree_cache = self._build_tree(self._config_dict["root"])
        if command is not None:
            self._config_dict["command"] = command

    def _build_tree(self, root: str, depth: int = 0, max_depth: int = 6) -> list[dict]:
        if depth > max_depth:
            return []
        out: list[dict] = []
        for entry in _scan_dir(root):
            node = {
                "name": entry["name"],
                "path": entry["path"],
                "is_dir": entry["is_dir"],
            }
            if entry["is_dir"]:
                node["children"] = self._build_tree(entry["path"], depth + 1, max_depth)
            out.append(node)
        return out

    def refresh(self) -> None:
        """Re-scan the file-system tree from ``root``."""
        self._tree_cache = self._build_tree(self._config_dict["root"])
        self._sync()

    @property
    def root(self) -> str:
        return self._config_dict.get("root", "")

    @root.setter
    def root(self, v: str) -> None:
        self._config_dict["root"] = os.path.expanduser(str(v))
        self._tree_cache = self._build_tree(self._config_dict["root"])
        self._sync()

    @property
    def selected_path(self) -> str:
        return self._config_dict.get("selected_path", "")

    def _render(self) -> str:
        style = self._render_style()
        width = self._config_dict.get("width", 320)
        height = self._config_dict.get("height", 240)
        attrs = self._render_attrs()
        sel = self._config_dict.get("selected_path", "")

        def render_nodes(nodes: list[dict]) -> str:
            parts: list[str] = []
            for n in nodes:
                is_sel = n["path"] == sel
                node_cls = "iskg-fb-node"
                if is_sel:
                    node_cls += " selected"
                if n["is_dir"]:
                    parts.append(
                        f'<li><div class="{node_cls}" data-path="{n["path"]}">📁 {n["name"]}</div>'
                    )
                else:
                    parts.append(
                        f'<li><div class="{node_cls}" data-path="{n["path"]}">📄 {n["name"]}</div>'
                    )
            return "<ul>" + "".join(parts) + "</ul>" if parts else ""

        inner = render_nodes(self._tree_cache)
        return f'''<div id="{self._id}" class="iskg-fb" style="{style}width:{width}px;height:{height}px;overflow:auto;" {attrs}>
  <div class="iskg-fb-root">{self.root}</div>
  {inner}
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-fb-node").forEach(function(n){{
    n.onclick=function(){{
      el.querySelectorAll(".iskg-fb-node.selected").forEach(function(s){{s.classList.remove("selected");}});
      this.classList.add("selected");
      iskg_bridge_event("{self._id}","select",this.getAttribute("data-path"));
    }};
  }});
}})();'''

    def _render_update_js(self) -> str:
        # Re-render the whole tree (refresh triggered). The simpler
        # implementation just emits a sync signal; the JS side already has
        # the cached HTML. To force re-render, call app.update() after
        # refresh() in Python.
        return ""

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "select":
            self._config_dict["selected_path"] = str(event_data or "")
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(self._config_dict["selected_path"])
        super()._handle_bridge_event(event_name, event_data)
