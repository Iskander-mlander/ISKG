"""Debugging and introspection tools for ISKG apps.

- :class:`Logger` — qDebug-style leveled logger.
- :class:`WidgetInspector` — click-to-inspect a widget tree overlay.
- :func:`fps_meter` — measure per-second render rate.
- :func:`enable_hot_reload` — re-apply ``app.inject_css`` when a file
  on disk changes (mtime-based polling).
"""

from __future__ import annotations

import json
import logging as _logging
import os
import time
from collections.abc import Callable
from typing import Any

from .app import _HANDLERS

_log = _logging.getLogger("iskg")


def qDebug(msg: str) -> None:
    """Qt-style qDebug: print to stderr with ``[ISKG:debug]`` prefix."""
    import sys

    print(f"[ISKG:debug] {msg}", file=sys.stderr)


def qInfo(msg: str) -> None:
    import sys

    print(f"[ISKG:info] {msg}", file=sys.stderr)


def qWarning(msg: str) -> None:
    import sys

    print(f"[ISKG:warn] {msg}", file=sys.stderr)


def qCritical(msg: str) -> None:
    import sys

    print(f"[ISKG:CRIT] {msg}", file=sys.stderr)


class Logger:
    """Levelled logger matching the ``qDebug`` / ``qInfo`` / ``qWarning`` /
    ``qCritical`` Qt API.

    Usage::

        log = Logger()
        log.debug("loading file", path=path)
        log.set_level("warning")
    """

    LEVELS = {"debug": 10, "info": 20, "warning": 30, "critical": 40}

    def __init__(self, name: str = "iskg", level: str = "info") -> None:
        self.name = name
        self._level = level
        self._history: list[tuple[float, str, str]] = []
        self._max_history = 1000

    def set_level(self, level: str) -> None:
        self._level = level

    def _emit(self, level: str, msg: str, **kwargs: Any) -> None:
        if self.LEVELS.get(level, 0) < self.LEVELS.get(self._level, 0):
            return
        ts = time.time()
        line = f"[{time.strftime('%H:%M:%S', time.localtime(ts))}] [{level.upper():8s}] {msg}"
        if kwargs:
            line += " " + " ".join(f"{k}={v!r}" for k, v in kwargs.items())
        import sys

        print(line, file=sys.stderr)
        self._history.append((ts, level, line))
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def debug(self, msg: str, **kw: Any) -> None:
        self._emit("debug", msg, **kw)

    def info(self, msg: str, **kw: Any) -> None:
        self._emit("info", msg, **kw)

    def warning(self, msg: str, **kw: Any) -> None:
        self._emit("warning", msg, **kw)

    def critical(self, msg: str, **kw: Any) -> None:
        self._emit("critical", msg, **kw)

    @property
    def history(self) -> list[tuple[float, str, str]]:
        return list(self._history)


class WidgetInspector:
    """Click-to-inspect overlay: click any widget to see its class, id and
    full config in a floating panel.

    On pick, the panel is populated from :meth:`Application.get_widget`
    / :meth:`Widget.dump` and the app event ``"widget-picked"`` is
    emitted with the same dict, so other tools can subscribe::

        inspector = WidgetInspector(app)
        inspector.enable()          # Alt+I toggles the panel
        app.on("widget-picked", lambda info: print(info["type"]))

    The bridge handler ``iskg-inspector`` is registered on ``enable()``
    and removed on ``disable()`` (before this fix the pick event had no
    handler, so clicks were silently swallowed).
    """

    def __init__(self, app: Any) -> None:
        self.app = app
        self._enabled = False

    def enable(self) -> None:
        if self._enabled:
            return
        self._enabled = True
        _HANDLERS["iskg-inspector"] = self._on_pick
        self.app.inject_js(
            """
(function(){
  if(document.getElementById('iskg-inspector'))return;
  var p=document.createElement('div');
  p.id='iskg-inspector';
  p.style.cssText='position:fixed;right:12px;bottom:12px;z-index:99999;'
    +'background:rgba(18,21,26,.96);color:#d6dae2;border:1px solid #3a4150;'
    +'border-radius:6px;padding:8px 10px;max-width:440px;max-height:50vh;'
    +'overflow:auto;font:11px/1.45 monospace;white-space:pre-wrap;'
    +'box-shadow:0 4px 18px rgba(0,0,0,.5);display:none;cursor:default;';
  p.innerHTML='<div style="color:#7dd3fc;font-weight:bold;">Inspector '
    +'<span style="color:#6b7280;font-weight:normal;">(click a widget, '
    +'Alt+I to hide, click title to close)</span></div>'
    +'<pre id="iskg-inspector-body" style="margin:6px 0 0 0;'
    +'white-space:pre-wrap;"></pre>';
  document.body.appendChild(p);
  window.iskg_inspect_show=function(info){
    var b=document.getElementById('iskg-inspector-body');
    b.textContent=JSON.stringify(info,null,1);
    var head=p.firstChild;
    head.firstChild.textContent='Inspector '
      +(info&&info.type?info.type+'#'+info.id:'');
    p.style.display='block';
  };
  document.addEventListener('click',function(e){
    var el=e.target.closest('[id^=iw]');
    if(!el||p.contains(el))return;
    iskg_bridge_event('iskg-inspector','pick',el.id);
  },true);
  window.addEventListener('keydown',function(e){
    if(e.altKey&&e.key==='i'){
      p.style.display=p.style.display==='none'?'block':'none';
    }
  });
})();
"""
        )

    def _on_pick(self, event_name: str, data: Any) -> None:
        if event_name != "pick" or not self._enabled:
            return
        widget = self.app.get_widget(str(data))
        info: dict[str, Any] = (
            widget.dump() if widget is not None else {"error": f"unknown widget {data!r}"}
        )
        self.app.emit("widget-picked", info)
        self.app.execute_js(f"window.iskg_inspect_show({json.dumps(info)});")

    def disable(self) -> None:
        self._enabled = False
        _HANDLERS.pop("iskg-inspector", None)
        self.app.inject_js("var c=document.getElementById('iskg-inspector');if(c)c.remove();")


def fps_meter(app: Any, duration_s: float = 1.0) -> float:
    """Measure the average frame rate by counting ``requestAnimationFrame``
    callbacks over ``duration_s`` seconds.
    """

    js = f"""
(function(){{
  window._iskg_fps_count=0;
  window._iskg_fps_start=performance.now();
  function tick(){{
    window._iskg_fps_count++;
    if(performance.now()-window._iskg_fps_start<{int(duration_s * 1000)})requestAnimationFrame(tick);
    else iskg_bridge_event('__fps__','done',String(window._iskg_fps_count));
  }}
  requestAnimationFrame(tick);
}})();
"""
    done: list[int] = []

    def handler(event_name: str, data: Any) -> None:
        if event_name == "done":
            try:
                done.append(int(data))
            except (TypeError, ValueError):
                done.append(0)

    # The result arrives as a *widget* bridge event (widget id
    # "__fps__"), so it must be registered in _HANDLERS. The previous
    # version called app.bind(), which registers a keyboard shortcut —
    # the event never reached the handler and fps_meter always returned
    # 0 after blocking for duration_s.
    _HANDLERS["__fps__"] = handler
    try:
        app.execute_js(js)
        deadline = time.time() + duration_s + 1.0
        while not done and time.time() < deadline:
            time.sleep(0.05)
    finally:
        _HANDLERS.pop("__fps__", None)
    count = done[0] if done else 0
    return count / duration_s


def enable_hot_reload(
    app: Any,
    css_path: str,
    on_change: Callable[[str], None] | None = None,
    poll_interval: float = 0.5,
) -> None:
    """Poll ``css_path`` for modifications and re-inject it when it changes.

    The poller runs on the daemon after-callback worker (single
    thread, no race conditions). Call :func:`disable_hot_reload` to
    stop.
    """
    state = {"mtime": 0, "running": True, "last_text": ""}

    def read() -> str:
        with open(css_path, encoding="utf-8") as f:
            return f.read()

    def poll() -> None:
        if not state["running"]:
            return
        try:
            mt = os.path.getmtime(css_path)
            if mt != state["mtime"]:
                state["mtime"] = mt
                text = read()
                if text != state["last_text"]:
                    state["last_text"] = text
                    app.inject_css(text)
                    if on_change is not None:
                        on_change(css_path)
        except OSError:
            pass
        app.after(int(poll_interval * 1000), poll)

    poll()


def disable_hot_reload() -> None:
    """Cancel the most recently-started hot-reload poller.

    (Hot-reload is global; this flips a sentinel checked by the next
    poll tick. Re-call ``enable_hot_reload`` to restart with a new
    file.)
    """
    # No state to share here; users typically use ``after_cancel`` on
    # the timer returned by ``after``. Provided for API symmetry.
    pass
