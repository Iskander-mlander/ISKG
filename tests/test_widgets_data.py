from iskg import DataGrid, DropTarget, FileDialog, ListBox, Menu, MenuBar, TreeView
from iskg.widgets._menus import MenuItem


class TestListBox:
    def test_create(self):
        lb = ListBox(items=["A", "B", "C"])
        assert lb.items == ["A", "B", "C"]

    def test_append(self):
        lb = ListBox()
        lb.append("X")
        assert lb.items == ["X"]

    def test_insert(self):
        lb = ListBox(items=["A", "C"])
        lb.insert(1, "B")
        assert lb.items == ["A", "B", "C"]

    def test_delete(self):
        lb = ListBox(items=["A", "B", "C"])
        lb.delete(1)
        assert lb.items == ["A", "C"]

    def test_clear(self):
        lb = ListBox(items=["A", "B"])
        lb.clear()
        assert lb.items == []

    def test_render_html(self):
        lb = ListBox(items=["Alpha", "Beta"])
        html = lb._render()
        assert "iskg-listbox" in html


class TestDataGrid:
    def test_create(self):
        dg = DataGrid(columns=["Name", "Value"], rows=[["A", "1"]])
        assert dg.rows == [["A", "1"]]

    def test_render_html(self):
        dg = DataGrid(
            columns=["Col1", "Col2"],
            rows=[["x", "y"], ["z", "w"]],
        )
        html = dg._render()
        assert "iskg-datagrid" in html
        assert "Col1" in html


class TestTreeView:
    def test_create(self):
        tv = TreeView(items=[{"text": "Root"}])
        html = tv._render()
        assert "iskg-tree" in html

    def test_render_with_children(self):
        tv = TreeView(items=[{"text": "A", "children": [{"text": "B"}]}])
        html = tv._render()
        assert "iskg-tree-children" in html


class TestDropTarget:
    def test_create(self):
        dt = DropTarget(text="Drop here")
        html = dt._render()
        assert "iskg-droptarget" in html
        assert "Drop here" in html


class TestMenuBar:
    def test_create(self):
        mb = MenuBar()
        mb.add_menu("File")
        assert len(mb._menus) == 1
        assert mb._menus[0].text == "File"

    def test_add_item(self):
        mb = MenuBar()
        m = mb.add_menu("Edit")
        item = m.add_item("Undo", command=lambda: None)
        assert item.text == "Undo"

    def test_add_submenu(self):
        mb = MenuBar()
        m = mb.add_menu("File")
        sub = m.add_menu("Recent")
        sub.add_item("Project A")
        assert len(m.items) == 1
        assert m.items[0] is not None
        assert m.items[0].submenu is not None

    def test_add_separator(self):
        mb = MenuBar()
        m = mb.add_menu("View")
        m.add_separator()
        assert m.items[0] is None

    def test_find_command(self):
        mb = MenuBar()
        calls = []
        m = mb.add_menu("File")
        m.add_item("Open", command=lambda: calls.append("open"))
        cmd = mb._find_command(["File", "Open"])
        assert cmd is not None
        cmd()
        assert calls == ["open"]

    def test_find_command_nested(self):
        mb = MenuBar()
        calls = []
        m = mb.add_menu("File")
        sub = m.add_menu("Recent")
        sub.add_item("Project A", command=lambda: calls.append("proj_a"))
        cmd = mb._find_command(["File", "Recent", "Project A"])
        assert cmd is not None
        cmd()
        assert calls == ["proj_a"]

    def test_render_html(self):
        mb = MenuBar()
        mb.add_menu("File")
        html = mb._render()
        assert "iskg-menubar" in html


def test_filedialog_static_methods():
    assert hasattr(FileDialog, "open_file")
    assert hasattr(FileDialog, "save_file")
    assert hasattr(FileDialog, "open_folder")


# ── Menu / MenuItem ───────────────────────────────────────────────────


class TestMenuItem:
    def test_create(self):
        item = MenuItem("Save", command=lambda: None, shortcut="Ctrl+S", icon="💾")
        assert item.text == "Save"
        assert item.command is not None
        assert item.shortcut == "Ctrl+S"
        assert item.icon == "💾"
        assert item.submenu is None

    def test_create_minimal(self):
        item = MenuItem("Quit")
        assert item.text == "Quit"
        assert item.command is None
        assert item.shortcut == ""
        assert item.icon == ""


class TestMenu:
    def test_create(self):
        m = Menu("File")
        assert m.text == "File"
        assert m.items == []

    def test_add_item(self):
        m = Menu("Edit")
        item = m.add_item("Copy", command=lambda: None)
        assert len(m.items) == 1
        assert item.text == "Copy"

    def test_add_separator(self):
        m = Menu("View")
        m.add_separator()
        assert m.items[0] is None

    def test_add_menu(self):
        m = Menu("File")
        sub = m.add_menu("Recent")
        assert isinstance(sub, Menu)
        assert sub.text == "Recent"
        assert m.items[0].submenu is sub

    def test_counter_increments(self):
        before = Menu._counter
        m1 = Menu("A")
        m2 = Menu("B")
        assert m2._id != m1._id
        assert Menu._counter == before + 2


class TestMenuBarExtended:
    def test_render_js_returns_js(self):
        mb = MenuBar()
        mb.add_menu("File")
        js = mb._render_js()
        assert "iskg-menubar" in js
        assert "function" in js

    def test_render_update_js_empty(self):
        mb = MenuBar()
        assert mb._render_update_js() == ""

    def test_find_command_not_found(self):
        mb = MenuBar()
        mb.add_menu("File")
        assert mb._find_command(["Nonexistent"]) is None

    def test_find_command_empty_path(self):
        mb = MenuBar()
        mb.add_menu("File")
        assert mb._find_command([]) is None

    def test_find_command_partial_path(self):
        mb = MenuBar()
        m = mb.add_menu("File")
        m.add_menu("Recent")  # no command on the submenu itself
        assert mb._find_command(["File", "Recent"]) is None

    def test_handle_bridge_event_command(self):
        mb = MenuBar()
        calls = []
        m = mb.add_menu("File")
        m.add_item("Open", command=lambda: calls.append("opened"))
        mb._handle_bridge_event("command", "File/Open")
        assert calls == ["opened"]

    def test_handle_bridge_event_other_event(self):
        mb = MenuBar()
        mb._handle_bridge_event("click", None)  # should not raise

    def test_render_menu_with_separator(self):
        mb = MenuBar()
        m = mb.add_menu("Edit")
        m.add_item("Cut", shortcut="Ctrl+X")
        m.add_separator()
        m.add_item("Copy", shortcut="Ctrl+C", icon="📋")
        m.add_separator()
        m.add_item("Paste", command=lambda: None)
        html = mb._render()
        assert "iskg-menu-sep" in html
        assert "Ctrl+X" in html
        assert "📋" in html
        assert "iskg-menu-sc" in html
        assert "iskg-menu-ico" in html

    def test_render_menu_with_submenu(self):
        mb = MenuBar()
        m = mb.add_menu("File")
        sub = m.add_menu("Recent")
        sub.add_item("Project A")
        sub.add_separator()
        sub.add_item("Clear")
        html = mb._render()
        assert "iskg-menu-sub" in html
        assert "▸" in html
        assert "iskg-menu-dd" in html

    def test_walk_items_empty_parts(self):
        mb = MenuBar()
        m = mb.add_menu("File")
        m.add_item("Open")
        assert mb._find_command(["File"]) is None

    def test_walk_items_skips_separator(self):
        mb = MenuBar()
        m = mb.add_menu("View")
        m.add_separator()
        m.add_item("Zoom", command=lambda: None)
        cmd = mb._find_command(["View", "Zoom"])
        assert cmd is not None

    def test_walk_items_no_match(self):
        mb = MenuBar()
        mb.add_menu("File")
        assert mb._find_command(["File", "Nonexistent"]) is None
