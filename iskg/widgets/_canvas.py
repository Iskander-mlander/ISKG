from __future__ import annotations

import base64
import json
from typing import Any

from ..base import Widget


class Canvas(Widget):
    """A drawing surface for shapes and text."""

    def __init__(
        self,
        parent: Widget | None = None,
        width: int = 300,
        height: int = 200,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._canvas_w = width
        self._canvas_h = height
        self._draw_commands: list[tuple] = []
        self._needs_redraw = False

    def _render(self) -> str:
        w = self._canvas_w
        h = self._canvas_h
        style = self._render_style()
        return f'<canvas id="{self._id}" class="iskg-canvas" width="{w}" height="{h}" style="{style}"></canvas>'

    def _render_update_js(self) -> str:
        return self._render_rebuild_js()

    def _render_js(self) -> str:
        return (
            self._render_rebuild_js()
            + f'''
(function(){{
var c=document.getElementById("{self._id}");
if(!c)return;
new ResizeObserver(function(entries){{
  var e=entries[0];
  if(!e)return;
  var r=e.contentRect;
  iskg_bridge_event("{self._id}","resize",JSON.stringify({{width:Math.round(r.width),height:Math.round(r.height)}}));
}}).observe(c);
}})();'''
        )

    def clear(self) -> None:
        self._draw_commands = []
        self._sync()

    def create_rectangle(self, x1: int, y1: int, x2: int, y2: int, **kwargs: Any) -> None:
        self._draw_commands.append(("rect", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_line(self, x1: int, y1: int, x2: int, y2: int, **kwargs: Any) -> None:
        self._draw_commands.append(("line", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_oval(self, x1: int, y1: int, x2: int, y2: int, **kwargs: Any) -> None:
        self._draw_commands.append(("oval", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_text(self, x: int, y: int, text: str = "", **kwargs: Any) -> None:
        self._draw_commands.append(("text", x, y, text, kwargs))
        self._sync()

    def create_arc(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        start: int = 0,
        extent: int = 90,
        **kwargs: Any,
    ) -> None:
        self._draw_commands.append(("arc", x1, y1, x2, y2, start, extent, kwargs))
        self._sync()

    def create_polygon(self, *points: int, **kwargs: Any) -> None:
        self._draw_commands.append(("polygon", points, kwargs))
        self._sync()

    def create_image(self, x: int, y: int, data: bytes, **kwargs: Any) -> None:
        b64 = base64.b64encode(data).decode("ascii")
        self._draw_commands.append(("image", x, y, b64, kwargs))
        self._sync()

    def _render_rebuild_js(self) -> str:
        w = self._canvas_w
        h = self._canvas_h
        cmds = json.dumps(self._draw_commands)
        return f'''(function(){{
var c=document.getElementById("{self._id}");
if(!c)return;
var ctx=c.getContext("2d");
var cmds={cmds};
function drawAll(){{
  ctx.clearRect(0,0,{w},{h});
  for(var i=0;i<cmds.length;i++){{
    var cmd=cmds[i];
    switch(cmd[0]){{
      case "rect":
        ctx.fillStyle=cmd[5].fill||"#4ade80";
        ctx.strokeStyle=cmd[5].outline||"#22d3ee";
        ctx.lineWidth=cmd[5].width||1;
        ctx.fillRect(cmd[1],cmd[2],cmd[3]-cmd[1],cmd[4]-cmd[2]);
        ctx.strokeRect(cmd[1],cmd[2],cmd[3]-cmd[1],cmd[4]-cmd[2]);
        break;
      case "line":
        ctx.strokeStyle=cmd[5].fill||cmd[5].color||"#22d3ee";
        ctx.lineWidth=cmd[5].width||1;
        ctx.beginPath();ctx.moveTo(cmd[1],cmd[2]);ctx.lineTo(cmd[3],cmd[4]);ctx.stroke();
        break;
      case "oval":
        ctx.fillStyle=cmd[5].fill||"transparent";
        ctx.strokeStyle=cmd[5].outline||"#22d3ee";
        ctx.lineWidth=cmd[5].width||1;
        ctx.beginPath();
        ctx.ellipse((cmd[1]+cmd[3])/2,(cmd[2]+cmd[4])/2,(cmd[3]-cmd[1])/2,(cmd[4]-cmd[2])/2,0,0,Math.PI*2);
        ctx.fill();ctx.stroke();
        break;
      case "text":
        ctx.fillStyle=cmd[4].fill||"#c8d6e5";
        ctx.font=cmd[4].font||"11px Share Tech Mono";
        ctx.textAlign=cmd[4].anchor||"start";
        ctx.fillText(cmd[3],cmd[1],cmd[2]);
        break;
      case "arc":
        ctx.fillStyle=cmd[7].fill||"transparent";
        ctx.strokeStyle=cmd[7].outline||"#22d3ee";
        ctx.lineWidth=cmd[7].width||1;
        ctx.beginPath();
        ctx.arc((cmd[1]+cmd[3])/2,(cmd[2]+cmd[4])/2,Math.min((cmd[3]-cmd[1])/2,(cmd[4]-cmd[2])/2),cmd[5]*Math.PI/180,(cmd[5]+cmd[6])*Math.PI/180);
        cmd[7].fill!==undefined?ctx.fill():ctx.stroke();
        break;
      case "polygon":
        ctx.fillStyle=cmd[2].fill||"rgba(78,204,163,0.3)";
        ctx.strokeStyle=cmd[2].outline||"#4ade80";
        ctx.lineWidth=cmd[2].width||2;
        ctx.beginPath();
        ctx.moveTo(cmd[1][0],cmd[1][1]);
        for(var pi=2;pi<cmd[1].length;pi+=2)ctx.lineTo(cmd[1][pi],cmd[1][pi+1]);
        ctx.closePath();ctx.fill();ctx.stroke();
        break;
    }}
  }}
}}
var pending=0;
for(var i=0;i<cmds.length;i++){{
  if(cmds[i][0]==="image"){{
    (function(cmd){{
      pending++;
      var img=new Image();
      img.onload=function(){{
        ctx.drawImage(img,cmd[1],cmd[2],cmd[4].width||img.width,cmd[4].height||img.height);
        pending--;
        if(pending===0)drawAll();
      }};
      img.src="data:image/png;base64,"+cmd[3];
    }})(cmds[i]);
  }}
}}
if(pending===0)drawAll();
}})();'''

    def _sync(self) -> None:
        super()._sync()

    def _render_children(self) -> str:
        return ""

    def _render_children_js(self) -> str:
        return ""


class Knob(Widget):
    """A rotary knob control for adjusting values.

    Config options: ``from``, ``to``, ``value``, ``size`` (pixels),
    ``color``, ``show_value`` (bool), plus all CSS properties.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        from_: int = 0,
        to: int = 100,
        value: float = 0,
        size: int = 60,
        color: str = "cyan",
        show_value: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["size"] = size
        self._config_dict["color"] = color
        self._config_dict["show_value"] = show_value

    @property
    def value(self) -> float:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: float) -> None:
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self) -> str:
        size = self._get_cfg("size", 60)
        show_val = self._get_cfg("show-value", True)
        val = self._get_cfg("value", 0)
        style = self._render_style()
        val_html = f'<span class="iskg-knob-val">{val}</span>' if show_val else ""
        return f'''<div id="{self._id}" class="iskg-knob-wrap" style="{style}width:{size}px;">
  <canvas id="{self._id}-cv" class="iskg-knob-canvas" width="{size}" height="{size}"></canvas>
  {val_html}
</div>'''

    def _render_js(self) -> str:
        size = self._config_dict.get("size", 60)
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 0)
        color = self._config_dict.get("color", "cyan")
        cx = size // 2
        cy = size // 2
        r = cx - 4
        start_angle = 225
        end_angle = 315
        return f'''(function(){{
  if(!window._iskg_knobHandlers){{window._iskg_knobHandlers={{}};
    document.addEventListener("mousemove",function(e){{
      var k=window._iskg_activeKnob,h=k&&window._iskg_knobHandlers[k];
      if(h)h.onMove(e);
    }});
    document.addEventListener("mouseup",function(){{
      window._iskg_activeKnob=null;
    }});
  }}
  var cv=document.getElementById("{self._id}-cv");
  var ctx=cv.getContext("2d");
  var cx={cx},cy={cy},r={r};
  var lo={lo},hi={hi},val={val};
  var arcStart={start_angle},arcSweep={end_angle};
  var color="{color}";
  var colMap={{"green":"#4ade80","red":"#ef4444","amber":"#f59e0b","cyan":"#22d3ee"}};
  var col=colMap[color]||colMap.cyan;
  function draw(v){{
    ctx.clearRect(0,0,cv.width,cv.height);
    var p=Math.max(0,Math.min(1,(v-lo)/(hi-lo)));
    var a=arcStart+p*arcSweep;
    ctx.strokeStyle="#1a2636";
    ctx.lineWidth=6;
    ctx.beginPath(); ctx.arc(cx,cy,r,-(arcStart+arcSweep)*Math.PI/180,-arcStart*Math.PI/180); ctx.stroke();
    ctx.strokeStyle=col;
    ctx.lineWidth=5;
    ctx.shadowColor=col; ctx.shadowBlur=6;
    ctx.beginPath(); ctx.arc(cx,cy,r,-a*Math.PI/180,-arcStart*Math.PI/180); ctx.stroke();
    ctx.shadowBlur=0;
    ctx.fillStyle=col;
    ctx.beginPath(); ctx.arc(cx,cy,3,0,2*Math.PI); ctx.fill();
    var angle=-a*Math.PI/180;
    ctx.strokeStyle=col; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+r*Math.cos(angle),cy+r*Math.sin(angle)); ctx.stroke();
    var sib=document.getElementById("{self._id}").querySelector(".iskg-knob-val");
    if(sib)sib.innerText=Math.round(v);
  }}
  draw(val);
  window.iskg_knob_{self._id}=draw;
  var curVal=val;
  cv.onmousedown=function(){{window._iskg_activeKnob="{self._id}";}};
  cv.onwheel=function(e){{
    e.preventDefault();
    var st=(hi-lo)/100||1;
    curVal+=e.deltaY>0?-st:st;
    curVal=Math.max(lo,Math.min(hi,curVal));
    draw(curVal);
    iskg_bridge_event("{self._id}","change",curVal.toString());
  }};
  window._iskg_knobHandlers["{self._id}"]={{onMove:function(e){{
    var rect=cv.getBoundingClientRect();
    var dx=e.clientX-(rect.left+cx);
    var dy=e.clientY-(rect.top+cy);
    var a=Math.atan2(dy,dx);
    var deg=-a*180/Math.PI;
    deg=(deg+360)%360;
    var da=(deg-arcStart+360)%360;
    var p=da/arcSweep;
    p=Math.max(0,Math.min(1,p));
    curVal=lo+p*(hi-lo);
    draw(curVal);
    iskg_bridge_event("{self._id}","change",curVal.toString());
  }}}};
}})();'''

    def _render_update_js(self) -> str:
        val = self._config_dict.get("value", 0)
        return f"""var fn=window.iskg_knob_{self._id};
if(fn)fn({val});"""
