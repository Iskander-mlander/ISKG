from __future__ import annotations

import json
from typing import Any, Callable, Optional

from ..base import Widget


class MessageDialog(Widget):
    """A message box overlay (info/warning/error/question).

    Shows an HTML overlay within the app window.
    Pass ``callback`` to receive the clicked button label.
    """

    def __init__(
        self,
        parent: Optional[Widget] = None,
        title: str = "",
        text: str = "",
        buttons: Optional[list[str]] = None,
        callback: Optional[Callable[[str], None]] = None,
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
        html = json.dumps(self._render())
        a._eval_js(
            f"(function(){{"
            f'var e=document.getElementById("{self._id}-ov");'
            f"if(!e){{"
            f'document.body.insertAdjacentHTML("beforeend",{html});'
            f"}}"
            f'window.location.hash="{self._id}-ov";'
            f"}})()"
        )

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def _render(self) -> str:
        title = self._escape(self._config_dict.get("_dialog_title", ""))
        text = self._escape(self._config_dict.get("_dialog_text", ""))
        buttons = self._config_dict.get("_dialog_buttons", ["OK"])
        bid = self._id
        btns_html = "".join(
            f'<button class="iskg-btn" onclick="iskg_bridge_event(\'{bid}\',\'result\',{json.dumps(b)})">{self._escape(b)}</button>'
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
        if event_name == "result" and self._dialog_callback:
            self._dialog_callback(str(event_data))
            self._dialog_callback = None
        super()._handle_bridge_event(event_name, event_data)


def showinfo(
    title: str = "",
    text: str = "",
    parent: Optional[Widget] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> MessageDialog:
    """Show an info message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showwarning(
    title: str = "",
    text: str = "",
    parent: Optional[Widget] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> MessageDialog:
    """Show a warning message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showerror(
    title: str = "",
    text: str = "",
    parent: Optional[Widget] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> MessageDialog:
    """Show an error message box (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["OK"], callback=callback)
    return md


def showquestion(
    title: str = "",
    text: str = "",
    parent: Optional[Widget] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> MessageDialog:
    """Show a question dialog with Yes/No buttons (HTML overlay)."""
    md = MessageDialog(parent=parent, title=title, text=text, buttons=["Yes", "No"], callback=callback)
    return md


class FileDialog:
    """Static methods for native file open/save dialogs."""

    @staticmethod
    def open_file(
        app: Any,
        title: str = "Open",
        directory: str = "",
        file_types: Optional[list[str]] = None,
        multiple: bool = False,
    ) -> Any:
        return app.file_dialog("open", directory, file_types, multiple)

    @staticmethod
    def save_file(
        app: Any,
        title: str = "Save As",
        directory: str = "",
        file_types: Optional[list[str]] = None,
    ) -> Any:
        return app.file_dialog("save", directory, file_types, False)

    @staticmethod
    def open_folder(
        app: Any,
        title: str = "Select Folder",
        directory: str = "",
    ) -> Any:
        return app.file_dialog("folder", directory, None, False)
