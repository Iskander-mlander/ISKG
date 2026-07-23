from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import Any

from ..base import Widget


class Button(Widget):
    """A clickable push button with IFAZ tactical styling.

    Config options: ``text``, ``command``, ``variant`` (``"primary"``,
    ``"success"``, ``"danger"``, ``"warning"``, ``"info"``), ``size``
    (``"sm"``, ``"lg"``), plus all CSS properties from ``_CONFIG_TO_CSS``.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value: str) -> None:
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self) -> str:
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
        attrs = self._render_attrs()
        width = self._config_dict.get("width", "")
        if width:
            style += f"width:{width}px;"
        return f'<button id="{self._id}" class="{cls}" style="{style}" {attrs}>{escaped}</button>'

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").onclick=function(){{
  iskg_bridge_event("{self._id}","click","");
}};'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        text = self._config_dict.get("text", "")
        escaped = text.replace("\\", "\\\\").replace("'", "\\'")
        return f'iskg_set_text("{self._id}","{escaped}");'


class Entry(Widget):
    """A single-line text input field.

    Config options: ``text``, ``placeholder``, ``justify``, ``width``,
    ``password`` (bool), ``maxlength``, plus all CSS properties from
    ``_CONFIG_TO_CSS``.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        justify: str = "",
        maxlength: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = (
            self._textvariable.get() if self._textvariable is not None else str(text)
        )
        if justify:
            self._config_dict["justify"] = justify
        if maxlength is not None:
            self._config_dict["maxlength"] = maxlength

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value: str) -> None:
        self._config_dict["text"] = str(value)
        self._sync()

    @property
    def justify(self) -> str:
        return self._config_dict.get("justify", "")

    @justify.setter
    def justify(self, value: str) -> None:
        self._config_dict["justify"] = value
        self._sync()

    @property
    def maxlength(self) -> int | None:
        return self._config_dict.get("maxlength")

    @maxlength.setter
    def maxlength(self, value: int | None) -> None:
        if value is not None:
            self._config_dict["maxlength"] = value
        else:
            self._config_dict.pop("maxlength", None)
        self._sync()

    def _render(self) -> str:
        val = self._config_dict.get("text", "")
        escaped = val.replace("&", "&amp;").replace('"', "&quot;")
        placeholder = self._config_dict.get("placeholder", "")
        placeholder_attr = f' placeholder="{placeholder}"' if placeholder else ""
        width = self._config_dict.get("width", 150)
        style = self._render_style() + f"width:{width}px;"
        j = self._config_dict.get("justify", "")
        if j == "center":
            style += "text-align:center;"
        elif j in ("right", "e"):
            style += "text-align:right;"
        input_type = "password" if self._config_dict.get("password") else "text"
        ml = self._config_dict.get("maxlength")
        ml_attr = f' maxlength="{ml}"' if ml is not None else ""
        attrs = self._render_attrs()
        return f'<input id="{self._id}" class="iskg-entry" type="{input_type}" value="{escaped}"{placeholder_attr}{ml_attr} style="{style}" {attrs}/>'

    def _var_updated(self, var: Any) -> None:
        if var is self._textvariable:
            self._config_dict["text"] = var.get()
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name in ("change", "input"):
            self._config_dict["text"] = str(event_data)
        super()._handle_bridge_event(event_name, event_data)

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").onchange=function(){{
  iskg_bridge_event("{self._id}","change",this.value);
}};
document.getElementById("{self._id}").oninput=function(){{
  iskg_bridge_event("{self._id}","input",this.value);
}};'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        parts = []
        val = self._config_dict.get("text", "")
        escaped = val.replace("\\", "\\\\").replace("'", "\\'")
        parts.append(f'iskg_set_value("{self._id}","{escaped}");')
        pw = "password" if self._config_dict.get("password") else "text"
        parts.append(f'iskg_set_attr("{self._id}","type","{pw}");')
        ml = self._config_dict.get("maxlength")
        if ml is not None:
            parts.append(f'iskg_set_attr("{self._id}","maxlength","{ml}");')
        j = self._config_dict.get("justify", "")
        if j:
            ta = {"center": "center", "right": "right", "e": "right"}.get(j, "left")
            parts.append(f'iskg_set_style("{self._id}",{json.dumps("text-align:" + ta)});')
        return ";".join(parts)


class CheckBox(Widget):
    """A toggleable check box with label."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        checked: bool = False,
        command: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["checked"] = checked

    @property
    def checked(self) -> bool:
        return self._config_dict.get("checked", False)

    @checked.setter
    def checked(self, value: bool) -> None:
        self._config_dict["checked"] = bool(value)
        self._sync()

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value: str) -> None:
        self._config_dict["text"] = str(value)
        self._sync()

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        checked = self._config_dict.get("checked", False)
        cls = "iskg-check-wrap"
        if self._config_dict.get("disabled"):
            cls += " disabled"
        check_cls = "iskg-check" + (" checked" if checked else "")
        style = self._render_style()
        attrs = self._render_attrs()
        return f'''<label id="{self._id}" class="{cls}" style="{style}" {attrs}>
  <span class="{check_cls}"></span>
  <span>{text}</span>
</label>'''

    def _var_updated(self, var: Any) -> None:
        if var is self._variable:
            self._config_dict["checked"] = var.get()
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            self._config_dict["checked"] = event_data == "true"
        super()._handle_bridge_event(event_name, event_data)

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").onclick=function(){{
  var c=this.querySelector(".iskg-check");
  c.classList.toggle("checked");
  iskg_bridge_event("{self._id}","change",c.classList.contains("checked")?"true":"false");
}};'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        checked = self._config_dict.get("checked", False)
        return f'var el=document.getElementById("{self._id}");if(el)el.querySelector(".iskg-check").classList.toggle("checked",{json.dumps(checked)});'


class RadioButton(Widget):
    """A radio button for single-selection within a group."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        group: str = "default",
        command: Callable | None = None,
        value: str = "",
        variable: Any = None,
        selected: bool = False,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, variable=variable, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["value"] = value
        self._config_dict["group"] = group
        if selected:
            self._config_dict["selected"] = True
            if self._variable:
                self._variable.set(value)

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, value: str) -> None:
        self._config_dict["text"] = str(value)
        self._sync()

    @property
    def value(self) -> Any:
        return self._config_dict.get("value")

    @value.setter
    def value(self, v: Any) -> None:
        self._config_dict["value"] = v

    @property
    def selected(self) -> bool:
        if self._variable:
            return self._variable.get() == self.value
        return self._config_dict.get("selected", False)

    @selected.setter
    def selected(self, v: bool) -> None:
        self._config_dict["selected"] = bool(v)
        if self._variable and bool(v):
            self._variable.set(self.value)
        self._sync()

    def _var_updated(self, var: Any) -> None:
        if var is self._variable:
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change" and self._variable is not None:
            self._variable_handled = True
            self._variable.set(self.value, _from_widget=self)
        super()._handle_bridge_event(event_name, event_data)
        self._variable_handled = False

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        sel = self.selected
        cls = "iskg-radio-wrap"
        if self._config_dict.get("disabled"):
            cls += " disabled"
        radio_cls = "iskg-radio" + (" checked" if sel else "")
        style = self._render_style()
        attrs = self._render_attrs()
        return f'''<label id="{self._id}" class="{cls}" style="{style}" {attrs}>
  <span class="{radio_cls}"></span>
  <span>{text}</span>
</label>'''

    def _render_js(self) -> str:
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

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        sel = self.selected
        return f'''var el=document.getElementById("{self._id}");
if(el)el.querySelector(".iskg-radio").classList.toggle("checked",{json.dumps(sel)});'''


class ComboBox(Widget):
    """A dropdown select menu."""

    def __init__(
        self,
        parent: Widget | None = None,
        values: list[str] | None = None,
        current: int = 0,
        command: Callable | None = None,
        editable: bool = False,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["values"] = values or []
        self._config_dict["current"] = current
        self._config_dict["editable"] = editable

    @property
    def current(self) -> int:
        return self._config_dict.get("current", 0)

    @current.setter
    def current(self, idx: int) -> None:
        self._config_dict["current"] = int(idx)
        self._sync()

    @property
    def value(self) -> str:
        vals = self._config_dict.get("values", [])
        idx = self._config_dict.get("current", 0)
        return vals[idx] if 0 <= idx < len(vals) else ""

    @property
    def editable(self) -> bool:
        return self._config_dict.get("editable", False)

    @editable.setter
    def editable(self, value: bool) -> None:
        self._config_dict["editable"] = bool(value)
        self._sync()

    def _var_updated(self, var: Any) -> None:
        if var is self._textvariable:
            vals = self._config_dict.get("values", [])
            target = var.get()
            for i, v in enumerate(vals):
                if v == target:
                    self._config_dict["current"] = i
                    break
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            self._variable_handled = True
            try:
                idx = int(event_data)
                vals = self._config_dict.get("values", [])
                if 0 <= idx < len(vals):
                    self._config_dict["current"] = idx
                    if self._textvariable is not None:
                        self._textvariable.set(vals[idx], _from_widget=self)
            except (ValueError, TypeError):
                pass
        super()._handle_bridge_event(event_name, event_data)
        self._variable_handled = False

    def _render(self) -> str:
        vals = self._config_dict.get("values", [])
        cur = self._config_dict.get("current", 0)
        cur_text = vals[cur] if vals and 0 <= cur < len(vals) else ""
        style = self._render_style()
        width = self._config_dict.get("width", 140)
        items_html = "".join(
            f'<div class="iskg-cb-item" data-idx="{i}">{v}</div>' for i, v in enumerate(vals)
        )
        cls = "iskg-cb-wrap"
        if self._config_dict.get("disabled"):
            cls += " iskg-disabled"
        if self._config_dict.get("editable"):
            sel_esc = cur_text.replace("&", "&amp;").replace('"', "&quot;")
            return f'''<div id="{self._id}" class="{cls}" style="{style}width:{width}px;">
  <input id="{self._id}-input" class="iskg-cb-input" value="{sel_esc}" style="width:{width - 22}px;">
  <div class="iskg-cb-display" id="{self._id}-disp">
    <span class="iskg-cb-arrow">▾</span>
  </div>
  <div class="iskg-cb-drop" id="{self._id}-drop" style="display:none;">
    {items_html}
  </div>
</div>'''
        return f'''<div id="{self._id}" class="{cls}" style="{style}width:{width}px;">
  <div class="iskg-cb-display" id="{self._id}-disp">
    <span id="{self._id}-text">{cur_text}</span>
    <span class="iskg-cb-arrow">▾</span>
  </div>
  <div class="iskg-cb-drop" id="{self._id}-drop" style="display:none;">
    {items_html}
  </div>
</div>'''

    def _render_js(self) -> str:
        if self._config_dict.get("editable"):
            return f'''(function(){{
var wrap=document.getElementById("{self._id}");
var inp=document.getElementById("{self._id}-input");
var disp=document.getElementById("{self._id}-disp");
var drop=document.getElementById("{self._id}-drop");
function closeDrop(){{drop.style.display="none";wrap.classList.remove("iskg-cb-open");}}
disp.onclick=function(e){{e.stopPropagation();
  var isOpen=drop.style.display=="block";
  document.querySelectorAll(".iskg-cb-drop").forEach(function(d){{d.style.display="none";}});
  document.querySelectorAll(".iskg-cb-wrap").forEach(function(w){{w.classList.remove("iskg-cb-open");}});
  if(!isOpen){{drop.style.display="block";wrap.classList.add("iskg-cb-open");}}
}};
drop.onclick=function(e){{var item=e.target.closest(".iskg-cb-item");
  if(item){{var idx=item.dataset.idx;
    inp.value=item.innerText;
    closeDrop();
    iskg_bridge_event("{self._id}","change",idx);
  }}
}};
inp.oninput=function(){{
  iskg_bridge_event("{self._id}","change","-1");
}};
document.addEventListener("click",function(e){{
  if(!wrap.contains(e.target))closeDrop();
}});
}})();'''
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

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        cur = self._config_dict.get("current", 0)
        vals = self._config_dict.get("values", [])
        cur_text = vals[cur] if vals and 0 <= cur < len(vals) else ""
        return f'''var t=document.getElementById("{self._id}-text");
if(t)t.innerText="{cur_text}";
var inp=document.getElementById("{self._id}-input");
if(inp)inp.value="{cur_text}";
var items=document.querySelectorAll("#{self._id}-drop .iskg-cb-item");
items.forEach(function(x,i){{x.classList.toggle("iskg-cb-sel",i=={cur});}});'''


class Slider(Widget):
    """A horizontal range slider.

    Config options: ``from``, ``to``, ``value``, ``orient``
    (``"horizontal"`` / ``"vertical"``), ``show_value`` (bool),
    plus all CSS properties.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        value: float = 50,
        min_value: float | None = None,
        max_value: float | None = None,
        command: Callable | None = None,
        from_: float = 0,
        to: float = 100,
        orient: str = "horizontal",
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        if min_value is not None:
            self._config_dict["from"] = min_value
        if max_value is not None:
            self._config_dict["to"] = max_value
        self._config_dict["value"] = self._variable.get() if self._variable is not None else value
        self._config_dict["orient"] = orient

    @property
    def value(self) -> float:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: float) -> None:
        self._config_dict["value"] = float(v)
        self._sync()

    def _render(self) -> str:
        lo = self._config_dict.get("from", 0)
        hi = self._config_dict.get("to", 100)
        val = self._config_dict.get("value", 0)
        orient = self._config_dict.get("orient", "horizontal")
        show_val = self._get_cfg("show-value", True)
        style = self._render_style()
        width = self._config_dict.get("width", 150)

        if orient == "vertical":
            vlen = self._config_dict.get("height", 100)
            slider_cls = "iskg-slider-vert"
            track_cls = "iskg-slider-vert-track"
            wrap_style = f"{style}flex-direction:column;align-items:center;gap:4px;"
            slider_style = f"width:{vlen}px;height:4px;"
            track_style = f"width:30px;height:{vlen}px;"
            val_html = f'<span class="iskg-slider-val-center">{val}</span>' if show_val else ""
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

    def _var_updated(self, var: Any) -> None:
        if var is self._variable:
            self._config_dict["value"] = float(var.get())
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            with contextlib.suppress(ValueError, TypeError):
                self._config_dict["value"] = float(event_data)
            super()._handle_bridge_event(event_name, event_data)

    def _render_js(self) -> str:
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

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        val = self._config_dict.get("value", 0)
        return f'''var el=document.getElementById("{self._id}");
if(el){{el.value={val};
var wrap=el.closest(".iskg-slider-wrap");
if(wrap){{
  var sib=wrap.querySelector(".iskg-slider-val,.iskg-slider-val-center");
  if(sib)sib.innerText={val};
}}}}'''


class SpinBox(Widget):
    """A numeric stepper with up/down buttons."""

    def __init__(
        self,
        parent: Widget | None = None,
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        command: Callable | None = None,
        from_: int = 0,
        to: int = 100,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["from"] = from_
        self._config_dict["to"] = to
        if min_value is not None:
            self._config_dict["from"] = min_value
        if max_value is not None:
            self._config_dict["to"] = max_value
        self._config_dict["step"] = step
        self._config_dict["value"] = self._variable.get() if self._variable is not None else value

    @property
    def value(self) -> int:
        return self._config_dict.get("value", 0)

    @value.setter
    def value(self, v: int) -> None:
        self._config_dict["value"] = int(v)
        self._sync()

    def _render(self) -> str:
        val = self._config_dict.get("value", 0)
        style = self._render_style()
        return f'''<div class="iskg-spinbox-wrap" style="{style}">
  <input id="{self._id}" class="iskg-spinbox" type="text" value="{val}" readonly/>
  <div class="iskg-spinbox-btns">
    <button class="iskg-spinup" id="{self._id}-up">▲</button>
    <button class="iskg-spindown" id="{self._id}-dn">▼</button>
  </div>
</div>'''

    def _render_js(self) -> str:
        step = self._config_dict.get("step", 1)
        return f'''document.getElementById("{self._id}-up").onclick=function(){{
  var inp=document.getElementById("{self._id}");
  var v=parseInt(inp.value)||0;
  if(v<{self._config_dict["to"]}){{v+={step};inp.value=v;iskg_bridge_event("{self._id}","change",v.toString());}}
}};
document.getElementById("{self._id}-dn").onclick=function(){{
  var inp=document.getElementById("{self._id}");
  var v=parseInt(inp.value)||0;
  if(v>{self._config_dict["from"]}){{v-={step};inp.value=v;iskg_bridge_event("{self._id}","change",v.toString());}}
}};'''

    def _var_updated(self, var: Any) -> None:
        if var is self._variable:
            self._config_dict["value"] = int(var.get())
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            with contextlib.suppress(ValueError, TypeError):
                self._config_dict["value"] = int(event_data)
        super()._handle_bridge_event(event_name, event_data)

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        val = self._config_dict.get("value", 0)
        return f'document.getElementById("{self._id}").value={val};'


class Scale(Slider):
    """A range slider with min/max labels."""

    def __init__(
        self,
        parent: Widget | None = None,
        value: float = 0.5,
        command: Callable | None = None,
        from_: float = 0.0,
        to: float = 1.0,
        orient: str = "horizontal",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            parent, value=value, command=command, from_=from_, to=to, orient=orient, **kwargs
        )

    def _render(self) -> str:
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


class ToggleSwitch(Widget):
    """A toggle switch akin to a checkbox with slider appearance."""

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        active: bool | None = None,
        command: Callable | None = None,
        checked: bool = False,
        **kwargs: Any,
    ) -> None:
        if command:
            kwargs["command"] = command
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["checked"] = checked if active is None else active

    @property
    def checked(self) -> bool:
        return self._config_dict.get("checked", False)

    @checked.setter
    def checked(self, v: bool) -> None:
        self._config_dict["checked"] = bool(v)
        self._sync()

    def _var_updated(self, var: Any) -> None:
        if var is self._variable:
            self._config_dict["checked"] = var.get()
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            self._config_dict["checked"] = event_data == "true"
        super()._handle_bridge_event(event_name, event_data)

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        checked = self._config_dict.get("checked", False)
        style = self._render_style()
        track_cls = "iskg-toggle-track" + (" checked" if checked else "")
        wrap_cls = "iskg-toggle-wrap"
        if self._config_dict.get("disabled"):
            wrap_cls += " disabled"
        attrs = self._render_attrs()
        return f'''<label id="{self._id}" class="{wrap_cls}" style="{style}" {attrs}>
  <span class="{track_cls}"><span class="iskg-toggle-knob"></span></span>
  <span class="iskg-toggle-text">{text}</span>
</label>'''

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").onclick=function(){{
  var t=this.querySelector(".iskg-toggle-track");
  t.classList.toggle("checked");
  iskg_bridge_event("{self._id}","change",t.classList.contains("checked")?"true":"false");
}};'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        checked = self._config_dict.get("checked", False)
        return f'''var el=document.getElementById("{self._id}");
if(el){{var t=el.querySelector(".iskg-toggle-track");
t.classList.toggle("checked",{json.dumps(checked)});}}'''
