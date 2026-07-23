from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from ..base import Widget


class MessageDialog(Widget):
    """A message box overlay (info/warning/error/question).

    Shows an HTML overlay within the app window.
    Pass ``callback`` to receive the clicked button label.
    """

    def __init__(
        self,
        parent: Widget | None = None,
        title: str = "",
        text: str = "",
        buttons: list[str] | None = None,
        callback: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._config_dict["_dialog_title"] = title
        self._config_dict["_dialog_text"] = text
        self._config_dict["_dialog_buttons"] = buttons or ["OK"]
        self._dialog_callback = callback

    def show(self, app: Any = None) -> None:
        a = app or self.app
        if not a:
            return
        from ..app import _HANDLERS
        _HANDLERS[self._id] = self._handle_bridge_event
        self._msg_app = a
        html = json.dumps(self._render())
        a._eval_js(
            f"(function(){{"
            f'var e=document.getElementById("{self._id}-ov");'
            f"if(!e){{"
            f'document.body.insertAdjacentHTML("beforeend",{html});'
            f"var escFn=function(ev){{"
            f"if(ev.key==='Escape'){{"
            f"var ov=document.getElementById('{self._id}-ov');"
            f"if(ov){{ov.remove();iskg_bridge_event('{self._id}','result','__esc__');}}"
            f"document.removeEventListener('keydown',escFn);"
            f"}}"
            f"}};"
            f"document.addEventListener('keydown',escFn);"
            f"}}"
            f"}})()"
        )

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _render(self) -> str:
        title = self._escape(self._config_dict.get("_dialog_title", ""))
        text = self._escape(self._config_dict.get("_dialog_text", ""))
        buttons = self._config_dict.get("_dialog_buttons", ["OK"])
        bid = self._id
        btns_html = "".join(
            f"<button class=\"iskg-btn\" onclick=\"(function(btn){{var el=document.getElementById('{bid}-ov');if(el)el.remove();iskg_bridge_event('{bid}','result',btn.textContent);}})(this)\">{self._escape(b)}</button>"
            for b in buttons
        )
        return f'''<div id="{self._id}-ov" class="iskg-msgbox-overlay">
  <div class="iskg-msgbox">
    <div class="iskg-msgbox-title">{title}</div>
    <div class="iskg-msgbox-text">{text}</div>
    <div class="iskg-msgbox-btns">{btns_html}</div>
  </div>
</div>'''

    def _handle_bridge_event(self, event_name: str, event_data: Any) -> None:
        if event_name == "result":
            if self._dialog_callback:
                self._dialog_callback(str(event_data))
                self._dialog_callback = None
            from ..app import _HANDLERS
            _HANDLERS.pop(self._id, None)
        super()._handle_bridge_event(event_name, event_data)


def showinfo(
    title: str = "",
    text: str = "",
    parent: Widget | None = None,
    callback: Callable[[str], None] | None = None,
) -> MessageDialog:
    """Show an info message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showwarning(
    title: str = "",
    text: str = "",
    parent: Widget | None = None,
    callback: Callable[[str], None] | None = None,
) -> MessageDialog:
    """Show a warning message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showerror(
    title: str = "",
    text: str = "",
    parent: Widget | None = None,
    callback: Callable[[str], None] | None = None,
) -> MessageDialog:
    """Show an error message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showquestion(
    title: str = "",
    text: str = "",
    parent: Widget | None = None,
    callback: Callable[[str], None] | None = None,
) -> MessageDialog:
    """Show a question dialog with Yes/No buttons (HTML overlay)."""
    md = MessageDialog(
        parent=parent, title=title, text=text, buttons=["Yes", "No"], callback=callback
    )
    return md


class FileDialog:
    """Static methods for native file open/save dialogs."""

    @staticmethod
    def open_file(
        app: Any,
        title: str = "Open",
        directory: str = "",
        file_types: list[str] | None = None,
        multiple: bool = False,
    ) -> Any:
        return app.file_dialog("open", directory, file_types, multiple)

    @staticmethod
    def save_file(
        app: Any,
        title: str = "Save As",
        directory: str = "",
        file_types: list[str] | None = None,
    ) -> Any:
        return app.file_dialog("save", directory, file_types, False)

    @staticmethod
    def open_folder(
        app: Any,
        title: str = "Select Folder",
        directory: str = "",
    ) -> Any:
        return app.file_dialog("folder", directory, None, False)
