# Plan de mejoras ISKG

Ideas priorizadas para el roadmap. Se implementan **de una en una**, en el orden
marcado, para no mezclar cambios. Estado general:

- [x] Menú contextual por widget (clic derecho)
- [x] Señales globales / event bus
- [x] Widgets de datos (TimeSeriesGraph, Sparkline, LogViewer, Clock, DatePicker)
- [x] Atajos globales
- [x] Drag & drop nativo

## Menú contextual por widget (clic derecho)

Done. Ver `docs/api.rst` (`_menus`) y commit de la versión 0.3.80.

## Señales globales / event bus

`app.on("evento", cb)` + `app.emit(...)` — bus ligero con eventos integrados
`theme-changed`, `closing` y `widget-created`. Soporta decorador y `app.off`.

## Widgets de datos

- `TimeSeriesGraph`/`Sparkline`: gráficos SVG multi-serie con curvas Bézier
  suavizadas, `max_pts`, `y_min`/`y_max` y `append/replace/update/clear`.
- `LogViewer`: scrollable con colores por severidad, timestamps y autoscroll.
- `Clock` (tick en vivo) y `DatePicker` (popup de calendario con navegación).

## Calidad de vida

- Atajos globales (`app.bind("<Control-...>")` sin foco en widget, soporta
  decorador).
- Drag & drop nativo entre widgets con `draggable=True` + `bind("<<Drop>>")`.

---

Estado de pendientes:

- [x] Menú contextual por widget — 2026-08-08 (`set_menu`/`popup_menu`/`bind("contextmenu")`)
- [x] Señales globales / event bus — 2026-08-08 (`app.on`/`emit`/`off`)
- [x] TimeSeriesGraph / Sparkline — 2026-08-08
- [x] LogViewer — 2026-08-08
- [x] Calendar / DatePicker / Clock — 2026-08-08 (`DatePicker` + `Clock`)
- [x] Atajos globales — 2026-08-08 (`app.bind`)
- [x] Drag & drop nativo — 2026-08-08

---

# Roadmap de robustez (crítica de uso real)

> Verificado 2026-08-12: los puntos anteriores están implementados en el código
> (`app.on`/`emit`/`off` en `iskg/app.py`, `DatePicker`/`Clock` en
> `iskg/widgets/_datetime.py`, `contextmenu` y `<<Drop>>` en `iskg/base.py`,
> `Widget.after` en `iskg/base.py:624`). Los siguientes puntos salen de construir
> una GUI real (ACE-Step) y son los friccionantes para casos no triviales y para
> que un agente de IA trabaje cómodo sin leer el fuente.

Estado de pendientes — **completado 2026-08-12**:

- [x] `Application.after` / scheduler — `iskg/app.py`
- [x] Reactividad: `Widget.rerender()` + update-JS para `ComboBox.values` e `IndicatorLED.color` — `iskg/base.py`, `iskg/widgets/*`
- [x] `ComboBox.values` actualizable en caliente — `iskg/widgets/_controls.py`
- [x] `IndicatorLED.color` actualizable en caliente — `iskg/widgets/_display.py`
- [x] Layout: `Frame(flex=False)` (sidebar fijo) + `PanedWindow` respeta `sash_pos` — `iskg/widgets/_containers.py`
- [x] `Application(icon=...)` oculta el acoplamiento a pywebview — `iskg/app.py`
- [x] Soporte `async`/`await` (`Application.run_async`) — `iskg/app.py`
- [x] Docs: type hints + docstrings en los widgets tocados; catálogo en `docs/api.rst`
- [x] Semántica de actualización documentada (ver nota abajo)

> **Nota de diseño sobre la reactividad:** el auto-render en `_sync` solo
> emite *update-JS* incremental cuando el widget lo implementa. Si una
> propiedad no tiene camino incremental (p. ej. una lista de opciones de un
> widget personalizado), el escape hatch es `widget.rerender()`, que
> reemplaza el DOM y re-engancha el JS de inicialización. No se auto-dispara
> desde `_sync` para no romper la deduplicación de JS idénticos ni los
> bindings de los hijos de los contenedores.
>
> **Reactivo en caliente (vía `_render_update_js`):** `IndicatorLED.color`,
> `IndicatorLED.active`, `IndicatorLED.size`, `IndicatorLED.label`,
> `ComboBox.values`, `ComboBox.current`. El resto de props de otros widgets
> requieren `rerender()` si no tienen update-JS.

## 1. `Application.after` / scheduler (`iskg/app.py`)

**Problema real:** para sondear un server cada N ms tuve que levantar un hilo
daemon (`threading.Thread` + `time.sleep`). `Widget.after` existe
(`iskg/base.py:624`) pero `Application` no lo expone, pese a ser el objeto que
vive durante toda la app.

**Objetivo:** polling/animaciones idiomáticos sin hilos manuales.

**Cambio propuesto:** añadir `Application.after(ms, cb)` y `Application.after_cancel(id)`
que deleguen en el timer del widget raíz (o un `_Timer` propio de la app). Devolver
un handle cancelable. El callback debe ejecutarse en el hilo de la app o vía
`self._defer_sync` para actualizar widgets de forma segura.

**Dónde:** `iskg/app.py` (`class Application`).

**Aceptación:** `app.after(1000, cb)` dispara `cb` una vez; tras `app.run()` los
widgets se actualizan sin excepciones; `after_cancel` detiene el timer.

**Tests:** `tests/` — timer único, cancelación, y que un callback que hace
`widget.config(...)` no rompa cuando `app._running`.

## 2. Reactividad total de widgets (`iskg/base.py`, `iskg/widgets/*`)

**Problema real:** `_sync()` (`iskg/base.py:800`) solo envía el JS parcial de
`_render_update_js()`; si un widget no implementa update-JS para una prop, el
cambio en caliente no se refleja y hay que recrear o usar `_config_dict` a mano.

**Objetivo:** cualquier `config()`/`prop = ...` se vea reflejado, o fallar claro.

**Cambio propuesto:**
- Añadir `Widget.rerender()` que reemplace el HTML completo del widget vía bridge.
- Hacer que `config()` y los setters llamen a `rerender()` cuando el widget no
  tenga update-JS para la prop cambiada (o siempre, si es barato).
- Documentar en docstring qué props son reactivas.

**Dónde:** `iskg/base.py` (`_sync`, `config`), y los widgets que hoy no actualizan.

**Aceptación:** tras `widget.config(color="red")` / `widget.value = x`, el DOM
cambia sin recrear el widget.

**Tests:** por widget afectado, test de que el update-JS o el re-render refleja
el cambio (usando `app.test_loop()` / `_TestWindow` ya existente).

## 3. `ComboBox.values` actualizable en caliente (`iskg/widgets/_controls.py`)

**Problema real:** el dropdown solo se renderiza en la creación. Cambiar
`values` en runtime (p. ej. tras consultar `/v1/models`) no actualiza la lista
porque `_render_update_js` solo toca el texto seleccionado, no los `<div>` items.

**Objetivo:** poblar el ComboBox después de arrancar la app.

**Cambio propuesto:** que `config(values=...)` / setter `values` dispare
re-render del dropdown (`rerender()` del punto 2), y que el índice `current` se
preserve si el valor sigue existiendo.

**Dónde:** `iskg/widgets/_controls.py` (`class ComboBox`).

**Aceptación:** `combo.config(values=["a","b","c"])` muestra las 3 opciones al abrir.

**Tests:** test de que tras `config(values=...)` el HTML contiene los nuevos items.

## 4. `IndicatorLED.color` actualizable en caliente (`iskg/widgets/_display.py`)

**Problema real:** `_render_update_js` solo cambia la clase `on/off`; el color
queda fijo del render inicial. Para un LED de estado verde/ámbar/rojo tuve que
crear 3 LEDs y togglear `visible`.

**Objetivo:** un solo LED cuyo color cambie en caliente.

**Cambio propuesto:** añadir update-JS que cambie `background`/`box-shadow` según
`color` (reusa el `col_map` de `_render`), o usar `rerender()`.

**Dónde:** `iskg/widgets/_display.py` (`class IndicatorLED`).

**Aceptación:** `led.color = "red"` cambia el color visible sin recrear.

**Tests:** test de que el update-JS contiene el color nuevo.

## 5. Layout: panel lateral fijo / `PanedWindow` respeta `sash_pos` (`iskg/widgets/_containers.py`)

**Problema real:** dos `Frame` en fila quedan 50/50 (`flex:1` por defecto). Para
un sidebar estrecho tuve que usar grid con pesos de columna. `PanedWindow`
existe pero ignora `sash_pos` inicial (ambos panes `flex:1`).

**Objetivo:** paneles laterales de ancho fijo y panedwindows con posición inicial.

**Cambio propuesto:**
- `PanedWindow._render` debe aplicar `_sash_pos` inicial a los `flex` de los panes.
- Añadir helper de "columna fija" (p. ej. `Frame(width=240, flex=False)` o un
  peso de grid `0` bien documentado) para sidebars sin recurrir a trucos.

**Dónde:** `iskg/widgets/_containers.py` (`Frame`, `PanedWindow`).

**Aceptación:** `PanedWindow(orient="horizontal", sash_pos=0.75)` arranca con el
panel derecho al 25%; un sidebar con ancho fijo no se estira.

**Tests:** test de que el HTML de los panes lleva el `flex` correcto según `sash_pos`.

## 6. `Application(icon=...)` oculta el acoplamiento a pywebview (`iskg/app.py`)

**Problema real:** el icono de la ventana nativa se pasa a `webview.start`, no a
`create_window`. Para poner `icon.ico` tuve que monkeypatchear `webview.start`.

**Objetivo:** API limpia y que no se fugue el detalle de pywebview al usuario.

**Cambio propuesto:** `Application(icon=...)` guarde la ruta y `run()` la inyecte
en `webview.start(icon=...)` (y documentar que el backend es pywebview).

**Dónde:** `iskg/app.py` (`__init__`, `run`).

**Aceptación:** `Application(icon="icon.ico")` muestra el icono sin monkeypatch.

**Tests:** test que `run` (con `webview` mockeado) llama a `start` con `icon=...`.

## 7. Soporte `async`/`await` para tareas largas (`iskg/app.py`, `iskg/base.py`)

**Problema real:** generar audio tarda; tuve que usar `threading.Thread` a mano y
sincronizar el resultado con la UI.

**Objetivo:** `app.run_async(coro)` o `widget.after` + `await` para no hilar a mano.

**Cambio propuesto:** helper que corra una corutina en un loop propio y permita
`await` de operaciones largas, actualizando widgets al finalizar. O al menos
documentar el patrón recomendado con `threading` + `app.after`.

**Dónde:** `iskg/app.py`.

**Aceptación:** un ejemplo `examples/async_task.py` que hace una tarea larga y
refresca la UI sin bloquear.

**Tests:** test de que una corutina larga no bloquea el `test_loop`.

## 8. Docs: catálogo de widgets, type hints, ejemplos (`docs/`, `examples/`)

**Problema real:** para saber la API tuve que leer el fuente (`_controls.py`,
`_display.py`, `base.py`). No hay catálogo ni ejemplos ejecutables por widget.

**Objetivo:** un agente de IA puede usar el proyecto leyendo docs, no código.

**Cambio propuesto:**
- `docs/api.rst` con todos los widgets y sus props/reactividad.
- `examples/widget_demo.py` ampliado o uno por widget, ejecutables.
- Type hints completos en widgets públicos.
- Sección "Qué es reactivo y qué solo inicial" (ver punto 9).

**Dónde:** `docs/`, `examples/`, docstrings en `iskg/widgets/*`.

**Aceptación:** un agente puede responder "¿cómo cambio el color de un LED en
caliente?" leyendo solo `docs/`.

## 9. Documentar semántica de actualización (reactivo vs inicial)

**Problema real:** no está documentado qué props se reflejan con `config()` y
cuáles solo en la creación. Eso obliga a leer `_render_update_js` de cada widget.

**Objetivo:** contrato explícito por widget.

**Cambio propuesto:** en la docstring de cada widget, lista de props reactivas
(marcar las que cambian en caliente) y notas de las que requieren `rerender()`.

**Dónde:** docstrings de `iskg/widgets/*` (complementa el punto 2).

**Aceptación:** la tabla de reactividad existe y es correcta frente al código.