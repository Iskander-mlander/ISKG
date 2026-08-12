"""Example: long-running async task + fixed sidebar + window icon.

Run with::

    python examples/async_task.py

Shows the three roadmap improvements working together:
- ``app.run_async`` runs a coroutine off the UI thread.
- ``Frame(flex=False, width=...)`` builds a fixed-width sidebar.
- ``Application(icon=...)`` sets the native window icon.
"""

import time

from iskg import Application, Button, Frame, Label, TreeView


def fake_long_task(seconds: float = 2.0) -> str:
    """Pretend network/CPU work (blocking)."""
    time.sleep(seconds)
    return "tarea terminada"


def main() -> None:
    app = Application(
        title="Roadmap Demo",
        width=720,
        height=480,
        icon="icon.ico",  # ruta opcional al .ico de la ventana
    )

    main_col = Frame(app, direction="column", gap=8)
    side = Frame(app, direction="column", gap=6, text="Canciones", flex=False, width=240)

    status = Label(main_col, text="Pulsa 'Generar'...")
    Button(
        main_col,
        text="Generar",
        command=lambda: app.run_async(
            # Envolvemos la función bloqueante en una corutina.
            __import__("asyncio").to_thread(fake_long_task, 2.0),
            then=lambda result: status.config(text=f"Resultado: {result}"),
        ),
    )

    TreeView(side, items=[{"text": "demo1.mp3"}, {"text": "demo2.mp3"}], width=220, height=360)

    app.run()


if __name__ == "__main__":
    main()
