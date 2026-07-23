"""Tests for MessageDialog, FileDialog, and convenience functions."""

from unittest.mock import MagicMock

from iskg import MessageDialog, Widget
from iskg.app import _HANDLERS
from iskg.widgets._dialogs import FileDialog, showerror, showinfo, showquestion, showwarning

# ── MessageDialog ──────────────────────────────────────────────────────


class TestMessageDialog:
    def test_create_defaults(self):
        d = MessageDialog()
        assert d._config_dict.get("_dialog_title") == ""
        assert d._config_dict.get("_dialog_text") == ""
        assert d._config_dict.get("_dialog_buttons") == ["OK"]

    def test_create_custom(self):
        d = MessageDialog(title="Hello", text="World", buttons=["Yes", "No"])
        assert d._config_dict.get("_dialog_title") == "Hello"
        assert d._config_dict.get("_dialog_text") == "World"
        assert d._config_dict.get("_dialog_buttons") == ["Yes", "No"]

    def test_create_with_callback(self):
        def cb(x):
            return None

        d = MessageDialog(callback=cb)
        assert d._dialog_callback is cb

    def test_show_no_app_does_nothing(self):
        d = MessageDialog()
        d.show(app=None)  # should not raise

    def test_show_registers_handler(self):
        app = MagicMock()
        d = MessageDialog(title="Test")
        d.show(app=app)
        handler = _HANDLERS.get(d._id)
        bound = d._handle_bridge_event
        assert handler is not None
        assert handler.__self__ is bound.__self__
        assert handler.__func__ is bound.__func__
        # cleanup
        _HANDLERS.pop(d._id, None)

    def test_show_calls_eval_js(self):
        app = MagicMock()
        d = MessageDialog(title="Test", text="Body")
        d.show(app=app)
        app._eval_js.assert_called_once()
        js = app._eval_js.call_args[0][0]
        assert "iskg-msgbox-overlay" in js
        assert d._id in js

    def test_show_json_encodes_html(self):
        app = MagicMock()
        d = MessageDialog(title="Test", text="Body")
        d.show(app=app)
        js = app._eval_js.call_args[0][0]
        # The HTML is JSON-encoded inside the JS
        assert "Test" in js
        assert "Body" in js

    def test_handle_result_calls_callback(self):
        app = MagicMock()
        calls = []
        d = MessageDialog(title="T", callback=lambda r: calls.append(r))
        d.show(app=app)
        _HANDLERS[d._id]("result", "OK")
        assert calls == ["OK"]

    def test_handle_result_cleans_up_handler(self):
        app = MagicMock()
        d = MessageDialog(title="T")
        d.show(app=app)
        assert d._id in _HANDLERS
        _HANDLERS[d._id]("result", "OK")
        assert d._id not in _HANDLERS

    def test_handle_result_callback_one_shot(self):
        app = MagicMock()
        calls = []
        d = MessageDialog(title="T", callback=lambda r: calls.append(r))
        d.show(app=app)
        _HANDLERS[d._id]("result", "OK")
        assert calls == ["OK"]
        # handler removed, so second call would be KeyError — that's correct
        assert d._id not in _HANDLERS

    def test_handle_other_event_skipped(self):
        app = MagicMock()
        calls = []
        d = MessageDialog(title="T", callback=lambda r: calls.append(r))
        d.show(app=app)
        _HANDLERS[d._id]("close", None)
        assert calls == []
        assert d._id in _HANDLERS  # still registered, not consumed
        _HANDLERS.pop(d._id, None)

    def test_escape_escapes_html(self):
        d = MessageDialog()
        result = d._escape('<script>alert("x")</script>')
        assert "<" not in result
        assert '"' not in result
        assert "&lt;" in result
        assert "&quot;" in result

    def test_render_returns_html(self):
        d = MessageDialog(title="Info", text="Hello", buttons=["OK", "Cancel"])
        html = d._render()
        assert "iskg-msgbox-overlay" in html
        assert "Info" in html
        assert "Hello" in html
        assert "OK" in html
        assert "Cancel" in html

    def test_show_twice_same_dialog(self):
        app = MagicMock()
        d = MessageDialog(title="T")
        d.show(app=app)
        first_id = d._id
        _HANDLERS.pop(d._id, None)
        d.show(app=app)
        handler = _HANDLERS.get(first_id)
        bound = d._handle_bridge_event
        assert handler is not None
        assert handler.__self__ is bound.__self__
        assert handler.__func__ is bound.__func__
        _HANDLERS.pop(first_id, None)


# ── Convenience functions ─────────────────────────────────────────────


class TestConvenienceFunctions:
    def test_showinfo_returns_dialog(self):
        d = showinfo(title="Info", text="Hello")
        assert isinstance(d, MessageDialog)
        assert d._config_dict.get("_dialog_title") == "Info"
        assert d._config_dict.get("_dialog_text") == "Hello"
        assert d._config_dict.get("_dialog_buttons") == ["OK"]

    def test_showwarning_returns_dialog(self):
        d = showwarning(title="Warning", text="Careful")
        assert isinstance(d, MessageDialog)
        assert d._config_dict.get("_dialog_buttons") == ["OK"]

    def test_showerror_returns_dialog(self):
        d = showerror(title="Error", text="Boom")
        assert isinstance(d, MessageDialog)
        assert d._config_dict.get("_dialog_buttons") == ["OK"]

    def test_showquestion_returns_dialog(self):
        d = showquestion(title="Question", text="Continue?")
        assert isinstance(d, MessageDialog)
        assert d._config_dict.get("_dialog_buttons") == ["Yes", "No"]

    def test_convenience_functions_accept_callback(self):
        def cb(r):
            return None

        d = showinfo(callback=cb)
        assert d._dialog_callback is cb

    def test_convenience_functions_accept_parent(self):
        parent = Widget()
        d = showinfo(parent=parent)
        assert d.parent is parent

    def test_convenience_returns_not_shown(self):
        # These functions return a MessageDialog without calling .show()
        d = showinfo(title="Not Shown")
        assert _HANDLERS.get(d._id) is None  # handler not registered


# ── FileDialog ─────────────────────────────────────────────────────────


class TestFileDialog:
    def test_open_file(self):
        app = MagicMock()
        app.file_dialog.return_value = "/path/file.txt"
        result = FileDialog.open_file(app, title="Open", directory="/home", file_types=["*.txt"])
        assert result == "/path/file.txt"
        app.file_dialog.assert_called_once_with("open", "/home", ["*.txt"], False, title="Open")

    def test_open_file_defaults(self):
        app = MagicMock()
        FileDialog.open_file(app)
        app.file_dialog.assert_called_once()

    def test_open_file_with_multiple(self):
        app = MagicMock()
        app.file_dialog.return_value = ["/a.txt", "/b.txt"]
        result = FileDialog.open_file(app, multiple=True)
        assert result == ["/a.txt", "/b.txt"]

    def test_save_file(self):
        app = MagicMock()
        app.file_dialog.return_value = "/out.txt"
        result = FileDialog.save_file(app, title="Save", directory="/out")
        assert result == "/out.txt"
        app.file_dialog.assert_called_once_with("save", "/out", None, False, title="Save")

    def test_save_file_defaults(self):
        app = MagicMock()
        FileDialog.save_file(app)
        app.file_dialog.assert_called_once()

    def test_open_folder(self):
        app = MagicMock()
        app.file_dialog.return_value = "/folder"
        result = FileDialog.open_folder(app, title="Select", directory="/home")
        assert result == "/folder"
        app.file_dialog.assert_called_once_with("folder", "/home", None, False, title="Select")

    def test_open_folder_defaults(self):
        app = MagicMock()
        FileDialog.open_folder(app)
        app.file_dialog.assert_called_once()

    def test_file_dialog_cancelled(self):
        app = MagicMock()
        app.file_dialog.return_value = None
        result = FileDialog.open_file(app)
        assert result is None


# ── Integration: MessageDialog render + _escape ───────────────────────


class TestMessageDialogRender:
    def test_escape_special_chars(self):
        d = MessageDialog()
        assert d._escape('a&b<c>d"e') == "a&amp;b&lt;c&gt;d&quot;e"

    def test_render_with_empty_values(self):
        d = MessageDialog()
        html = d._render()
        assert 'class="iskg-msgbox-overlay"' in html
        assert 'class="iskg-msgbox-title"></div>' in html

    def test_render_multiple_buttons(self):
        d = MessageDialog(buttons=["A", "B", "C"])
        html = d._render()
        assert html.count("iskg-btn") == 3

    def test_render_single_button(self):
        d = MessageDialog(buttons=["OK"])
        html = d._render()
        assert html.count("iskg-btn") == 1
