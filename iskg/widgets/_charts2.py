"""Additional chart widgets: BarChart, PieChart, ScatterPlot, Heatmap,
LineChart (multi-series), Sparkline variants.
"""

from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import Any

from ..base import Widget


def _safe_color(i: int, total: int) -> str:
    """Pick a stable IFAZ theme color for a series index."""
    palette = [
        "#22d3ee",  # cyan
        "#4ade80",  # green
        "#f59e0b",  # amber
        "#f43f5e",  # red
        "#a78bfa",  # purple
        "#fb923c",  # orange
        "#34d399",  # emerald
        "#60a5fa",  # blue
    ]
    return palette[i % len(palette)]


# ─── BarChart ──────────────────────────────────────────────────────────


class BarChart(Widget):
    """Vertical bar chart.

    Args:
        parent: parent widget.
        data: list of ``(label, value)`` pairs, or just a list of values.
        width: chart width in px.
        height: chart height in px.
        show_values: if ``True`` show the value at the top of each bar.
        color: bar color (CSS string).
        command: optional ``(label) -> None`` callback when a bar is
            clicked.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        data: list[Any] | None = None,
        width: int = 300,
        height: int = 200,
        show_values: bool = False,
        color: str = "var(--cyan)",
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["data"] = self._normalize(data)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["show_values"] = show_values
        self._config_dict["color"] = color
        if command is not None:
            self._config_dict["command"] = command

    @staticmethod
    def _normalize(data: list[Any] | None) -> list[tuple[str, float]]:
        if not data:
            return []
        out: list[tuple[str, float]] = []
        for i, item in enumerate(data):
            if isinstance(item, tuple) and len(item) == 2:
                out.append((str(item[0]), float(item[1])))
            else:
                out.append((f"#{i + 1}", float(item)))
        return out

    @property
    def data(self) -> list[tuple[str, float]]:
        return list(self._config_dict.get("data", []))

    @data.setter
    def data(self, v: list[Any]) -> None:
        self._config_dict["data"] = self._normalize(v)
        self._sync()

    def _render(self) -> str:
        data = self._config_dict.get("data", [])
        width = self._config_dict.get("width", 300)
        height = self._config_dict.get("height", 200)
        show_values = self._config_dict.get("show_values", False)
        color = self._config_dict.get("color", "var(--cyan)")
        attrs = self._render_attrs()
        if not data:
            return f'<div id="{self._id}" class="iskg-barchart" {attrs}></div>'
        max_v = max((v for _, v in data), default=1) or 1
        bars_html = ""
        bw = (width - 8) / max(1, len(data))
        for i, (label, value) in enumerate(data):
            h = (value / max_v) * (height - 30)
            x = 4 + i * bw
            y = height - 20 - h
            bw_inner = max(2, bw - 4)
            bars_html += (
                f'<rect class="iskg-bc-bar" x="{x:.1f}" y="{y:.1f}" '
                f'width="{bw_inner:.1f}" height="{h:.1f}" '
                f'fill="{color}" data-label="{label}" data-idx="{i}" />'
            )
            if show_values:
                bars_html += (
                    f'<text class="iskg-bc-val" x="{x + bw_inner / 2:.1f}" '
                    f'y="{y - 2:.1f}" text-anchor="middle">{value:g}</text>'
                )
            bars_html += (
                f'<text class="iskg-bc-label" x="{x + bw_inner / 2:.1f}" '
                f'y="{height - 4}" text-anchor="middle">{label}</text>'
            )
        return (
            f'<div id="{self._id}" class="iskg-barchart" '
            f'style="width:{width}px;height:{height}px;" {attrs}>'
            f'<svg width="{width}" height="{height}">{bars_html}</svg>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-bc-bar").forEach(function(b){{
    b.onclick=function(){{iskg_bridge_event("{self._id}","click",b.dataset.label);}};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "click":
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(str(event_data))
        super()._handle_bridge_event(event_name, event_data)

    def _render_update_js(self) -> str:
        return f'var el=document.getElementById("{self._id}");if(el){{el.innerHTML={json.dumps(self._render().split(">", 1)[1].rsplit("<", 1)[0])};}}'


# ─── PieChart ──────────────────────────────────────────────────────────


class PieChart(Widget):
    """Pie chart with SVG.

    Args:
        parent: parent widget.
        data: list of ``(label, value)`` pairs.
        size: chart diameter in px.
        command: optional ``(label) -> None`` callback.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        data: list[Any] | None = None,
        size: int = 200,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["data"] = BarChart._normalize(data)
        self._config_dict["size"] = size
        if command is not None:
            self._config_dict["command"] = command

    @property
    def data(self) -> list[tuple[str, float]]:
        return list(self._config_dict.get("data", []))

    @data.setter
    def data(self, v: list[Any]) -> None:
        self._config_dict["data"] = BarChart._normalize(v)
        self._sync()

    def _render(self) -> str:
        data = self._config_dict.get("data", [])
        size = self._config_dict.get("size", 200)
        attrs = self._render_attrs()
        if not data:
            return f'<div id="{self._id}" class="iskg-piechart" {attrs}></div>'
        total = sum(v for _, v in data) or 1
        r = size / 2 - 2
        cx = cy = size / 2
        angle = -90.0
        slices = ""
        for i, (label, value) in enumerate(data):
            sweep = (value / total) * 360.0
            end = angle + sweep
            large = 1 if sweep > 180 else 0
            import math as _m

            x1 = cx + r * _m.cos(_m.radians(angle))
            y1 = cy + r * _m.sin(_m.radians(angle))
            x2 = cx + r * _m.cos(_m.radians(end))
            y2 = cy + r * _m.sin(_m.radians(end))
            d = f"M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f} Z"
            color = _safe_color(i, len(data))
            slices += (
                f'<path class="iskg-pc-slice" d="{d}" fill="{color}" '
                f'data-label="{label}" data-idx="{i}" />'
            )
            angle = end
        return (
            f'<div id="{self._id}" class="iskg-piechart" '
            f'style="width:{size}px;height:{size}px;" {attrs}>'
            f'<svg width="{size}" height="{size}">{slices}</svg>'
            f"</div>"
        )

    def _render_js(self) -> str:
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  if(!el)return;
  el.querySelectorAll(".iskg-pc-slice").forEach(function(s){{
    s.onclick=function(){{iskg_bridge_event("{self._id}","click",s.dataset.label);}};
  }});
}})();'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "click":
            cmd = self._config_dict.get("command")
            if cmd is not None:
                with contextlib.suppress(Exception):
                    cmd(str(event_data))
        super()._handle_bridge_event(event_name, event_data)


# ─── ScatterPlot ───────────────────────────────────────────────────────


class ScatterPlot(Widget):
    """A scatter plot with optional trend.

    Args:
        parent: parent widget.
        points: list of ``(x, y)`` pairs.
        width: chart width.
        height: chart height.
        color: marker color.
        show_trend: if ``True`` draw a best-fit line.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        points: list[tuple[float, float]] | None = None,
        width: int = 300,
        height: int = 200,
        color: str = "var(--cyan)",
        show_trend: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["points"] = [list(p) for p in (points or [])]
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["color"] = color
        self._config_dict["show_trend"] = show_trend

    @property
    def points(self) -> list[tuple[float, float]]:
        return [tuple(p) for p in self._config_dict.get("points", [])]

    @points.setter
    def points(self, v: list[tuple[float, float]]) -> None:
        self._config_dict["points"] = [list(p) for p in v]
        self._sync()

    def _render(self) -> str:
        points = self._config_dict.get("points", [])
        width = self._config_dict.get("width", 300)
        height = self._config_dict.get("height", 200)
        color = self._config_dict.get("color", "var(--cyan)")
        show_trend = self._config_dict.get("show_trend", False)
        attrs = self._render_attrs()
        if not points:
            return f'<div id="{self._id}" class="iskg-scatter" {attrs}></div>'
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        x_range = x_max - x_min or 1
        y_range = y_max - y_min or 1
        margin = 20
        dots = ""
        for x, y in points:
            px = margin + (x - x_min) / x_range * (width - 2 * margin)
            py = height - margin - (y - y_min) / y_range * (height - 2 * margin)
            dots += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{color}" />'
        trend = ""
        if show_trend and len(points) > 1:
            # Simple linear regression
            n = len(points)
            sx, sy, sxy, sxx = sum(xs), sum(ys), 0, 0
            for x, y in points:
                sxy += x * y
                sxx += x * x
            denom = n * sxx - sx * sx or 1
            slope = (n * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / n
            x1, x2 = x_min, x_max
            y1l = slope * x1 + intercept
            y2l = slope * x2 + intercept
            px1 = margin
            py1 = height - margin - (y1l - y_min) / y_range * (height - 2 * margin)
            px2 = width - margin
            py2 = height - margin - (y2l - y_min) / y_range * (height - 2 * margin)
            trend = (
                f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" '
                f'stroke="var(--green)" stroke-width="1.5" stroke-dasharray="4,2" />'
            )
        return (
            f'<div id="{self._id}" class="iskg-scatter" '
            f'style="width:{width}px;height:{height}px;" {attrs}>'
            f'<svg width="{width}" height="{height}">{trend}{dots}</svg>'
            f"</div>"
        )


# ─── Heatmap ───────────────────────────────────────────────────────────


class Heatmap(Widget):
    """A 2D matrix heatmap (cells coloured by value).

    Args:
        parent: parent widget.
        matrix: 2D list of values (``matrix[row][col]``).
        cmap: name of the colormap (``"viridis"``, ``"inferno"``,
            ``"grayscale"``, ``"ifaz"``). Default ``"ifaz"``.
        cell_size: pixel size of each cell.
    """

    _CMAPS = {
        "ifaz": [
            (0.0, "#0c111a"),
            (0.25, "#1a2636"),
            (0.5, "#22d3ee"),
            (0.75, "#f59e0b"),
            (1.0, "#ef4444"),
        ],
        "viridis": [
            (0.0, "#440154"),
            (0.5, "#21908C"),
            (1.0, "#FDE725"),
        ],
        "inferno": [
            (0.0, "#000004"),
            (0.5, "#BB3754"),
            (1.0, "#FCFFA4"),
        ],
        "grayscale": [
            (0.0, "#000000"),
            (1.0, "#ffffff"),
        ],
    }

    def __init__(
        self,
        parent: Widget | None = None,
        matrix: list[list[float]] | None = None,
        cmap: str = "ifaz",
        cell_size: int = 16,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["matrix"] = matrix or []
        self._config_dict["cmap"] = cmap
        self._config_dict["cell_size"] = cell_size

    @property
    def matrix(self) -> list[list[float]]:
        return self._config_dict.get("matrix", [])

    @matrix.setter
    def matrix(self, v: list[list[float]]) -> None:
        self._config_dict["matrix"] = v
        self._sync()

    def _lerp(self, t: float, cmap: list[tuple[float, str]]) -> str:
        for i in range(len(cmap) - 1):
            a_t, a_c = cmap[i]
            b_t, b_c = cmap[i + 1]
            if a_t <= t <= b_t:
                f = (t - a_t) / (b_t - a_t) if b_t > a_t else 0
                # Simple hex lerp
                ax, ay, az = int(a_c[1:3], 16), int(a_c[3:5], 16), int(a_c[5:7], 16)
                bx, by, bz = int(b_c[1:3], 16), int(b_c[3:5], 16), int(b_c[5:7], 16)
                rx, gy, bz2 = (
                    int(ax + (bx - ax) * f),
                    int(ay + (by - ay) * f),
                    int(az + (bz - az) * f),
                )
                return f"#{rx:02x}{gy:02x}{bz2:02x}"
        return cmap[-1][1]

    def _render(self) -> str:
        matrix = self._config_dict.get("matrix", [])
        cmap_name = self._config_dict.get("cmap", "ifaz")
        cell_size = self._config_dict.get("cell_size", 16)
        attrs = self._render_attrs()
        cmap = self._CMAPS.get(cmap_name, self._CMAPS["ifaz"])
        if not matrix:
            return f'<div id="{self._id}" class="iskg-heatmap" {attrs}></div>'
        rows = len(matrix)
        cols = max((len(r) for r in matrix), default=0)
        all_vals = [v for row in matrix for v in row]
        vmin = min(all_vals) if all_vals else 0
        vmax = max(all_vals) if all_vals else 1
        rng = vmax - vmin or 1
        cells = ""
        for r, row in enumerate(matrix):
            for c, v in enumerate(row):
                t = (v - vmin) / rng
                color = self._lerp(t, cmap)
                cells += (
                    f'<rect x="{c * cell_size}" y="{r * cell_size}" '
                    f'width="{cell_size}" height="{cell_size}" '
                    f'fill="{color}" data-val="{v}">'
                    f"<title>{v}</title></rect>"
                )
        w = cols * cell_size
        h = rows * cell_size
        return (
            f'<div id="{self._id}" class="iskg-heatmap" '
            f'style="width:{w}px;height:{h}px;" {attrs}>'
            f'<svg width="{w}" height="{h}">{cells}</svg></div>'
        )
