"""Demuestra la reactividad en caliente de ISKG.

Muestra cómo cambiar props vía ``config()``/setter se refleja en el DOM sin
recrear el widget: color/fg/bg (capa base ``_CONFIG_TO_CSS``), ``disabled``,
``text``, ``value``, ``ComboBox.values`` e ``IndicatorLED.color``.

Ejecuta: ``python -m examples.reactivity_demo``
"""

from iskg import (
    Application,
    Button,
    ComboBox,
    Frame,
    IndicatorLED,
    Label,
    ProgressBar,
    Slider,
)


def build_app() -> Application:
    app = Application(title="Reactivity demo", width=420, height=560)
    root = Frame(parent=None)
    root.grid_columnconfigure(0, weight=1)

    label = Label(parent=root, text="Texto inicial", anchor="center")
    label.grid(row=0, column=0, pady=6)

    led = IndicatorLED(parent=root, color="green", label="estado")
    led.grid(row=1, column=0, pady=6)

    bar = ProgressBar(parent=root, value=10, show_text=True)
    bar.grid(row=2, column=0, sticky="we", padx=12, pady=6)

    slider = Slider(parent=root, from_=0, to=100, value=10)
    slider.grid(row=3, column=0, sticky="we", padx=12, pady=6)

    combo = ComboBox(parent=root, values=["uno", "dos", "tres"])
    combo.grid(row=4, column=0, sticky="we", padx=12, pady=6)

    btn = Button(
        parent=root,
        text="Cambiar todo",
        command=lambda: on_change(),
    )
    btn.grid(row=5, column=0, pady=8)

    def on_change() -> None:
        label.text = "Texto cambiado"
        label.config(fg="red", bg="#22304a")
        led.color = "red"
        bar.value = 80
        slider.value = 80
        combo.values = ["alpha", "beta", "gamma", "delta"]
        btn.config(disabled=True)

    app.add(root)
    return app


if __name__ == "__main__":
    build_app().run()
