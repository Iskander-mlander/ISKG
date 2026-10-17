from iskg import (
    Application,
    Box,
    Button,
    Entry,
    HBox,
    Label,
    LogViewer,
    Text,
    TreeView,
    VBox,
)
from iskg import ComboBox as Combo


class TestBox:
    def test_box_is_frame(self):
        b = Box()
        assert isinstance(b, Box)

    def test_add_registers_child(self):
        b = Box()
        child = Label(parent=b, text="x")
        assert child in b._children
        assert child._layout_mode == "pack"
        assert child._layout_info.get("side") == "top"

    def test_vbox_default_fill_x(self):
        b = VBox()
        child = Label(parent=b)
        assert child._layout_info.get("fill") == "x"

    def test_hbox_default_fill_none(self):
        b = HBox()
        child = Label(parent=b)
        assert child._layout_info.get("fill") == "none"

    def test_box_tuple_padding_applies_to_children(self):
        b = VBox(padx=(6, 2), pady=(0, 8))
        child = b.label("x")
        assert child._layout_info.get("padx") == (6, 2)
        assert child._layout_info.get("pady") == (0, 8)
        style = child._render_style()
        assert "margin-left:6px;margin-right:2px;" in style
        assert "margin-top:0px;margin-bottom:8px;" in style

    def test_box_per_child_padding_override(self):
        b = VBox(padx=4, pady=4)
        child = Label(parent=b, text="x")
        b.add(child, padx=(1, 9))
        assert child._layout_info.get("padx") == (1, 9)
        assert child._layout_info.get("pady") == 4

    def test_shorthand_creators(self):
        b = VBox()
        btn = b.button("OK", command=lambda: None)
        lbl = b.label("Hola")
        assert isinstance(btn, Button)
        assert btn in b._children
        assert btn._config_dict.get("text") == "OK"
        assert lbl in b._children

    def test_render_contains_all_children(self):
        app = Application("t", 400, 300)
        root = VBox(gap=8)
        files = HBox(gap=6)
        root.add(files)
        files.button("uno")
        files.button("dos")
        root.label("tres")
        app.add(root)
        html = app._build_html()
        assert "uno" in html
        assert "dos" in html
        assert "tres" in html

    def test_first_child_renders(self):
        b = VBox()
        b.button("primero")
        b.button("segundo")
        assert len(b._children) == 2
        html = Application("t", 400, 300)
        html._root_widgets.append(b)
        out = html._build_html()
        assert "primero" in out
        assert "segundo" in out


class TestBoxLayoutContextManager:
    def test_autoparent_into_active_box(self):
        with VBox() as root:
            lbl = Label("Hola")
        assert lbl._parent is root
        assert lbl in root._children
        assert lbl._layout_mode == "pack"

    def test_nested_boxes(self):
        with VBox() as root:
            with HBox() as sub:
                btn = Button("A")
        assert btn._parent is sub
        assert sub._parent is root
        assert sub in root._children
        assert btn in sub._children

    def test_stack_cleaned_after_exit(self):
        from iskg.base import _LAYOUT_STACK

        with VBox() as root:
            with HBox():
                Label("x")
            assert _LAYOUT_STACK[-1] is root
        assert _LAYOUT_STACK == []

    def test_render_with_context_manager(self):
        app = Application("t", 720, 520)
        with VBox(gap=8, padx=8) as root:
            Label("RPSaveFixer", font="bold 16px")
            with HBox(gap=6):
                Button("Cargar corrupto", command=lambda: None)
                Button("Cargar referencia")
            with HBox(gap=6):
                Label("Base antigua:")
                Entry(width=320)
            with HBox(gap=6):
                Button("Seleccionar carpeta")
                Combo(values=["renpy7-py2", "renpy8-py3"])
            with HBox(gap=6):
                TreeView(width=340, height=300)
                Text(width=340, height=300)
            LogViewer(height=120)
        app.add(root)
        out = app._build_html()
        for t in [
            "RPSaveFixer",
            "Cargar corrupto",
            "Cargar referencia",
            "Base antigua:",
            "Seleccionar carpeta",
            "renpy7-py2",
        ]:
            assert t in out, t
