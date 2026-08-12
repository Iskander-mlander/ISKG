"""Demuestra el cambio de tema en caliente (``Application.set_theme``).

Permite elegir entre todos los temas registrados (``iskg.themes.available_themes``)
y aplicarlos en runtime sobre un conjunto de widgets de muestra, además de un
botón que recorre los temas cíclicamente.

Ejecuta: ``python -m examples.theming_demo``
"""

from iskg import (
    Application,
    Button,
    ComboBox,
    Frame,
    Label,
    ProgressBar,
)
from iskg.themes import available_themes


def build_app() -> Application:
    app = Application(title="Theming demo", width=520, height=520)
    app.set_theme("ifaz")

    themes = available_themes()
    initial = themes.index(app.current_theme()) if app.current_theme() in themes else 0
    root = Frame(parent=None)
    root.grid_columnconfigure(0, weight=1)

    header = Label(parent=root, text="Selector de tema")
    header.grid(row=0, column=0, pady=(0, 6))

    status = Label(parent=root, text=f"Tema actual: {app.current_theme()}")
    status.grid(row=1, column=0, pady=(0, 6))

    combo = ComboBox(parent=root, values=themes, current=initial)
    combo.grid(row=2, column=0, sticky="we", padx=12, pady=(0, 6))

    preview = Frame(parent=root, text="Vista previa")
    preview.grid(row=3, column=0, sticky="we", padx=12, pady=(0, 6))
    Button(parent=preview, text="Botón").grid(row=0, column=0, padx=4, pady=6)
    Button(parent=preview, text="Peligro", style="danger").grid(
        row=0, column=1, padx=4, pady=6
    )
    bar = ProgressBar(parent=preview, value=65, show_text=True)
    bar.grid(row=1, column=0, columnspan=2, sticky="we", padx=4, pady=6)

    def apply_selected() -> None:
        name = themes[combo.current]
        app.set_theme(name)
        status.text = f"Tema actual: {app.current_theme()}"

    apply_btn = Button(parent=root, text="Aplicar tema", command=apply_selected)
    apply_btn.grid(row=4, column=0, pady=(0, 6))

    idx = {"n": 0}

    def cycle() -> None:
        idx["n"] = (idx["n"] + 1) % len(themes)
        name = themes[idx["n"]]
        app.set_theme(name)
        combo.current = idx["n"]
        status.text = f"Tema actual: {app.current_theme()}"

    cycle_btn = Button(
        parent=root,
        text="Siguiente tema",
        command=cycle,
    )
    cycle_btn.grid(row=5, column=0, pady=(0, 6))

    app.add(root)
    return app


if __name__ == "__main__":
    build_app().run()
