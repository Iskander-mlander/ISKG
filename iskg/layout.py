class PackLayout:
    def __init__(self, container):
        self.container = container

    def render_open(self):
        side = "top"
        for child in self.container._children:
            if child._layout_mode == "pack":
                s = child._layout_info.get("side", "top")
                if s in ("top", "bottom", "left", "right"):
                    side = s
                break
        dir_class = {
            "top": "iskg-pack-top",
            "bottom": "iskg-pack-bottom",
            "left": "iskg-pack-left",
            "right": "iskg-pack-right",
        }
        cls = dir_class.get(side, "iskg-pack-top")
        return f'<div class="{cls}" style="display:flex;flex-direction:{"column" if side in ("top", "bottom") else "row"}{"-reverse" if side in ("bottom", "right") else ""};min-height:0;min-width:0;gap:2px;">'

    def render_close(self):
        return "</div>"


class GridLayout:
    def __init__(self, container):
        self.container = container

    def render_open(self):
        max_row = 0
        max_col = 0
        for child in self.container._children:
            if child._layout_mode == "grid":
                li = child._layout_info
                r = li.get("row", 0) + li.get("rowspan", 1)
                c = li.get("column", 0) + li.get("columnspan", 1)
                max_row = max(max_row, r)
                max_col = max(max_col, c)
        rows = max(1, max_row)
        cols = max(1, max_col)
        return f'<div class="iskg-grid" style="grid-template-rows:repeat({rows},auto);grid-template-columns:repeat({cols},1fr);min-height:0;min-width:0;">'

    def render_close(self):
        return "</div>"


class PlaceLayout:
    @staticmethod
    def render_open():
        return '<div style="position:relative;flex:1;min-height:0;min-width:0;">'

    @staticmethod
    def render_close():
        return "</div>"
