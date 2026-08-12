"""Demuestra los widgets de datos: ``ListBox``, ``DataGrid``, ``TreeView`` y
``DropTarget``.

Incluye selección reactiva (``command``) que refleja el ítem elegido en una
etiqueta de estado, ordenamiento por columna en el ``DataGrid`` y una jerarquía
plegable en el ``TreeView``.

Ejecuta: ``python -m examples.data_widgets_demo``
"""

from iskg import (
    Application,
    DataGrid,
    DropTarget,
    Frame,
    Label,
    ListBox,
    TreeView,
)


def build_app() -> Application:
    app = Application(title="Data widgets demo", width=620, height=560)
    root = Frame(parent=None)
    root.grid_columnconfigure(0, weight=1)

    status = Label(parent=root, text="Selecciona algo…")
    status.grid(row=0, column=0, sticky="we", padx=6, pady=(0, 6))

    # ---- ListBox ----
    list_frame = Frame(parent=root, text="ListBox")
    list_frame.grid(row=1, column=0, sticky="we", padx=6, pady=(0, 6))
    listbox = ListBox(
        parent=list_frame,
        items=["alpha", "beta", "gamma", "delta", "epsilon"],
    )
    listbox.grid(row=0, column=0, padx=6, pady=6)
    listbox.bind(
        "change",
        lambda idx: status.config(text=f"ListBox → {listbox.items[int(idx)]}"),
    )

    # ---- DataGrid ----
    grid_frame = Frame(parent=root, text="DataGrid (ordenable)")
    grid_frame.grid(row=2, column=0, sticky="we", padx=6, pady=(0, 6))
    grid = DataGrid(
        parent=grid_frame,
        columns=["Nombre", "Tipo", "Peso"],
        rows=[
            ["Manzana", "fruta", "120g"],
            ["Zanahoria", "verdura", "80g"],
            ["Plátano", "fruta", "150g"],
            ["Brócoli", "verdura", "90g"],
        ],
    )
    grid.grid(row=0, column=0, padx=6, pady=6)

    # ---- TreeView ----
    tree_frame = Frame(parent=root, text="TreeView")
    tree_frame.grid(row=3, column=0, sticky="we", padx=6, pady=(0, 6))
    tree = TreeView(
        parent=tree_frame,
        items=[
            {
                "text": "Proyecto",
                "children": [
                    {
                        "text": "src",
                        "children": [
                            {"text": "main.py"},
                            {"text": "utils.py"},
                        ],
                    },
                    {"text": "README.md"},
                ],
            },
            {"text": "LICENSE"},
        ],
    )
    tree.grid(row=0, column=0, padx=6, pady=6)

    # ---- DropTarget ----
    drop_frame = Frame(parent=root, text="DropTarget")
    drop_frame.grid(row=4, column=0, sticky="we", padx=6, pady=(0, 6))
    drop = DropTarget(
        parent=drop_frame,
        text="Suelta archivos aquí",
    )
    drop.grid(row=0, column=0, padx=6, pady=6)
    drop.bind(
        "<<Drop>>",
        lambda files: status.config(text=f"Drop → {files}"),
    )

    app.add(root)
    return app


if __name__ == "__main__":
    build_app().run()
