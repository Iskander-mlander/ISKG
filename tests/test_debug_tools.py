"""Tests for the debug toolset: bridge trace, tree dumps, inspector, fps."""

import json
import threading
import time

from iskg import Application, Button, Label, VBox, WidgetInspector
from iskg.app import _HANDLERS, _JSAPI, _JSAPI_INSTANCE, _TRACE_MAX
from iskg.base import _dump_value
from iskg.debug import fps_meter


class TestBridgeTrace:
    def test_js_out_recorded(self):
        app = Application("t")
        app.trace_clear()
        label = Label(text="hi")
        app.add(label)
        app.test_loop()
        label.text = "bye"
        outs = [e for e in app.trace() if e["kind"] == "js-out"]
        assert outs, "no js-out entries"
        assert any("iskg_set_text" in (e.get("js") or "") for e in outs)
        assert all(e["bytes"] > 0 for e in outs)

    def test_event_in_and_unhandled_recorded(self):
        app = Application("t")
        app.trace_clear()
        app.test_loop()
        _JSAPI_INSTANCE.on_event("iw-nonexistent", "click", None)
        kinds = [(e["kind"], e.get("widget")) for e in app.trace()]
        assert ("event-in", "iw-nonexistent") in kinds
        assert ("event-unhandled", "iw-nonexistent") in kinds

    def test_debounced_duplicate_recorded_as_dropped(self):
        app = Application("t")
        app.trace_clear()
        _JSAPI._last_event.clear()
        app.test_loop()
        # "scroll" is not in _NON_DEBOUNCED: same payload twice within
        # 50ms must be forwarded once and recorded as dropped once.
        _JSAPI_INSTANCE.on_event("iw-x", "scroll", "d")
        _JSAPI_INSTANCE.on_event("iw-x", "scroll", "d")
        kinds = [e["kind"] for e in app.trace()]
        assert kinds.count("event-in") == 2
        assert kinds.count("event-dropped") == 1
        _JSAPI._last_event.clear()

    def test_handled_event_has_no_unhandled_entry(self):
        app = Application("t")
        app.trace_clear()
        btn = Button(text="Go")
        got = []
        btn.bind("click", lambda d: got.append(d))
        app.add(btn)
        loop = app.test_loop()
        loop.fire(btn._id, "click", "x")
        assert got == ["x"]
        kinds = [e["kind"] for e in app.trace() if e.get("widget") == btn._id]
        assert "event-unhandled" not in kinds
        assert "event-in" in kinds

    def test_trace_limit_and_clear(self):
        app = Application("t")
        app.trace_clear()
        app.test_loop()
        _JSAPI_INSTANCE.on_event("iw-a", "click", None)
        _JSAPI_INSTANCE.on_event("iw-b", "click", None)
        assert len(app.trace(limit=1)) == 1
        assert app.trace(limit=0) == []
        app.trace_clear()
        assert app.trace() == []

    def test_trace_buffer_is_bounded(self):
        app = Application("t")
        app.trace_clear()
        for i in range(_TRACE_MAX + 50):
            _JSAPI_INSTANCE.on_event("iw-flood", "click", str(i))
        assert len(app.trace()) <= _TRACE_MAX
        app.trace_clear()

    def test_trace_survives_eval_error(self, monkeypatch):
        app = Application("t")
        app.trace_clear()
        app.test_loop()

        class Boom:
            def evaluate_js(self, js):
                raise RuntimeError("boom")

        monkeypatch.setattr(app, "_window", Boom())
        app.execute_js("1+1")
        errs = [e for e in app.trace() if e["kind"] == "js-error"]
        assert errs and "boom" in errs[-1]["error"]
        app.trace_clear()


class TestDumpTree:
    def _app(self):
        app = Application("t")
        with VBox() as root:
            Label(text="hi")
            Button(text="Go")
        app.add(root)
        return app, root

    def test_structure_and_types(self):
        app, root = self._app()
        dump = app.dump_tree()
        assert len(dump) == 1
        node = dump[0]
        assert node["type"] == "VBox"
        assert node["id"] == root._id
        assert node["destroyed"] is False
        types = [c["type"] for c in node["children"]]
        assert types == ["Label", "Button"]

    def test_dump_is_json_serialisable(self):
        app, _ = self._app()
        text = json.dumps(app.dump_tree())
        assert "Label" in text

    def test_dump_tree_text(self):
        app, _ = self._app()
        text = app.dump_tree_text()
        assert "VBox#iw" in text
        assert "  Label#iw" in text
        assert "text='hi'" in text

    def test_get_widget_by_id(self):
        app, root = self._app()
        label = root._children[0]
        assert app.get_widget(label._id) is label
        assert app.get_widget("iw-nonexistent") is None

    def test_widget_dump_subtree(self):
        app, root = self._app()
        sub = root._children[0].dump()
        assert sub["type"] == "Label"
        assert "children" not in sub

    def test_dump_value_sanitises(self):
        assert _dump_value("x") == "x"
        assert _dump_value("y" * 500).endswith("…")
        assert len(_dump_value("y" * 500)) < 200
        assert _dump_value([1, 2, 3]) == [1, 2, 3]
        big = _dump_value(list(range(30)))
        assert len(big) == 13 and big[-1] == "…(18 more)"
        assert _dump_value(lambda: None).startswith("<function")
        assert _dump_value(None) is None


class TestWidgetInspector:
    def test_enable_registers_handler_and_queues_js(self):
        app = Application("t")
        insp = WidgetInspector(app)
        insp.enable()  # before any window: must queue, not raise
        try:
            assert _HANDLERS.get("iskg-inspector") == insp._on_pick
            assert app._pending_js, "enable() before run() should queue JS"
            loop = app.test_loop()
            assert any("iskg-inspector" in c for c in loop.js_calls)
        finally:
            insp.disable()

    def test_pick_reports_widget_and_emits_event(self):
        app = Application("t")
        label = Label(text="hi")
        app.add(label)
        loop = app.test_loop()
        insp = WidgetInspector(app)
        insp.enable()
        picked = []
        app.on("widget-picked", lambda info: picked.append(info))
        loop.fire("iskg-inspector", "pick", label._id)
        assert picked and picked[0]["type"] == "Label"
        assert picked[0]["id"] == label._id
        assert any("iskg_inspect_show" in c for c in loop.js_calls)
        insp.disable()

    def test_pick_unknown_widget_reports_error(self):
        app = Application("t")
        loop = app.test_loop()
        insp = WidgetInspector(app)
        insp.enable()
        picked = []
        app.on("widget-picked", lambda info: picked.append(info))
        loop.fire("iskg-inspector", "pick", "iw-404")
        assert picked and "error" in picked[0]
        insp.disable()

    def test_disable_removes_handler(self):
        app = Application("t")
        app.test_loop()
        insp = WidgetInspector(app)
        insp.enable()
        insp.disable()
        assert _HANDLERS.get("iskg-inspector") is None


class TestFpsMeter:
    def test_fps_meter_uses_widget_event(self):
        app = Application("t")
        loop = app.test_loop()
        result = []

        def run():
            result.append(fps_meter(app, duration_s=0.3))

        t = threading.Thread(target=run, daemon=True)
        t.start()
        deadline = time.time() + 2.0
        while "__fps__" not in _HANDLERS and time.time() < deadline:
            time.sleep(0.01)
        loop.fire("__fps__", "done", "42")
        t.join(timeout=3.0)
        assert result, "fps_meter did not return"
        assert abs(result[0] - 42 / 0.3) < 0.001
        assert "__fps__" not in _HANDLERS, "handler must be cleaned up"


class TestInjectJs:
    def test_queued_then_flushed_by_test_loop(self):
        app = Application("t")
        app.inject_js("window.__injected=1;")
        assert app._pending_js
        loop = app.test_loop()
        assert any("__injected=1" in c for c in loop.js_calls)
        assert not app._pending_js

    def test_direct_when_running(self):
        app = Application("t")
        loop = app.test_loop()
        app.inject_js("window.__direct=1;")
        assert any("__direct=1" in c for c in loop.js_calls)
        assert not app._pending_js
