from iskg import Frame, Label, Notebook, ScrollBar, Separator, Spacer


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
        lbl = Label(parent=f, text="inside")
        assert lbl in f._children

    def test_container_disabled(self):
        f = Frame(container=False)
        Label(f, text="a").pack()
        html = f._render()
        assert "display:flex" not in html.split("iskg-frame")[1].split(">")[0]

    def test_direction_explicit(self):
        f = Frame(direction="row")
        Label(f, text="a").pack(side="left")
        Label(f, text="b").pack(side="left")
        html = f._render()
        assert "flex-direction:row" in html

    def test_direction_auto(self):
        f = Frame(direction="auto")
        Label(f, text="a").pack(side="left")
        html = f._render()
        assert "flex-direction:row" in html

    def test_gap_custom(self):
        f = Frame(gap=12)
        Label(f, text="a").pack()
        html = f._render()
        assert "gap:12px" in html

    def test_skip_hidden_true_default(self):
        f = Frame()
        Label(f, text="v").pack()
        l2 = Label(f, text="h").pack()
        l2.config(hidden=True)
        html = f._render()
        assert "display:none" not in html

    def test_skip_hidden_false(self):
        f = Frame(skip_hidden=False)
        Label(f, text="v").pack()
        l2 = Label(f, text="h").pack()
        l2.config(hidden=True)
        html = f._render()
        assert "display:none" in html

    def test_height_mode_percent(self):
        f = Frame(height_mode="percent")
        Label(f, text="a").pack()
        html = f._render()
        assert "height:100%" in html

    def test_height_mode_flex(self):
        f = Frame(height_mode="flex")
        Label(f, text="a").pack()
        html = f._render()
        assert "flex:1" in html

    def test_propagate_string(self):
        f = Frame(propagate="auto")
        Label(f, text="a").pack()
        html = f._render()
        assert "overflow:auto" in html


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


class TestIntegration:
    def test_scrolledframe_panedwindow_grid_mixed(self):
        from iskg import Frame, Label, PanedWindow, ScrolledFrame

        root = Frame()
        sf = ScrolledFrame(root, width=400, height=300)
        pw = PanedWindow(sf, orient="horizontal")
        left = Frame(pw)
        right = Frame(pw)
        l1 = Label(left, text="left-top")
        l1.grid(row=0, column=0)
        l2 = Label(left, text="left-bottom")
        l2.grid(row=1, column=0)
        Label(right, text="right-pane").pack()

        html = root._render()
        assert "iskg-scrollframe" in html
        assert "iskg-panedwindow" in html
        assert "iskg-grid" in html
        assert "display:grid" in html
        assert "left-top" in html
        assert "left-bottom" in html
        assert "right-pane" in html
        assert "iskg-sash" in html
