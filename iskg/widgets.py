import json
from .base import Widget


class Label(Widget):
    def __init__(self, parent=None, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value):
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self):
        text = self._config_dict.get("text", "")
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cls = "iskg-label"
        color = self._config_dict.get("color", "")
        if color:
            cls += f" {color}"
        style = self._render_style()
        return f'<span id="{self._id}" class="{cls}" style="{style}">{escaped}</span>'

    def _render_update_js(self):
        text = self._config_dict.get("text", "")
        escaped = text.replace("\\", "\\\\").replace("'", "\\'")
        return f'iskg_set_text("{self._id}","{escaped}");'


class Button(Widget):
    def __init__(self, parent=None, text="", command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value):
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self):
        text = self._config_dict.get("text", "")
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cls = "iskg-btn"
        style = self._render_style()
        variant = self._config_dict.get("variant", "")
        if variant:
            cls += f" {variant}"
        size = self._config_dict.get("size", "")
        if size:
            cls += f" {size}"
        disabled = "disabled" if self._config_dict.get("disabled") else ""
        width = self._config_dict.get("width", "")
        if width:
            style += f"width:{width}px;"
        return f'<button id="{self._id}" class="{cls}" style="{style}" {disabled}>{escaped}</button>'

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onclick=function(){{
  iskg_bridge_event("{self._id}","click","");
}};'''

    def _render_update_js(self):
        text = self._config_dict.get("text", "")
        escaped = text.replace("\\", "\\\\").replace("'", "\\'")
        return f'iskg_set_text("{self._id}","{escaped}");'


class Entry(Widget):
    def __init__(self, parent=None, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = str(text)

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value):
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self):
        val = self._config_dict.get("text", "")
        escaped = val.replace("&", "&amp;").replace('"', "&quot;")
        placeholder = self._config_dict.get("placeholder", "")
        placeholder_attr = f' placeholder="{placeholder}"' if placeholder else ""
        width = self._config_dict.get("width", 150)
        style = self._render_style() + f"width:{width}px;"
        disabled = "disabled" if self._config_dict.get("disabled") else ""
        input_type = "password" if self._config_dict.get("password") else "text"
        return f'<input id="{self._id}" class="iskg-entry" type="{input_type}" value="{escaped}"{placeholder_attr} style="{style}" {disabled}/>'

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onchange=function(){{
  iskg_bridge_event("{self._id}","change",this.value);
}};
document.getElementById("{self._id}").oninput=function(){{
  iskg_bridge_event("{self._id}","input",this.value);
}};'''

    def _render_update_js(self):
        parts = []
        val = self._config_dict.get("text", "")
        escaped = val.replace("\\", "\\\\").replace("'", "\\'")
        parts.append(f'iskg_set_value("{self._id}","{escaped}");')
        pw = "password" if self._config_dict.get("password") else "text"
        parts.append(f'iskg_set_attr("{self._id}","type","{pw}");')
        return ";".join(parts)


class CheckBox(Widget):
    def __init__(self, parent=None, text="", checked=False, command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["checked"] = checked

    @property
    def checked(self):
        return self._config_dict.get("checked", False)

    @checked.setter
    def checked(self, value):
        self._config_dict["checked"] = bool(value)
        self._sync()

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value):
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self):
        text = self._config_dict.get("text", "")
        checked = self._config_dict.get("checked", False)
        cls = "iskg-check-wrap"
        if self._config_dict.get("disabled"):
            cls += " disabled"
        check_cls = "iskg-check" + (" checked" if checked else "")
        style = self._render_style()
        return f'''<label id="{self._id}" class="{cls}" style="{style}">
  <span class="{check_cls}"></span>
  <span>{text}</span>
</label>'''

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onclick=function(){{
  var c=this.querySelector(".iskg-check");
  c.classList.toggle("checked");
  iskg_bridge_event("{self._id}","change",c.classList.contains("checked")?"true":"false");
}};'''

    def _render_update_js(self):
        checked = self._config_dict.get("checked", False)
        action = "add" if checked else "remove"
        return (
            f'iskg_{action}_class("{self._id}","checked");'
            if False
            else f'var el=document.getElementById("{self._id}");if(el)el.querySelector(".iskg-check").classList.toggle("checked",{json.dumps(checked)});'
        )


class RadioButton(Widget):
    def __init__(
        self, parent=None, text="", value=None, variable=None, command=None, **kwargs
    ):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["value"] = value
        self._group = variable

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value):
        self._config_dict["text"] = str(value)
        self._sync()

    @property
    def value(self):
        return self._config_dict.get("value")

    @value.setter
    def value(self, v):
        self._config_dict["value"] = v

    @property
    def selected(self):
        if self._group:
            return self._group.get() == self.value
        return self._config_dict.get("selected", False)

    @selected.setter
    def selected(self, v):
        self._config_dict["selected"] = bool(v)
        if self._group and bool(v):
            self._group.set(self.value)
        self._sync()

    def _render(self):
        text = self._config_dict.get("text", "")
        sel = self.selected
        cls = "iskg-radio-wrap"
        if self._config_dict.get("disabled"):
            cls += " disabled"
        radio_cls = "iskg-radio" + (" checked" if sel else "")
        style = self._render_style()
        return f'''<label id="{self._id}" class="{cls}" style="{style}">
  <span class="{radio_cls}"></span>
  <span>{text}</span>
</label>'''

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onclick=function(){{
  var parent=this.parentElement;
  if(parent){{
    var siblings=parent.querySelectorAll(".iskg-radio-wrap");
    for(var i=0;i<siblings.length;i++){{
      siblings[i].querySelector(".iskg-radio").classList.remove("checked");
    }}
  }}
  this.querySelector(".iskg-radio").classList.add("checked");
  iskg_bridge_event("{self._id}","change","selected");
}};'''

    def _render_update_js(self):
        sel = self.selected
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-radio").classList.toggle("checked",{json.dumps(sel)});'''


class ComboBox(Widget):
    def __init__(self, parent=None, values=None, current=0, command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["values"] = values or []
        self._config_dict["current"] = current

    @property
    def current(self):
        return self._config_dict.get("current", 0)

    @current.setter
    def current(self, idx):
        self._config_dict["current"] = int(idx)
        self._sync()

    @property
    def value(self):
        vals = self._config_dict.get("values", [])
        idx = self._config_dict.get("current", 0)
        return vals[idx] if 0 <= idx < len(vals) else ""

    def _render(self):
        vals = self._config_dict.get("values", [])
        cur = self._config_dict.get("current", 0)
        cur_text = vals[cur] if vals and 0 <= cur < len(vals) else ""
        style = self._render_style()
        width = self._config_dict.get("width", 140)
        items_html = "".join(
            f'<div class="iskg-cb-item" data-idx="{i}">{v}</div>'
            for i, v in enumerate(vals)
        )
        return f'''<div id="{self._id}" class="iskg-cb-wrap" style="{style}width:{width}px;">
  <div class="iskg-cb-display" id="{self._id}-disp">
    <span id="{self._id}-text">{cur_text}</span>
    <span class="iskg-cb-arrow">▾</span>
  </div>
  <div class="iskg-cb-drop" id="{self._id}-drop" style="display:none;">
    {items_html}
  </div>
</div>'''

    def _render_js(self):
        return f'''(function(){{
var wrap=document.getElementById("{self._id}");
var disp=document.getElementById("{self._id}-disp");
var drop=document.getElementById("{self._id}-drop");
var text=document.getElementById("{self._id}-text");
function closeDrop(){{drop.style.display="none";wrap.classList.remove("iskg-cb-open");}}
disp.onclick=function(e){{e.stopPropagation();
  var isOpen=drop.style.display=="block";
  document.querySelectorAll(".iskg-cb-drop").forEach(function(d){{d.style.display="none";}});
  document.querySelectorAll(".iskg-cb-wrap").forEach(function(w){{w.classList.remove("iskg-cb-open");}});
  if(!isOpen){{drop.style.display="block";wrap.classList.add("iskg-cb-open");}}
}};
drop.onclick=function(e){{var item=e.target.closest(".iskg-cb-item");
  if(item){{var idx=item.dataset.idx;
    text.innerText=item.innerText;
    closeDrop();
    iskg_bridge_event("{self._id}","change",idx);
  }}
}};
document.addEventListener("click",function(e){{
  if(!wrap.contains(e.target))closeDrop();
}});
}})();'''

    def _render_update_js(self):
        cur = self._config_dict.get("current", 0)
        vals = self._config_dict.get("values", [])
        cur_text = vals[cur] if vals and 0 <= cur < len(vals) else ""
        return f'''var t=document.getElementById("{self._id}-text");
if(t)t.innerText="{cur_text}";
var items=document.querySelectorAll("#{self._id}-drop .iskg-cb-item");
items.forEach(function(x,i){{x.classList.toggle("iskg-cb-sel",i=={cur});}});'''


class Slider(Widget):
    def __init__(
        self,
        parent=None,
        from_=0,
        to=100,
        value=0,
        orient="horizontal",
        command=None,
        **kwargs,
    ):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["orient"] = orient

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self):
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 0)
        orient = self._config_dict.get("orient", "horizontal")
        show_val = self._config_dict.get("show_value", True)
        style = self._render_style()
        width = self._config_dict.get("width", 150)

        if orient == "vertical":
            vlen = self._config_dict.get("height", 100)
            slider_cls = "iskg-slider-vert"
            track_cls = "iskg-slider-vert-track"
            wrap_style = f"{style}flex-direction:column;align-items:center;gap:4px;"
            slider_style = f"width:{vlen}px;height:4px;"
            track_style = f"width:30px;height:{vlen}px;"
            val_html = (
                f'<span class="iskg-slider-val-center">{val}</span>' if show_val else ""
            )
            return f'''<div class="iskg-slider-wrap" style="{wrap_style}">
  <div class="{track_cls}" style="{track_style}">
    <input id="{self._id}" class="{slider_cls}" type="range" min="{lo}" max="{hi}" value="{val}" style="{slider_style}"/>
  </div>
  {val_html}
</div>'''
        else:
            slider_cls = "iskg-slider"
            wrap_style = f"{style}width:{width}px;"
            slider_style = f"width:{width}px;"
            val_html = f'<span class="iskg-slider-val">{val}</span>' if show_val else ""
            return f'''<div class="iskg-slider-wrap" style="{wrap_style}">
  <input id="{self._id}" class="{slider_cls}" type="range" min="{lo}" max="{hi}" value="{val}" style="{slider_style}"/>
  {val_html}
</div>'''

    def _render_js(self):
        return f'''var el=document.getElementById("{self._id}");
el.oninput=function(){{
  var v=parseFloat(this.value);
  var wrap=this.closest(".iskg-slider-wrap");
  if(wrap){{
    var sib=wrap.querySelector(".iskg-slider-val,.iskg-slider-val-center");
    if(sib)sib.innerText=v;
  }}
  iskg_bridge_event("{self._id}","change",v.toString());
}};
el.onwheel=function(e){{
  e.preventDefault();
  var step=(parseFloat(this.max)-parseFloat(this.min))/100||1;
  this.value=parseFloat(this.value)+(e.deltaY>0?-step:step);
  var evt=new Event("input",{{bubbles:true}});
  this.dispatchEvent(evt);
}};'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.value={val};
var wrap=el.closest(".iskg-slider-wrap");
if(wrap){{
  var sib=wrap.querySelector(".iskg-slider-val,.iskg-slider-val-center");
  if(sib)sib.innerText={val};
}}}}'''


class ProgressBar(Widget):
    def __init__(self, parent=None, value=0, max_=100, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["value"] = value
        self._config_dict["max"] = max_

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self):
        val = self._config_dict.get("value", 0)
        mx = self._config_dict.get("max", 100)
        pct = min(100, max(0, (val / mx * 100))) if mx > 0 else 0
        show_text = self._config_dict.get("show_text", False)
        style = self._render_style()
        width = self._config_dict.get("width", 200)
        text_html = ""
        if show_text:
            text_html = f'<span class="iskg-progress-text">{int(pct)}%</span>'
        return f'''<div class="iskg-progress-wrap" id="{self._id}-wrap" style="{style}width:{width}px;">
  <div class="iskg-progress-fill" id="{self._id}" style="width:{pct}%"></div>
  {text_html}
</div>'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        mx = self._config_dict.get("max", 100)
        pct = min(100, max(0, (val / mx * 100))) if mx > 0 else 0
        return f'''var el=document.getElementById("{self._id}");
if(el)el.style.width="{pct}%";
var t=document.getElementById("{self._id}-wrap").querySelector(".iskg-progress-text");
if(t)t.innerText="{int(pct)}%";'''


class Frame(Widget):
    def __init__(self, parent=None, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._pack_layout = None
        self._grid_layout = None

    def _detect_layout(self):
        has_pack = any(
            c._layout_mode == "pack" for c in self._children if not c._destroyed
        )
        has_grid = any(
            c._layout_mode == "grid" for c in self._children if not c._destroyed
        )
        if has_grid:
            return "grid"
        return "pack"

    def _render(self):
        text = self._config_dict.get("text", "")
        style = self._render_style()
        flex = self._config_dict.get("flex", "")
        if flex:
            style += f"flex:{flex};"
        min_h = self._config_dict.get("min_height", "")
        if min_h:
            style += f"min-height:{min_h}px;overlow:auto;"

        layout_type = self._detect_layout()

        header = ""
        if text:
            header = f'<div class="iskg-frame-header"><span class="hdr-dot"></span> {text}</div>'

        has_grid = any(
            c._layout_mode == "grid" for c in self._children if not c._destroyed
        )

        children_html = ""
        for child in self._children:
            if not child._destroyed:
                children_html += child._render()

        if not children_html:
            children_html = ""
        elif has_grid:
            children_html = f'<div class="iskg-grid" style="display:grid;gap:3px;min-height:0;min-width:0;">{children_html}</div>'
        else:
            children_html = f'<div style="display:flex;flex-wrap:wrap;gap:3px;min-height:0;min-width:0;">{children_html}</div>'

        return f'''<div id="{self._id}" class="iskg-frame" style="{style}">
{header}{children_html}</div>'''


class ListBox(Widget):
    def __init__(self, parent=None, items=None, command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["items"] = items or []

    def insert(self, idx, item):
        items = self._config_dict["items"]
        items.insert(idx, item)
        self._sync()

    def append(self, item):
        self._config_dict["items"].append(item)
        self._sync()

    def delete(self, idx):
        items = self._config_dict["items"]
        if 0 <= idx < len(items):
            items.pop(idx)
            self._sync()

    def clear(self):
        self._config_dict["items"] = []
        self._sync()

    @property
    def items(self):
        return self._config_dict.get("items", [])

    @items.setter
    def items(self, vals):
        self._config_dict["items"] = list(vals)
        self._sync()

    def _render(self):
        items = self._config_dict.get("items", [])
        style = self._render_style()
        width = self._config_dict.get("width", 150)
        height = self._config_dict.get("height", 120)
        item_html = ""
        for i, item in enumerate(items):
            item_html += f'<div class="iskg-listbox-item" data-idx="{i}">{item}</div>'
        return f'<div id="{self._id}" class="iskg-listbox" style="{style}width:{width}px;height:{height}px;">{item_html}</div>'

    def _render_js(self):
        return f'''document.getElementById("{self._id}").addEventListener("click",function(e){{
  var item=e.target.closest(".iskg-listbox-item");
  if(item){{
    this.querySelectorAll(".iskg-listbox-item").forEach(function(x){{x.classList.remove("selected");}});
    item.classList.add("selected");
    iskg_bridge_event("{self._id}","change",item.dataset.idx);
  }}
}});'''

    def _render_update_js(self):
        items = self._config_dict.get("items", [])
        escaped = json.dumps(items)
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.innerHTML={escaped}.map(function(x,i){{
  return '<div class=\"iskg-listbox-item\" data-idx=\"'+i+'\">'+x+'</div>';
}}).join("");}}'''


class ScrollBar(Widget):
    def __init__(self, parent=None, orient="vertical", value=0, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["orient"] = orient
        self._config_dict["value"] = value

    def _render(self):
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

    def _render_js(self):
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

    def _render_update_js(self):
        orient = self._config_dict.get("orient", "vertical")
        val = self._config_dict.get("value", 0)
        pos_prop = "top" if orient == "vertical" else "left"
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-scrollbar-thumb").style.{pos_prop}="{val}%";'''


class Text(Widget):
    def __init__(self, parent=None, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = str(text)

    @property
    def text(self):
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, val):
        self._config_dict["text"] = str(val)
        self._sync()

    def append(self, text):
        self._config_dict["text"] += str(text)
        self._sync()

    def clear(self):
        self._config_dict["text"] = ""
        self._sync()

    def _render(self):
        val = self._config_dict.get("text", "")
        escaped = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        style = self._render_style()
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 100)
        disabled = "disabled" if self._config_dict.get("disabled") else ""
        return f'<textarea id="{self._id}" class="iskg-text" style="{style}width:{width}px;height:{height}px;" {disabled}>{escaped}</textarea>'

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onchange=function(){{
  iskg_bridge_event("{self._id}","change",this.value);
}};'''

    def _render_update_js(self):
        val = self._config_dict.get("text", "")
        escaped = val.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f'iskg_set_text("{self._id}","{escaped}");'


class SpinBox(Widget):
    def __init__(self, parent=None, from_=0, to=100, value=0, command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = int(v)
        self._sync()

    def _render(self):
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 0)
        style = self._render_style()
        return f'''<div class="iskg-spinbox-wrap" style="{style}">
  <input id="{self._id}" class="iskg-spinbox" type="text" value="{val}" readonly/>
  <div class="iskg-spinbox-btns">
    <button class="iskg-spinup" id="{self._id}-up">▲</button>
    <button class="iskg-spindown" id="{self._id}-dn">▼</button>
  </div>
</div>'''

    def _render_js(self):
        return f'''document.getElementById("{self._id}-up").onclick=function(){{
  var inp=document.getElementById("{self._id}");
  var v=parseInt(inp.value)||0;
  if(v<{self._config_dict["to"]}){{v++;inp.value=v;iskg_bridge_event("{self._id}","change",v.toString());}}
}};
document.getElementById("{self._id}-dn").onclick=function(){{
  var inp=document.getElementById("{self._id}");
  var v=parseInt(inp.value)||0;
  if(v>{self._config_dict["from"]}){{v--;inp.value=v;iskg_bridge_event("{self._id}","change",v.toString());}}
}};'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        return f'document.getElementById("{self._id}").value={val};'


class Separator(Widget):
    def __init__(self, parent=None, orient="horizontal", **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["orient"] = orient

    def _render(self):
        orient = self._config_dict.get("orient", "horizontal")
        cls = "iskg-vsep" if orient == "vertical" else "iskg-hsep"
        style = self._render_style()
        if orient == "vertical":
            height = self._config_dict.get("height", 50)
            return (
                f'<hr class="{cls}" id="{self._id}" style="{style}height:{height}px;"/>'
            )
        width = self._config_dict.get("width", "100%")
        return f'<hr class="{cls}" id="{self._id}" style="{style}width:{width}px;"/>'


class Notebook(Widget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._tabs = []

    def add_tab(self, title, widget):
        self._tabs.append({"title": title, "widget": widget})
        widget._parent = self
        self._children.append(widget)
        return widget

    def _render(self):
        style = self._render_style()
        tabs_html = ""
        pages_html = ""
        for i, tab in enumerate(self._tabs):
            active = " active" if i == 0 else ""
            tabs_html += (
                f'<div class="iskg-tab{active}" data-idx="{i}">{tab["title"]}</div>'
            )
            page_style = "display:block;" if i == 0 else "display:none;"
            pages_html += f'<div class="iskg-tabpage" id="{self._id}-page-{i}" style="{page_style}">{tab["widget"]._render()}</div>'
        return f'''<div id="{self._id}" class="iskg-notebook" style="{style}">
  <div class="iskg-tabbar">{tabs_html}</div>
  {pages_html}
</div>'''

    def _render_js(self):
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


class Canvas(Widget):
    def __init__(self, parent=None, width=300, height=200, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["canvas_width"] = width
        self._config_dict["canvas_height"] = height
        self._draw_commands = []
        self._needs_redraw = False

    def _render(self):
        w = self._config_dict.get("canvas_width", 300)
        h = self._config_dict.get("canvas_height", 200)
        style = self._render_style()
        return f'<canvas id="{self._id}" class="iskg-canvas" width="{w}" height="{h}" style="{style}"></canvas>'

    def _render_update_js(self):
        return ""

    def _render_js(self):
        return f'''(function(){{
var c=document.getElementById("{self._id}");
if(!c)return;
var ctx=c.getContext("2d");
ctx.fillStyle="#040810";
ctx.fillRect(0,0,c.width,c.height);
}})();'''

    def clear(self):
        self._draw_commands = []
        self._sync()

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        self._draw_commands.append(("rect", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_line(self, x1, y1, x2, y2, **kwargs):
        self._draw_commands.append(("line", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_oval(self, x1, y1, x2, y2, **kwargs):
        self._draw_commands.append(("oval", x1, y1, x2, y2, kwargs))
        self._sync()

    def create_text(self, x, y, text="", **kwargs):
        self._draw_commands.append(("text", x, y, text, kwargs))
        self._sync()

    def create_arc(self, x1, y1, x2, y2, start=0, extent=90, **kwargs):
        self._draw_commands.append(("arc", x1, y1, x2, y2, start, extent, kwargs))
        self._sync()

    def _render_rebuild_js(self):
        w = self._config_dict.get("canvas_width", 300)
        h = self._config_dict.get("canvas_height", 200)
        cmds = json.dumps(self._draw_commands)
        return f'''(function(){{
var c=document.getElementById("{self._id}");
if(!c)return;
var ctx=c.getContext("2d");
ctx.clearRect(0,0,{w},{h});
var cmds={cmds};
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
  }}
}}
}})();'''

    def _sync(self):
        if self._app and self._app._running:
            js = self._render_rebuild_js()
            if js:
                self._app._eval_js(js)

    def _render_children(self):
        return ""

    def _render_children_js(self):
        return ""


class Scale(Widget):
    def __init__(
        self,
        parent=None,
        from_=0,
        to=100,
        value=0,
        orient="horizontal",
        command=None,
        **kwargs,
    ):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["orient"] = orient

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self):
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 0)
        orient = self._config_dict.get("orient", "horizontal")
        style = self._render_style()
        width = self._config_dict.get("width", 200)

        if orient == "horizontal":
            return f'''<div class="iskg-scale-wrap" style="{style}width:{width}px;">
  <div class="iskg-scale-labels"><span>{lo}</span><span>{hi}</span></div>
  <input id="{self._id}" class="iskg-slider" type="range" min="{lo}" max="{hi}" value="{val}" style="width:100%;"/>
</div>'''
        else:
            height = self._config_dict.get("height", 200)
            return f'''<div class="iskg-scale-wrap" style="{style}height:{height}px;align-items:center;">
  <span>{hi}</span>
  <div class="iskg-slider-vert-track" style="flex:1;width:30px;">
    <input id="{self._id}" class="iskg-slider-vert" type="range" min="{lo}" max="{hi}" value="{val}" style="width:{height}px;height:4px;"/>
  </div>
  <span>{lo}</span>
</div>'''

    def _render_js(self):
        return f'''var el=document.getElementById("{self._id}");
el.oninput=function(){{
  iskg_bridge_event("{self._id}","change",this.value);
}};
el.onwheel=function(e){{
  e.preventDefault();
  var step=(parseFloat(this.max)-parseFloat(this.min))/100||1;
  this.value=parseFloat(this.value)+(e.deltaY>0?-step:step);
  var evt=new Event("input",{{bubbles:true}});
  this.dispatchEvent(evt);
}};'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        return f'document.getElementById("{self._id}").value={val};'


class MessageDialog(Widget):
    def __init__(self, parent=None, title="", text="", buttons=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["_dialog_title"] = title
        self._config_dict["_dialog_text"] = text
        self._config_dict["_dialog_buttons"] = buttons or ["OK"]

    def show(self, app=None):
        a = app or self.app
        if not a:
            return
        need_show_js = json.dumps(self._render())
        a._eval_js(
            f"(function(){{"
            f'var e=document.getElementById("{self._id}-ov");'
            f"if(!e){{"
            f'document.body.insertAdjacentHTML("beforeend",{need_show_js});'
            f"}}"
            f'window.location.hash="{self._id}-ov";'
            f"}})()"
        )

    def _render(self):
        title = self._config_dict.get("_dialog_title", "")
        text = self._config_dict.get("_dialog_text", "")
        buttons = self._config_dict.get("_dialog_buttons", ["OK"])
        btns_html = "".join(
            f'<button class="iskg-btn" onclick="window.location.hash=\'\'">{b}</button>'
            for b in buttons
        )
        return f'''<div id="{self._id}-ov" class="iskg-msgbox-overlay">
  <div class="iskg-msgbox">
    <div class="iskg-msgbox-title">{title}</div>
    <div class="iskg-msgbox-text">{text}</div>
    <div class="iskg-msgbox-btns">{btns_html}</div>
  </div>
</div>'''

    def _render_js(self):
        return ""


class Knob(Widget):
    def __init__(
        self,
        parent=None,
        from_=0,
        to=100,
        value=0,
        size=60,
        color="cyan",
        show_value=True,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["size"] = size
        self._config_dict["color"] = color
        self._config_dict["show_value"] = show_value

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self):
        size = self._config_dict.get("size", 60)
        show_val = self._config_dict.get("show_value", True)
        val = self._config_dict.get("value", 0)
        style = self._render_style()
        val_html = f'<span class="iskg-knob-val">{val}</span>' if show_val else ""
        return f'''<div id="{self._id}" class="iskg-knob-wrap" style="{style}width:{size}px;">
  <canvas id="{self._id}-cv" class="iskg-knob-canvas" width="{size}" height="{size}"></canvas>
  {val_html}
</div>'''

    def _render_js(self):
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
  var curVal=val,dragging=false;
  cv.onmousedown=function(e){{dragging=true;}};
  document.onmousemove=function(e){{
    if(!dragging)return;
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
  }};
  document.onmouseup=function(){{dragging=false;}};
  cv.onwheel=function(e){{
    e.preventDefault();
    var st=(hi-lo)/100||1;
    curVal+=e.deltaY>0?-st:st;
    curVal=Math.max(lo,Math.min(hi,curVal));
    draw(curVal);
    iskg_bridge_event("{self._id}","change",curVal.toString());
  }};
}})();'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        return f"""var fn=window.iskg_knob_{self._id};
if(fn)fn({val});"""


class LEDDisplay(Widget):
    def __init__(
        self,
        parent=None,
        value=0,
        digits=4,
        color="green",
        label="",
        height=32,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["value"] = value
        self._config_dict["digits"] = digits
        self._config_dict["color"] = color
        self._config_dict["label"] = label
        self._config_dict["height"] = height

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = v
        self._sync()

    def _render(self):
        digits = self._config_dict.get("digits", 4)
        val = self._config_dict.get("value", 0)
        color = self._config_dict.get("color", "green")
        label = self._config_dict.get("label", "")
        height = self._config_dict.get("height", 32)
        style = self._render_style()
        disp = str(val).rjust(digits, "0")[:digits]
        font_size = max(12, height - 10)
        padt = (height - font_size) // 2
        lbl_html = f'<div class="iskg-led-label">{label}</div>' if label else ""
        return f'''<div id="{self._id}" class="iskg-led-wrap" style="{style}">
  {lbl_html}
  <div class="iskg-led-digits iskg-led-{color}" style="font-size:{font_size}px;height:{height}px;line-height:{height - padt * 2}px;padding:{padt}px 8px;">
    {disp}
  </div>
</div>'''

    def _render_update_js(self):
        digits = self._config_dict.get("digits", 4)
        val = self._config_dict.get("value", 0)
        disp = str(val).rjust(digits, "0")[:digits]
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-led-digits").innerText="{disp}";'''


class DataGrid(Widget):
    def __init__(
        self, parent=None, columns=None, rows=None, width=300, height=200, **kwargs
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["columns"] = columns or []
        self._config_dict["rows"] = rows or []
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    @property
    def rows(self):
        return self._config_dict.get("rows", [])

    @rows.setter
    def rows(self, v):
        self._config_dict["rows"] = v
        self._sync()

    def _render(self):
        cols = self._config_dict.get("columns", [])
        rows = self._config_dict.get("rows", [])
        width = self._config_dict.get("width", 300)
        height = self._config_dict.get("height", 200)
        style = self._render_style()
        ths = "".join(
            f'<th data-col="{i}">{c} <span class="arrow"></span></th>'
            for i, c in enumerate(cols)
        )
        trs = ""
        for ri, row in enumerate(rows):
            cls = "even" if ri % 2 == 0 else "odd"
            tds = "".join(f"<td>{v}</td>" for v in row)
            trs += f'<tr class="{cls}" data-row="{ri}">{tds}</tr>'
        return f'''<div id="{self._id}" class="iskg-datagrid" style="{style}width:{width}px;height:{height}px;">
  <table>
    <thead><tr>{ths}</tr></thead>
    <tbody>{trs}</tbody>
  </table>
</div>'''

    def _render_js(self):
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var ths=el.querySelectorAll("th");
  var tbody=el.querySelector("tbody");
  var sortCol=-1,asc=true;
  ths.forEach(function(th,i){{
    th.onclick=function(){{
      if(sortCol==i)asc=!asc;
      else{{sortCol=i;asc=true;}}
      var rows=Array.from(tbody.querySelectorAll("tr"));
      rows.sort(function(a,b){{
        var va=a.children[i].innerText,vb=b.children[i].innerText;
        if(va<vb)return asc?-1:1;
        if(va>vb)return asc?1:-1;
        return 0;
      }});
      rows.forEach(function(r){{tbody.appendChild(r);}});
      ths.forEach(function(t){{t.querySelector(".arrow").innerText="";}});
      th.querySelector(".arrow").innerText=asc?"\\u25b2":"\\u25bc";
    }};
  }});
  el.querySelectorAll("tr").forEach(function(r){{
    r.onclick=function(){{
      el.querySelectorAll("tr.selected").forEach(function(s){{s.classList.remove("selected");}});
      this.classList.add("selected");
      iskg_bridge_event("{self._id}","select",this.dataset.row);
    }};
  }});
}})();'''

    def _render_update_js(self):
        rows = self._config_dict.get("rows", [])
        trs = ""
        for ri, row in enumerate(rows):
            cls = "even" if ri % 2 == 0 else "odd"
            tds = "".join(f"<td>{v}</td>" for v in row)
            trs += f'<tr class="{cls}" data-row="{ri}">{tds}</tr>'
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.querySelector("tbody").innerHTML="{trs.replace('"', '\\"')}";}}'''


class IndicatorLED(Widget):
    def __init__(
        self, parent=None, color="green", size=8, active=True, label="", **kwargs
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["color"] = color
        self._config_dict["size"] = size
        self._config_dict["active"] = active
        self._config_dict["label"] = label

    @property
    def active(self):
        return self._config_dict.get("active", True)

    @active.setter
    def active(self, v):
        self._config_dict["active"] = bool(v)
        self._sync()

    def _render(self):
        size = self._config_dict.get("size", 8)
        color = self._config_dict.get("color", "green")
        active = self._config_dict.get("active", True)
        label = self._config_dict.get("label", "")
        style = self._render_style()
        col_map = {
            "green": "#4ade80",
            "red": "#ef4444",
            "amber": "#f59e0b",
            "cyan": "#22d3ee",
            "blue": "#60a5fa",
        }
        col = col_map.get(color, "#4ade80")
        on_cls = "iskg-indicator-on" if active else "iskg-indicator-off"
        shadow = f"0 0 {size}px {col}" if active else "none"
        lbl_html = f'<span class="iskg-indicator-label">{label}</span>' if label else ""
        return f'''<div id="{self._id}" class="iskg-indicator" style="{style}">
  <span class="iskg-indicator-dot {on_cls}" style="width:{size}px;height:{size}px;background:{col};box-shadow:{shadow};"></span>
  {lbl_html}
</div>'''

    def _render_update_js(self):
        active = self._config_dict.get("active", True)
        on_cls = "iskg-indicator-on" if active else "iskg-indicator-off"
        return f'''var el=document.getElementById("{self._id}");
if(el){{var d=el.querySelector(".iskg-indicator-dot");
d.className="iskg-indicator-dot {on_cls}";}}'''


class RadialGauge(Widget):
    def __init__(
        self,
        parent=None,
        from_=0,
        to=100,
        value=50,
        size=100,
        label="",
        units="",
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        self._config_dict["value"] = value
        self._config_dict["size"] = size
        self._config_dict["label"] = label
        self._config_dict["units"] = units

    @property
    def value(self):
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v):
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self):
        size = self._config_dict.get("size", 100)
        label = self._config_dict.get("label", "")
        units = self._config_dict.get("units", "")
        style = self._render_style()
        lbl_html = (
            f'<div class="iskg-gauge-label">{label}{" " + units if units else ""}</div>'
            if label or units
            else ""
        )
        return f'''<div id="{self._id}" class="iskg-gauge-wrap" style="{style}width:{size}px;">
  <canvas id="{self._id}-cv" class="iskg-gauge-canvas" width="{size}" height="{size + 20}"></canvas>
  {lbl_html}
</div>'''

    def _render_js(self):
        size = self._config_dict.get("size", 100)
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 50)
        cx, cy = size // 2, size // 2 + 5
        r = cx - 10
        return f'''(function(){{
  var cv=document.getElementById("{self._id}-cv");
  var ctx=cv.getContext("2d");
  var cx={cx},cy={cy},r={r},lo={lo},hi={hi},val={val};
  var arcStart=135,arcSweep=270;
  function draw(v){{
    ctx.clearRect(0,0,cv.width,cv.height);
    var p=(v-lo)/(hi-lo);
    var endA=arcStart+p*arcSweep;
    ctx.strokeStyle="#1a2636"; ctx.lineWidth=12;
    ctx.beginPath();
    ctx.arc(cx,cy,r,(-arcStart-arcSweep)*Math.PI/180,-arcStart*Math.PI/180);
    ctx.stroke();
    var grad=ctx.createLinearGradient(0,0,cv.width,0);
    grad.addColorStop(0,"#4ade80"); grad.addColorStop(0.5,"#f59e0b"); grad.addColorStop(1,"#ef4444");
    ctx.strokeStyle=grad; ctx.lineWidth=10;
    ctx.shadowColor="#22d3ee"; ctx.shadowBlur=8;
    ctx.beginPath();
    ctx.arc(cx,cy,r,-endA*Math.PI/180,-arcStart*Math.PI/180);
    ctx.stroke();
    ctx.shadowBlur=0;
    for(var i=0;i<=10;i++){{
      var a=(arcStart+i/10*arcSweep)*Math.PI/180;
      var len=i%5==0?8:4;
      ctx.strokeStyle=i%5==0?"#c8d6e5":"#4a5a6a";
      ctx.lineWidth=i%5==0?1.5:1;
      ctx.beginPath();
      ctx.moveTo(cx+(r-2)*Math.cos(-a),cy+(r-2)*Math.sin(-a));
      ctx.lineTo(cx+(r-len)*Math.cos(-a),cy+(r-len)*Math.sin(-a));
      ctx.stroke();
    }}
    ctx.fillStyle="#c8d6e5";
    ctx.font="bold "+Math.round({size}/8)+"px 'Share Tech Mono',monospace";
    ctx.textAlign="center"; ctx.textBaseline="middle";
    ctx.fillText(Math.round(v),cx,cy+r*0.6);
  }}
  draw(val);
  window.iskg_gauge_{self._id}=draw;
}})();'''

    def _render_update_js(self):
        val = self._config_dict.get("value", 0)
        return f"var fn=window.iskg_gauge_{self._id};if(fn)fn({val});"


class ToggleSwitch(Widget):
    def __init__(self, parent=None, text="", checked=False, command=None, **kwargs):
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["checked"] = checked

    @property
    def checked(self):
        return self._config_dict.get("checked", False)

    @checked.setter
    def checked(self, v):
        self._config_dict["checked"] = bool(v)
        self._sync()

    def _render(self):
        text = self._config_dict.get("text", "")
        checked = self._config_dict.get("checked", False)
        style = self._render_style()
        track_cls = "iskg-toggle-track" + (" checked" if checked else "")
        wrap_cls = "iskg-toggle-wrap"
        if self._config_dict.get("disabled"):
            wrap_cls += " disabled"
        return f'''<label id="{self._id}" class="{wrap_cls}" style="{style}">
  <span class="{track_cls}"><span class="iskg-toggle-knob"></span></span>
  <span class="iskg-toggle-text">{text}</span>
</label>'''

    def _render_js(self):
        return f'''document.getElementById("{self._id}").onclick=function(){{
  var t=this.querySelector(".iskg-toggle-track");
  t.classList.toggle("checked");
  iskg_bridge_event("{self._id}","change",t.classList.contains("checked")?"true":"false");
}};'''

    def _render_update_js(self):
        checked = self._config_dict.get("checked", False)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var t=el.querySelector(".iskg-toggle-track");
t.classList.toggle("checked",{json.dumps(checked)});}}'''


class StatusBar(Widget):
    def __init__(self, parent=None, sections=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["sections"] = sections or []

    def _render(self):
        sections = self._config_dict.get("sections", [])
        style = self._render_style()
        parts = []
        for sec in sections:
            if isinstance(sec, dict):
                text = sec.get("text", "")
                color = sec.get("color", "")
                style_attr = f"color:var(--{color})" if color else ""
                parts.append(
                    f'<span class="iskg-statusbar-section" style="{style_attr}">{text}</span>'
                )
            else:
                parts.append(f'<span class="iskg-statusbar-section">{sec}</span>')
        inner = "".join(parts)
        return f'''<div id="{self._id}" class="iskg-statusbar" style="{style}">
  {inner}
</div>'''

    def _render_update_js(self):
        return ""


class MenuItem:
    def __init__(self, text, command=None, shortcut="", icon=""):
        self.text = text
        self.command = command
        self.shortcut = shortcut
        self.icon = icon
        self.submenu = None


class Menu:
    _counter = 0

    def __init__(self, text=""):
        Menu._counter += 1
        self._id = f"iskg-m{Menu._counter}"
        self.text = text
        self.items = []

    def add_item(self, text, command=None, shortcut="", icon=""):
        item = MenuItem(text, command, shortcut, icon)
        self.items.append(item)
        return item

    def add_separator(self):
        self.items.append(None)

    def add_menu(self, text):
        sub = Menu(text)
        item = MenuItem(text)
        item.submenu = sub
        self.items.append(item)
        return sub


class MenuBar(Widget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._menus = []

    def add_menu(self, text):
        m = Menu(text)
        self._menus.append(m)
        return m

    def _render_menu_dd(self, menu, top_level_text=None):
        mn_attr = f' data-mn="{top_level_text}"' if top_level_text else ""
        parts = []
        for item in menu.items:
            if item is None:
                parts.append('<div class="iskg-menu-sep"></div>')
            else:
                cls = "iskg-menu-item"
                attrs = ""
                txt = (
                    item.text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                sc = (
                    f'<span class="iskg-menu-sc">{item.shortcut}</span>'
                    if item.shortcut
                    else ""
                )
                ico = (
                    f'<span class="iskg-menu-ico">{item.icon}</span>'
                    if item.icon
                    else ""
                )
                if item.submenu:
                    cls += " iskg-menu-sub"
                    attrs = f' data-sub="{item.submenu._id}"'
                    parts.append(
                        f'<div class="{cls}"{attrs}>{ico}<span class="iskg-menu-txt">{txt}</span>▸{sc}'
                        f"{self._render_menu_dd(item.submenu, top_level_text=top_level_text)}</div>"
                    )
                else:
                    parts.append(
                        f'<div class="{cls}" data-cmd="1">{ico}<span class="iskg-menu-txt">{txt}</span>{sc}</div>'
                    )
        return (
            f'<div id="{menu._id}" class="iskg-menu-dd"{mn_attr}>{"".join(parts)}</div>'
        )

    def _render(self):
        style = self._render_style()
        items_html = "".join(
            f'<div class="iskg-menubar-item" data-m="{m._id}">{m.text}</div>'
            for m in self._menus
        )
        dds_html = "".join(
            self._render_menu_dd(m, top_level_text=m.text) for m in self._menus
        )
        return f'<div id="{self._id}" class="iskg-menubar" style="{style}position:relative;">{items_html}{dds_html}</div>'

    def _render_js(self):
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  var openDD=null;
  function hideAll(){{el.querySelectorAll(".iskg-menu-dd").forEach(function(d){{d.style.display="none";}});openDD=null;}}
  el.querySelectorAll(".iskg-menubar-item").forEach(function(h){{
    h.onclick=function(e){{
      e.stopPropagation();
      var dd=document.getElementById(this.getAttribute("data-m"));
      if(!dd)return;
      if(openDD===dd){{hideAll();return;}}
      hideAll();
      dd.style.display="block";
      openDD=dd;
    }};
  }});
  el.querySelectorAll(".iskg-menu-item").forEach(function(it){{
    it.onclick=function(e){{
      e.stopPropagation();
      if(this.getAttribute("data-sub")){{
        var sub=document.getElementById(this.getAttribute("data-sub"));
        if(sub)sub.style.display=sub.style.display==="block"?"none":"block";
        return;
      }}
      if(this.getAttribute("data-cmd")){{
        var path=[];var cur=this;
        while(cur&&cur!=el){{
          var mn=cur.getAttribute("data-mn");
          if(mn)path.unshift(mn);
          if(!cur.classList.contains("iskg-menu-dd")){{
            var t=cur.querySelector(".iskg-menu-txt");
            if(t)path.unshift(t.innerText);
          }}
          cur=cur.parentElement;
        }}
        hideAll();
        iskg_bridge_event("{self._id}","command",path.join("/"));
      }}
    }};
    it.onmouseenter=function(e){{
      var sub=this.getAttribute("data-sub");
      if(sub){{
        el.querySelectorAll(".iskg-menu-dd").forEach(function(d){{if(d.id!=sub)d.style.display="none";}});
        document.getElementById(sub).style.display="block";
      }}
    }};
  }});
  document.addEventListener("click",function(){{hideAll();}});
}})();'''

    def _render_update_js(self):
        return ""

    def _find_command(self, path_parts):
        for m in self._menus:
            if path_parts and m.text == path_parts[0]:
                return self._walk_items(m.items, path_parts[1:])
        return None

    def _walk_items(self, items, parts):
        if not parts:
            return None
        for item in items:
            if item is None:
                continue
            if item.text == parts[0]:
                if len(parts) == 1:
                    return item.command
                if item.submenu:
                    return self._walk_items(item.submenu.items, parts[1:])
        return None

    def _handle_bridge_event(self, event_name, event_data):
        if event_name == "command" and event_data:
            cmd = self._find_command(event_data.split("/"))
            if cmd:
                cmd()
        super()._handle_bridge_event(event_name, event_data)


class FileDialog:
    @staticmethod
    def open_file(app, title="Open", directory="", file_types=None, multiple=False):
        return app.file_dialog("open", directory, file_types, multiple)

    @staticmethod
    def save_file(app, title="Save As", directory="", file_types=None):
        return app.file_dialog("save", directory, file_types, False)

    @staticmethod
    def open_folder(app, title="Select Folder", directory=""):
        return app.file_dialog("folder", directory, None, False)


class Tooltip(Widget):
    def __init__(self, parent=None, text="", delay=500, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["delay"] = delay

    def attach(self, target_id):
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

    def _render(self):
        return ""

    def _render_js(self):
        return ""

    def _render_children_js(self):
        return ""


class Spacer(Widget):
    def __init__(self, parent=None, width=0, height=0, expand=False, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["expand"] = expand

    def _render(self):
        style = self._render_style()
        w = self._config_dict.get("width", 0)
        h = self._config_dict.get("height", 0)
        exp = self._config_dict.get("expand", False)
        w_s = f"width:{w}px;" if w else ""
        h_s = f"height:{h}px;" if h else ""
        e_s = "flex:1;min-height:0;min-width:0;" if exp else ""
        return f'<div id="{self._id}" class="iskg-spacer" style="{style}{w_s}{h_s}{e_s}"></div>'


class ImageBox(Widget):
    def __init__(
        self, parent=None, src="", width=100, height=100, fit="contain", **kwargs
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["src"] = src
        self._config_dict["width"] = width
        self._config_dict["height"] = height
        self._config_dict["fit"] = fit

    def _render(self):
        src = self._config_dict.get("src", "")
        width = self._config_dict.get("width", 100)
        height = self._config_dict.get("height", 100)
        fit = self._config_dict.get("fit", "contain")
        style = self._render_style()
        return f'''<div id="{self._id}" class="iskg-imagebox" style="{style}width:{width}px;height:{height}px;">
  <img src="{src}" style="object-fit:{fit};"/>
</div>'''


class IconLabel(Widget):
    def __init__(self, parent=None, text="", icon="", icon_size=14, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["icon"] = icon
        self._config_dict["icon_size"] = icon_size

    def _render(self):
        text = self._config_dict.get("text", "")
        icon = self._config_dict.get("icon", "")
        icon_size = self._config_dict.get("icon_size", 14)
        style = self._render_style()
        icon_html = ""
        if icon:
            if icon.startswith("<"):
                icon_html = f'<span class="iskg-icon" style="width:{icon_size}px;height:{icon_size}px;">{icon}</span>'
            else:
                icon_html = f'<span class="iskg-icon" style="font-size:{icon_size}px;width:{icon_size}px;height:{icon_size}px;">{icon}</span>'
        return f'''<span id="{self._id}" class="iskg-iconlabel" style="{style}">
  {icon_html}
  <span>{text}</span>
</span>'''


class RichText(Widget):
    def __init__(self, parent=None, text="", height=150, show_toolbar=True, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["height"] = height
        self._config_dict["show_toolbar"] = show_toolbar

    def _render(self):
        text = self._config_dict.get("text", "")
        height = self._config_dict.get("height", 150)
        show_tb = self._config_dict.get("show_toolbar", True)
        style = self._render_style()
        tb_html = ""
        if show_tb:
            cmds = [
                ("B", "bold"),
                ("I", "italic"),
                ("U", "underline"),
                ("S", "strikeThrough"),
                ("|", ""),
                ("R", "forecolor:#ef4444"),
                ("G", "forecolor:#4ade80"),
                ("C", "forecolor:#22d3ee"),
                ("Y", "forecolor:#f59e0b"),
                ("|", ""),
                ("H1", "formatBlock:h1"),
                ("H2", "formatBlock:h2"),
                ("P", "formatBlock:p"),
                ("|", ""),
                ("UL", "insertUnorderedList"),
                ("OL", "insertOrderedList"),
            ]
            btns = ""
            for label, cmd in cmds:
                if cmd == "":
                    btns += '<span style="width:1px;height:14px;background:var(--border);margin:0 2px;"></span>'
                else:
                    args = ""
                    c = cmd
                    if ":" in cmd:
                        c, args = cmd.split(":", 1)
                    btns += (
                        f'<button data-cmd="{c}" data-args="{args}">{label}</button>'
                    )
            tb_html = f'<div class="iskg-richtext-toolbar">{btns}</div>'
        return f'''<div id="{self._id}" class="iskg-richtext-wrap" style="{style}height:{height}px;">
  {tb_html}
  <div id="{self._id}-editor" class="iskg-richtext-editor" contenteditable="true">{text}</div>
</div>'''

    def _render_js(self):
        return f'''(function(){{
  var wrap=document.getElementById("{self._id}");
  if(!wrap)return;
  var editor=wrap.querySelector(".iskg-richtext-editor");
  var savedRange=null;
  editor.addEventListener("focus",function(){{
    var sel=window.getSelection();
    if(sel&&sel.rangeCount)savedRange=sel.getRangeAt(0);
  }});
  editor.addEventListener("keyup",function(){{
    var sel=window.getSelection();
    if(sel&&sel.rangeCount)savedRange=sel.getRangeAt(0);
  }});
  wrap.querySelectorAll(".iskg-richtext-toolbar button").forEach(function(btn){{
    btn.onmousedown=function(e){{e.preventDefault();editor.focus();}};
    btn.onclick=function(){{
      if(savedRange){{var sel=window.getSelection();sel.removeAllRanges();sel.addRange(savedRange);}}
      var cmd=this.dataset.cmd;
      var args=this.dataset.args;
      if(cmd=="formatBlock"){{
        document.execCommand("formatBlock",false,args||"<p>");
      }}else if(cmd=="forecolor"){{
        document.execCommand("foreColor",false,args||"#22d3ee");
      }}else{{
        document.execCommand(cmd,false,args||null);
      }}
      editor.focus();
    }};
  }});
  editor.oninput=function(){{
    iskg_bridge_event("{self._id}","change",this.innerHTML);
  }};
}})();'''

    def _render_update_js(self):
        text = self._config_dict.get("text", "")
        escaped = (
            text.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("/", "\\/")
        )
        return f'''var el=document.getElementById("{self._id}-editor");
if(el)el.innerHTML="{escaped}";'''


class TreeView(Widget):
    def __init__(self, parent=None, items=None, width=200, height=200, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_dict["items"] = items or []
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    def _render(self):
        items = self._config_dict.get("items", [])
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 200)
        style = self._render_style()

        def render_items(items_list, depth=0):
            parts = []
            for item in items_list:
                if isinstance(item, str):
                    item = {"text": item}
                text = item.get("text", "")
                children = item.get("children", [])
                open_state = item.get("open", False)
                icon = item.get("icon", "&#128193;" if children else "&#128196;")
                toggle = ""
                child_html = ""
                if children:
                    toggle = f'<span class="iskg-tree-toggle">{"&#9660;" if open_state else "&#9658;"}</span>'
                    child_html = f'<ul class="iskg-tree-children{" open" if open_state else ""}">{render_items(children, depth + 1)}</ul>'
                parts.append(f"""<li>
  <div class="iskg-tree-node">
    {toggle}
    <span class="iskg-tree-icon">{icon}</span>
    <span class="iskg-tree-text">{text}</span>
  </div>
  {child_html}
</li>""")
            return "".join(parts)

        inner = render_items(items)
        return f'''<div id="{self._id}" class="iskg-tree" style="{style}width:{width}px;height:{height}px;">
  <ul>{inner}</ul>
</div>'''

    def _render_js(self):
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  el.querySelectorAll(".iskg-tree-toggle").forEach(function(tog){{
    tog.onclick=function(e){{
      e.stopPropagation();
      var li=this.closest("li");
      var children=li&&li.querySelector(":scope > .iskg-tree-children");
      if(children){{
        children.classList.toggle("open");
        this.innerHTML=children.classList.contains("open")?"&#9660;":"&#9658;";
      }}
    }};
  }});
      el.querySelectorAll(".iskg-tree-node").forEach(function(node){{
        node.onclick=function(){{
          el.querySelectorAll(".iskg-tree-node.selected").forEach(function(s){{s.classList.remove("selected");}});
          this.classList.add("selected");
          var path=[];
          var cur=this;
          while(cur&&cur!=el){{
            var txt=cur.querySelector(".iskg-tree-text");
            if(txt)path.unshift(txt.innerText);
            cur=cur.parentElement?.parentElement?.parentElement?.querySelector(":scope > .iskg-tree-node")||null;
          }}
          iskg_bridge_event("{self._id}","select",path.join("/"));
        }};
      }});
}})();'''


class DropTarget(Widget):
    def __init__(
        self, parent=None, text="Drop files here", width=200, height=100, **kwargs
    ):
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["width"] = width
        self._config_dict["height"] = height

    def _render(self):
        text = self._config_dict.get("text", "")
        width = self._config_dict.get("width", 200)
        height = self._config_dict.get("height", 100)
        style = self._render_style()
        return f'''<div id="{self._id}" class="iskg-droptarget" style="{style}width:{width}px;height:{height}px;">
  <div class="iskg-droptarget-icon">⬇</div>
  <div class="iskg-droptarget-text">{text}</div>
</div>'''

    def _render_js(self):
        return f'''(function(){{
  var el=document.getElementById("{self._id}");
  el.ondragover=function(e){{e.preventDefault();this.classList.add("dragover");}};
  el.ondragleave=function(){{this.classList.remove("dragover");}};
  el.ondrop=function(e){{
    e.preventDefault();
    this.classList.remove("dragover");
    var files=[];
    for(var i=0;i<e.dataTransfer.files.length;i++){{
      files.push(e.dataTransfer.files[i].name);
    }}
    iskg_bridge_event("{self._id}","drop",files.join(","));
  }};
}})();'''
