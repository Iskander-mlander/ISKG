"""Y-axis chart widgets: time-series graph and sparkline."""

from __future__ import annotations

import json
from typing import Any

from ..base import Widget


class TimeSeriesGraph(Widget):
    """A lightweight real-time SVG chart (one or more series).

        Use :meth:`append` to stream values in (the graph keeps only the last
        ``max_pts`` points), or :meth:`replace` to draw a fixed dataset.

    Args:
                parent: parent widget (optional).
                height: SVG height in px.
                series: dict mapping a series name to its colour keyword
                    (``"green"``/``"red"``/``"amber"``/``"cyan"``) or hex.
                    A graph needs at least one series.
                max_pts: how many trailing points to keep per series.
                y_min / y_max: optional fixed Y bounds; ``None`` auto-scales.
                gridlines: draw horizontal gridlines (default ``True``).
                smooth: render the series as smoothed Bézier curves instead of
                    straight polylines (default ``True``).
                kwargs: forwarded to :class:`~iskg.base.Widget`.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        width: int = 300,
        height: int = 80,
        series: dict[str, str] | None = None,
        max_pts: int = 200,
        y_min: float | None = None,
        y_max: float | None = None,
        gridlines: bool = True,
        smooth: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["max_pts"] = max_pts
        self._config_dict["y_min"] = y_min
        self._config_dict["y_max"] = y_max
        self._config_dict["gridlines"] = gridlines
        self._config_dict["smooth"] = smooth
        self._series_cfg = series or {"s0": "cyan"}
        self._data: dict[str, list[float]] = {name: [] for name in self._series_cfg}

    @property
    def series(self) -> list[str]:
        """Names of the chart series."""
        return list(self._series_cfg.keys())

    def _col(self, name: str) -> str:
        mapping = {
            "green": "#4ade80",
            "red": "#ef4444",
            "amber": "#f59e0b",
            "cyan": "#22d3ee",
            "blue": "#60a5fa",
            "magenta": "#e879f9",
        }
        c = self._series_cfg.get(name, "cyan")
        return mapping.get(c, c)

    def append(self, series: str, value: float | None = None) -> None:
        """Append one value to a series, dropping old points.

        With a single-series chart you may call just ``append(value)``.
        """
        if value is None:
            if len(self._data) != 1:
                raise ValueError("series name required when multiple series are present")
            name = next(iter(self._data))
            value = float(series)
        else:
            name = series
            value = float(value)
        values = self._data.setdefault(name, [])
        values.append(value)
        max_pts = self._config_dict.get("max_pts", 200)
        if len(values) > max_pts:
            del values[: len(values) - max_pts]
        self._sync()

    def update(self, value: float) -> None:
        """Append to the first series (convenience for single-series graphs)."""
        self.append(self.series[0], value)

    def replace(self, series: str | list[float], values: list[float] | None = None) -> None:
        """Replace a series with a fixed dataset.

        With a single-series chart you may call ``replace(values)``.
        """
        if values is None:
            if len(self._data) != 1:
                raise ValueError("series name required when multiple series are present")
            name = next(iter(self._data))
            data = [float(v) for v in series]  # type: ignore[union-attr]
        else:
            name = series  # type: ignore[assignment]
            data = [float(v) for v in values]
        self._data[name] = data
        max_pts = int(self._config_dict.get("max_pts", 200))
        if len(self._data[name]) > max_pts:
            self._data[name] = self._data[name][-max_pts:]
        self._sync()

    def clear(self) -> None:
        """Clear all series data."""
        for v in self._data.values():
            v.clear()
        self._sync()

    @property
    def values(self) -> dict[str, list[float]]:
        """A copy of the current data per series."""
        return {name: list(v) for name, v in self._data.items()}

    def _render(self) -> str:
        w = int(self._config_dict.get("width", 300))
        h = int(self._config_dict.get("height", 80))
        style = self._render_style()
        return f'<svg id="{self._id}" class="iskg-chart" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="{style}"></svg>'

    def _render_js(self) -> str:
        return self._render_update_js()

    def _render_update_js(self) -> str:
        w = int(self._config_dict.get("width", 300))
        h = int(self._config_dict.get("height", 80))
        pad = 4
        y_min = self._config_dict.get("y_min")
        y_max = self._config_dict.get("y_max")
        parts: list[str] = []
        if self._config_dict.get("gridlines", True):
            step = max(4, h // 8)
            for y in range(pad, h - pad - 1, step):
                parts.append(
                    f'<line x1="{pad}" y1="{y}" x2="{w - pad}" y2="{y}" '
                    'stroke="#1a2636" stroke-width="1" opacity="0.5"/>'
                )
        for name in self.series:
            vals = self._data.get(name, [])
            if not vals:
                continue
            lo = y_min if y_min is not None else min(vals)
            hi = y_max if y_max is not None else max(vals)
            rng = (hi - lo) or 1.0
            n = len(vals)
            width = w - pad * 2
            height = h - pad * 2
            pts: list[str] = []
            for i, v in enumerate(vals):
                x = pad + (i / max(n - 1, 1)) * width
                y = pad + height - ((v - lo) / rng) * height
                pts.append(f"{x:.1f},{y:.1f}")
            col = self._col(name)
            smooth = self._config_dict.get("smooth", True)
            if smooth and len(pts) >= 3:
                d = self._bezier_path(pts)
                parts.append(
                    f'<path fill="none" stroke="{col}" stroke-width="1.5" '
                    f'stroke-linejoin="round" stroke-linecap="round" d="{d}"/>'
                )
            else:
                line = " ".join(pts)
                parts.append(
                    f'<polyline fill="none" stroke="{col}" stroke-width="1.5" points="{line}"/>'
                )
            last = pts[-1].split(",")
            parts.append(f'<circle cx="{last[0]}" cy="{last[1]}" r="2" fill="{col}"/>')
        svg = "".join(parts)
        return f'''var svg=document.getElementById("{self._id}");
if(svg)svg.innerHTML={json.dumps(svg)};'''

    @staticmethod
    def _bezier_path(pts: list[str]) -> str:
        """Build a smooth SVG path through the points using Catmull-Rom
        splines converted to cubic Béziers."""
        coords = [tuple(float(v) for v in p.split(",")) for p in pts]
        d = f"M{coords[0][0]:.1f},{coords[0][1]:.1f}"
        for i in range(1, len(coords) - 1):
            p0 = coords[i - 1]
            p1 = coords[i]
            p2 = coords[i + 1]
            p3 = coords[i + 2] if i + 2 < len(coords) else p2
            # Catmull-Rom -> cubic Bézier control points
            c1x = p1[0] + (p2[0] - p0[0]) / 6
            c1y = p1[1] + (p2[1] - p0[1]) / 6
            c2x = p2[0] - (p3[0] - p1[0]) / 6
            c2y = p2[1] - (p3[1] - p1[1]) / 6
            d += f"C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        return d

    def __repr__(self) -> str:
        return f"<TimeSeriesGraph {self._id} series={self.series}>"


class Sparkline(TimeSeriesGraph):
    """A compact single-series mini-graph.

    Identical API to :class:`TimeSeriesGraph` (``append``/``replace``/
    ``update``/``clear``); defaults to a smaller, borderless chart.
    """

    def __init__(self, parent: Widget | None = None, **kwargs: Any) -> None:
        kwargs.setdefault("width", 80)
        kwargs.setdefault("height", 24)
        kwargs.setdefault("series", {"s": "green"})
        kwargs.setdefault("max_pts", 60)
        kwargs.setdefault("gridlines", False)
        super().__init__(parent, **kwargs)

    def _render(self) -> str:
        w = int(self._config_dict.get("width", 80))
        h = int(self._config_dict.get("height", 24))
        style = self._render_style()
        return f'<svg id="{self._id}" class="iskg-chart" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="{style}"></svg>'
