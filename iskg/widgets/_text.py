from __future__ import annotations

from typing import Any

from ..base import Widget


class Text(Widget):
    """A multi-line text input area."""

    _ARIA_ROLE = "textbox"

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = (
            self._textvariable.get() if self._textvariable is not None else str(text)
        )

    @property
    def text(self) -> str:
        return self._config_dict.get("text", "")

    @text.setter
    def text(self, val: str) -> None:
        self._config_dict["text"] = str(val)
        self._sync()

    def append(self, text: str) -> None:
        self._config_dict["text"] += str(text)
        self._sync()

    def clear(self) -> None:
        self._config_dict["text"] = ""
        self._sync()

    def _var_updated(self, var: Any) -> None:
        if var is self._textvariable:
            self._config_dict["text"] = var.get()
            self._sync()

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "change":
            self._config_dict["text"] = str(event_data)
        super()._handle_bridge_event(event_name, event_data)

    def _render(self) -> str:
        val = self._config_dict.get("text", "")
        escaped = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        style = self._render_style()
        width = self._config_dict.get("width")
        height = self._config_dict.get("height")
        if width is not None:
            style += f"width:{width}px;"
        if height is not None:
            style += f"height:{height}px;"
        attrs = self._render_attrs()
        return f'<textarea id="{self._id}" class="iskg-text" style="{style}" {attrs}>{escaped}</textarea>'

    def _render_js(self) -> str:
        return f'''document.getElementById("{self._id}").onchange=function(){{
  iskg_bridge_event("{self._id}","change",this.value);
}};'''

    def _default_takefocus(self) -> bool:
        return True

    def _render_update_js(self) -> str:
        val = self._config_dict.get("text", "")
        escaped = val.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f'iskg_set_text("{self._id}","{escaped}");'


class RichText(Widget):
    """A rich text editor with formatting toolbar."""

    _ARIA_ROLE = "textbox"

    def __init__(
        self,
        parent: Widget | None = None,
        text: str = "",
        height: int = 150,
        show_toolbar: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["text"] = text
        self._config_dict["height"] = height
        self._config_dict["show_toolbar"] = show_toolbar

    def _render(self) -> str:
        text = self._config_dict.get("text", "")
        height = self._config_dict.get("height", 150)
        show_tb = self._get_cfg("show-toolbar", True)
        style = self._render_style()
        attrs = self._render_attrs()
        tb_html = ""
        if show_tb:
            cmds: list[tuple[str, str, str]] = [
                ("B", "bold", "Bold"),
                ("I", "italic", "Italic"),
                ("U", "underline", "Underline"),
                ("S", "strikeThrough", "Strikethrough"),
                ("", "", ""),
                ("\u25cf", "forecolor:#ef4444", "Red"),
                ("\u25cf", "forecolor:#4ade80", "Green"),
                ("\u25cf", "forecolor:#22d3ee", "Cyan"),
                ("\u25cf", "forecolor:#f59e0b", "Amber"),
                ("", "", ""),
                ("H1", "formatBlock:h1", "Heading 1"),
                ("H2", "formatBlock:h2", "Heading 2"),
                ("P", "formatBlock:p", "Paragraph"),
                ("", "", ""),
                ("\u2261", "insertUnorderedList", "Bullet list"),
                ("1.", "insertOrderedList", "Numbered list"),
            ]
            btns = ""
            for label, cmd, tip in cmds:
                if cmd == "":
                    btns += '<span class="iskg-rt-sep"></span>'
                else:
                    args = ""
                    c = cmd
                    if ":" in cmd:
                        c, args = cmd.split(":", 1)
                    color_style = ""
                    if c == "forecolor":
                        color_style = f" color:{args};"
                    btns += (
                        f'<button data-cmd="{c}" data-args="{args}"'
                        f' title="{tip}" style="{color_style}">{label}</button>'
                    )
            tb_html = f'<div class="iskg-richtext-toolbar">{btns}</div>'
        return f'''<div id="{self._id}" class="iskg-richtext-wrap" style="{style}height:{height}px;" {attrs}>
  {tb_html}
  <div id="{self._id}-editor" class="iskg-richtext-editor" contenteditable="true">{text}</div>
</div>'''

    def _render_js(self) -> str:
        return f'''(function(){{
  var wrap=document.getElementById("{self._id}");
  if(!wrap)return;
  var editor=wrap.querySelector(".iskg-richtext-editor");
  var toggleCmds={{"bold":true,"italic":true,"underline":true,"strikeThrough":true}};
  function updateActiveStates(){{
    wrap.querySelectorAll(".iskg-richtext-toolbar button").forEach(function(b){{
      var c=b.dataset.cmd;
      if(toggleCmds[c]){{
        try{{b.classList.toggle("active",document.queryCommandState(c));}}catch(e){{}}
      }}
    }});
  }}
  editor.addEventListener("mouseup",updateActiveStates);
  editor.addEventListener("keyup",updateActiveStates);
  wrap.querySelectorAll(".iskg-richtext-toolbar button").forEach(function(btn){{
    btn.onmousedown=function(e){{e.preventDefault();editor.focus();}};
    btn.onclick=function(){{
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
      updateActiveStates();
    }};
  }});
  editor.oninput=function(){{
    iskg_bridge_event("{self._id}","change",this.innerHTML);
  }};
  updateActiveStates();
}})();'''

    def _render_update_js(self) -> str:
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
