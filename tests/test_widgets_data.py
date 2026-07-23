from iskg import DataGrid, DropTarget, FileDialog, ListBox, MenuBar, TreeView


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
