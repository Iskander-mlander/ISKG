from __future__ import annotations

from typing import Any

from ..base import Widget


class Tooltip(Widget):
    """A tooltip that appears on hover."""

    _ARIA_ROLE = "tooltip"

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        delay: int = 500,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["delay"] = delay

    def attach(self, target_id: str) -> str:
        text = self._config_dict.get("text", "")
        delay = self._config_dict.get("delay", 500)
        self._tid = target_id
        return f'''(function(){{
  var target=document.getElementById("{target_id}");
  if(!target)return;
  var el=document.createElement("div");
  el.className="iskg-tooltip"; el.innerText="{text}";
  el.style.display="none"; document.body.appendChild(el);
  var timer=null;
  target.onmouseenter=function(e){{
    timer=setTimeout(function(){{
      var r=target.getBoundingClientRect();
      el.style.display="block";
      el.style.left=Math.min(e.clientX,document.documentElement.clientWidth-el.offsetWidth)+"px";
      el.style.top=(r.bottom+4)+"px";
    }},{delay});
  }};
  target.onmouseleave=function(){{clearTimeout(timer);el.style.display="none";}};
}})();'''

    def _render(self) -> str:
        return ""

    def _render_js(self) -> str:
        return ""

    def _render_children_js(self) -> str:
        return ""
