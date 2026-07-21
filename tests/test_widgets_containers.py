from iskg import Frame, Notebook, Separator, Spacer, ScrollBar


class TestFrame:
    def test_create(self):
        f = Frame(text="Group")
        assert f._config_dict.get("text") == "Group"

    def test_render_with_text(self):
        f = Frame(text="Controls")
        html = f._render()
        assert "iskg-frame" in html
        assert "Controls" in html

    def test_add_child(self):
        f = Frame()
        from iskg import Label

        lbl = Label(parent=f, text="inside")
        assert lbl in f._children


class TestNotebook:
    def test_create(self):
        nb = Notebook()
        assert len(nb._tabs) == 0

    def test_add_tab(self):
        nb = Notebook()
        from iskg import Label

        l1 = Label(text="Content 1")
        nb.add_tab("Tab 1", l1)
        assert len(nb._tabs) == 1
        assert nb._tabs[0]["title"] == "Tab 1"

    def test_render_html(self):
        nb = Notebook()
        from iskg import Label

        nb.add_tab("A", Label(text="page1"))
        html = nb._render()
        assert "iskg-notebook" in html
        assert "iskg-tabbar" in html


class TestSeparator:
    def test_create_horizontal(self):
        s = Separator(orient="horizontal")
        html = s._render()
        assert "iskg-hsep" in html

    def test_create_vertical(self):
        s = Separator(orient="vertical")
        html = s._render()
        assert "iskg-vsep" in html


class TestSpacer:
    def test_create(self):
        sp = Spacer(width=10, height=20)
        html = sp._render()
        assert "iskg-spacer" in html

    def test_expand(self):
        sp = Spacer(expand=True)
        html = sp._render()
        assert "flex:1" in html


class TestScrollBar:
    def test_create_vertical(self):
        sb = ScrollBar(orient="vertical", value=30, height=100)
        html = sb._render()
        assert "iskg-scrollbar-vert" in html

    def test_create_horizontal(self):
        sb = ScrollBar(orient="horizontal", value=50, width=100)
        html = sb._render()
        assert "iskg-scrollbar-horiz" in html
