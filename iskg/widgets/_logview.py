"""Scrollable, colour-coded log output widget."""

from __future__ import annotations

import html as _html
from typing import Any

from ..base import Widget

LEVEL_COLORS = {
    "DEBUG": "#64748b",
    "INFO": "#22d3ee",
    "WARN": "#f59e0b",
    "ERROR": "#ef4444",
    "CRITICAL": "#f43f5e",
}


class LogViewer(Widget):
    """A read-only, auto-scrolling log output area.

    Lines are colour-coded by severity level and the most recent lines are
    shown at the bottom. Old lines beyond ``max_lines`` are dropped.

    Args:
        parent: parent widget (optional).
        height: visible height in px.
        max_lines: max lines kept before trimming.
        show_timestamp: prefix each line with an ISO timestamp
            (default ``False``).
        autoscroll: always keep the view scrolled to the newest line
            (default ``True``).
        kwargs: forwarded to :class:`~iskg.base.Widget`.
    """

    _ARIA_ROLE = "log"

    def __init__(
        self,
        parent: Widget | None = None,
        height: int = 150,
        max_lines: int = 500,
        show_timestamp: bool = False,
        autoscroll: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["height"] = height
        self._config_dict["max_lines"] = max_lines
        self._config_dict["show_timestamp"] = show_timestamp
        self._config_dict["autoscroll"] = autoscroll
        self._lines: list[tuple[str, str]] = []

    @property
    def lines(self) -> list[tuple[str, str]]:
        """(severity, text) pairs currently shown."""
        return list(self._lines)

    def append(self, text: str, level: str = "INFO") -> LogViewer:
        """Append a line to the log.

        Args:
            text: message (may contain multiple lines separated by ``\\n``).
            level: one of ``"DEBUG"``, ``"INFO"``, ``"WARN"``, ``"ERROR"``,
                ``"CRITICAL"``.

        Returns:
            self (for chaining).
        """
        level = level.upper()
        for part in str(text).split("\n"):
            if part == "":
                continue
            self._lines.append((level, part))
        max_lines = int(self._config_dict.get("max_lines", 500))
        if len(self._lines) > max_lines:
            del self._lines[: len(self._lines) - max_lines]
        self._sync()
        return self

    def clear(self) -> LogViewer:
        """Clear all lines."""
        self._lines.clear()
        self._sync()
        return self

    def _line_html(self) -> str:
        out: list[str] = []
        for level, msg in self._lines:
            color = LEVEL_COLORS.get(level, "#c8d6e5")
            ts = ""
            if self._config_dict.get("show_timestamp"):
                from datetime import datetime

                ts = f'<span class="iskg-log-ts">{datetime.now().isoformat(timespec="seconds")}</span>'
            out.append(
                f'<div class="iskg-log-line" data-level="{level}">'
                f'<span class="iskg-log-badge" style="color:{color}">[{level}]</span> '
                f"{ts}<span>{_html.escape(msg)}</span></div>"
            )
        return "".join(out)

    def _render(self) -> str:
        height = int(self._config_dict.get("height", 150))
        style = self._render_style()
        attrs = self._render_attrs()
        return (
            f'<div id="{self._id}" class="iskg-logviewer" style="{style}height:{height}px;" {attrs}>'
            f'<div class="iskg-log-content">{self._line_html()}</div>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
var el=document.getElementById("{self._id}");
if(!el)return;
var auto=el.getAttribute("data-autoscroll");
if(auto==="false")return;
var content=el.querySelector(".iskg-log-content");
if(content)content.scrollTop=content.scrollHeight;
}})();'''

    def _render_update_js(self) -> str:
        import json

        html = self._line_html()
        autoscroll = "true" if self._config_dict.get("autoscroll", True) else "false"
        return (
            f'var el=document.getElementById("{self._id}");'
            f"if(!el)return;"
            f'var content=el.querySelector(".iskg-log-content");'
            f"if(content){{content.innerHTML={json.dumps(html)};"
            f"if({autoscroll})content.scrollTop=content.scrollHeight;}}"
        )

    def __repr__(self) -> str:
        return f"<LogViewer {self._id} {len(self._lines)} lines>"
