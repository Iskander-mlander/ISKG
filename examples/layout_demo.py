"""Demuestra layout: sidebar fijo (``Frame(flex=False)``) y PanedWindow con
``sash_pos`` inicial.

Ejecuta: ``python -m examples.layout_demo``
"""

from iskg import Application, Button, Frame, Label, PanedWindow


def build_app() -> Application:
    app = Application(title="Layout demo", width=620, height=400)

    sidebar = Frame(
        parent=None,
        direction="column",
        width=180,
        flex=False,
        text="Menú",
    )
    Label(parent=sidebar, text="Item 1").grid(row=0, column=0, pady=4)
    Label(parent=sidebar, text="Item 2").grid(row=1, column=0, pady=4)
    Button(parent=sidebar, text="Acción").grid(row=2, column=0, pady=4)

    pw = PanedWindow(parent=None, orient="horizontal", sash_pos=0.7)
    left = Frame(parent=pw, text="Izquierda")
    Label(parent=left, text="Panel izquierdo").grid(row=0, column=0, pady=8)
    right = Frame(parent=pw, text="Derecha")
    Label(parent=right, text="Panel derecho").grid(row=0, column=0, pady=8)

    app.add(sidebar)
    app.add(pw)
    return app


if __name__ == "__main__":
    build_app().run()
