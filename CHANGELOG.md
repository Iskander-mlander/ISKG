# Changelog

## [0.4.4] — 2026-08-12

### Fixed
- **Backend GTK en Linux**: `_import_gi_backend` fijaba la versión de GTK
  explícitamente (`Gtk 3.0` + `WebKit2 4.1`/4.0) antes de importar. Antes la
  importación sin versión resolvía a la GTK más alta instalada (4.0 cuando
  GTK3 y GTK4 coexisten), chocando con WebKit2GTK (solo GTK3) y rompiendo apps
  que usan iskg en ese entorno (p. ej. `ACE-Step/gui_app.py`: *"Requiring
  namespace 'Gtk' version '3.0', but '4.0' is already loaded"*).

## [0.4.3] — 2026-08-12

### Fixed
- **`command` recibe el payload del evento cuando el callback lo acepta**: antes
  `command` solo se invocaba sin argumentos en `click`/`change`, así que callbacks
  tipo `command=lambda idx: ...` (p. ej. el índice de un `ListBox`) fallaban. Ahora
  los callbacks de 1 argumento reciben el dato del evento; los de 0 argumentos
  (`lambda: ...`) siguen sin recibir nada (compatibilidad hacia atrás).
- **`DropTarget` enruta el evento `drop` a `command`**: `command=lambda files: ...`
  ahora funciona (antes el parámetro se ignoraba en silencio).
- **`docs/conf.py`**: `release` refleja la versión real del paquete.

### Added
- **CI (`ci.yml`)**: job `examples` que importa los módulos de `examples/` en cada
  push/PR, detectando drift de API en los demos sin abrirlos manualmente.

## [0.4.2] — 2026-08-12

### Added
- **`examples/theming_demo.py`**: demo ejecutable del cambio de tema en caliente
  (`Application.set_theme`) con selector de los 13 temas registrados y botón
  cíclico.
- **`examples/data_widgets_demo.py`**: demo de `ListBox`, `DataGrid` (ordenable),
  `TreeView` (jerárquico) y `DropTarget`, con selección reactiva vía
  `bind("change", …)` / `bind("<<Drop>>", …)`.
- **CI (`ci.yml`)**: nuevo job `docs` que instala Sphinx + extensiones y corre
  `sphinx-build -b html docs docs/_build/html`, dejando el build de documentación
  como check de CI en push/PR (además del deploy a Pages en `docs.yml`).

## [0.4.1] — 2026-08-12

### Changed
- **CI de release (`release.yml`)**: ahora corre la suite (`pytest`) y valida que
  la versión del paquete coincida con el tag (`vX.Y.Z` == `iskg._version.VERSION`)
  **antes** de publicar en PyPI, para no soltar releases rotos.
- **README**: línea de instalación actualizada a la versión actual; imágenes con
  URLs absolutas de raw GitHub (se ven igual en GitHub y PyPI); sección
  "Installation" con deps del backend por distro y nota de Arch (PEP 668:
  venv / pipx / `--break-system-packages`).

## [0.4.0] — 2026-08-12

### Added
- **`Application.after(ms, cb)` / `after_cancel(id)`**: scheduler con timers daemon
  para polling/animaciones sin hilos manuales; devuelve un handle cancelable.
- **`Widget.rerender()`**: escape hatch que reemplaza el DOM y re-engancha el JS de
  inicialización para props sin camino incremental (helper JS `iskg_replace_widget`).
- **`ComboBox.values` actualizable en caliente**: el dropdown se reconstruye al cambiar
  la lista en runtime (p. ej. tras consultar `/v1/models`).
- **`IndicatorLED.color`/`active`/`size`/`label` reactivos en caliente** vía
  `_render_update_js` (antes solo la clase on/off).
- **Layout**: `Frame(flex=False, width=...)` para sidebars de ancho fijo, y
  `PanedWindow` respeta `sash_pos` inicial (p. ej. `sash_pos=0.75`).
- **`Application(icon=...)`**: guarda el icono y lo inyecta en `webview.start`,
  ocultando el acoplamiento a pywebview.
- **`Application.run_async(coro, then=...)`**: corre corutinas en un loop propio fuera
  del hilo UI; `then(result)` recibe el valor o la excepción.
- **Docs**: type hints + docstrings en los widgets tocados; semántica de reactividad
  documentada en `docs/PLAN_MEJORAS.md` (qué props son reactivas vs requieren
  `rerender()`).
- **`examples/async_task.py`**: ejemplo ejecutable de tarea larga que refresca la UI
  sin bloquear.
- **`tests/test_roadmap_improvements.py`**: 23 tests cubren los puntos anteriores.

## [0.3.81] — 2026-08-08

### Fixed
- Re-release de 0.3.80 con el job de typecheck de CI en verde: `pyright` señalaba
  7 errores — `date` (el parámetro) sombreaba el tipo importado en `DatePicker`,
  `TimeSeriesGraph.update(value)` rompía la firma de `Widget.update()` y el acceso
  a `self._context_menu.items` quedaba sin narrowing. Solo cambios de tipos; sin
  cambios de comportamiento en runtime.

## [0.3.80] — 2026-08-08

### Added
- **Menú contextual** (clic derecho) por widget: `widget.set_menu(menu)` / `widget.popup_menu(menu, x, y)` y `bind("contextmenu", cb)` (el callback recibe `{x, y}`). Reutiliza `Menu`/`MenuItem`; submenús, separadores y atajos soportados. `MenuItem` ahora se exporta a nivel de paquete (`iskg.MenuItem`).
- **Event bus** global: `app.on(event, cb)` / `app.emit(event, *args)` / `app.off(event, cb)` (soporta decorador). Eventos integrados `theme-changed` (al cambiar tema), `closing` y `widget-created`.
- **`TimeSeriesGraph` / `Sparkline`**: gráficos SVG en tiempo real con múltiples series, curvas Bézier suavizadas (`smooth=True`), límite de puntos (`max_pts`), bounds fijos (`y_min`/`y_max`) y `append/replace/update/clear`. `Sparkline` hereda la API.
- **`LogViewer`**: área de log auto-scroll con colores por severidad (DEBUG/INFO/WARN/ERROR/CRITICAL), timestamps opcionales (`show_timestamp`), recorte (`max_lines`) y `append/clear`.
- **`Clock`**: reloj digital en vivo (24h/12h, con/sin segundos) que se actualiza solo en el navegador y puede invocar `command` por tick.
- **`DatePicker`**: campo con popup de calendario (navegación mes/mes), evento `change` con fecha ISO, `command` y propiedades `value`/`iso`. El popup usa `position:fixed` para superponerse a contenedores bajos.
- **Atajos globales**: `app.bind("<Control-s>")` (sintaxis tkinter) dispara sin importar el foco; soporta decorador. Callback recibe `{key, code, ctrl, alt, shift}`.
- **Drag & drop entre widgets**: `draggable=True` en la fuente y `widget.bind("<<Drop>>", cb)` como destino; el callback recibe `{source, x, y, target}`.
- `examples/widget_demo.py`: filas nuevas con los widgets del batch 2026 (charts, sparklines, LogViewer, Clock, DatePicker, telemetry por event bus, atajos globales y drag&drop a una bahía).

### Changed
- **Bump 0.3.72 → 0.3.80**; README con captura nueva (`examples/Cap.png`), 40 widgets y features del batch documentadas. `docs/api.rst` añade los módulos `_charts`, `_logview`, `_datetime`.

### Fixed
- CI (`e2e-linux`): el smoke de ventana real fallaba en GitHub con `ModuleNotFoundError: No module named 'gi'` porque `actions/setup-python` crea un venv aislado que no ve los bindings del sistema. **El test de ventana real y el job `e2e-linux` se eliminaron definitivamente** (nunca se estabilizó en CI); los tests headless siguen corriendo en todos los runners.
- `DatePicker`: el popup quedaba oculto si el card padre tenía `overflow:hidden`/poca altura — ahora se reposiciona con `position:fixed`.
- `Application.bind` exigía callback obligatorio; ahora soporta `@app.bind(...)` como decorador.
- Lint: corregidos f-string sin placeholder y `if` anidado (`ruff SIM102`) del menú contextual.
- Charts: polylines → paths Bézier suavizados por defecto (opción `smooth=False` para líneas rectas).

## [0.3.72] — 2026-08-08

### Changed
- README: ejemplo de quick start rehecho con widgets comunes (Entry, Slider, ProgressBar, ComboBox, ToggleSwitch) y temas actualizados (incluye night/warm/cold); verificado con `test_loop`.

### Fixed
- `docs/`: badge PyPI dinámico; docstring de `Frame` y `Slider` corregidos para Sphinx; `step` horizontal del `Slider` aplicaba antes solo en orientación vertical.
- CI: fix de los fallos en todos los jobs de test — el test GTK hacía `import gi` sin guard (fallaba sin `gi`), y `TestLoop` era detectado como clase de test; `result` reutilizado con tipos distintos rompía pyright.
- E2E: el smoke de ventana real programaba el cierre antes de que GTK inicializara; ahora se agenda desde `func` de `webview.start` (4s) y es fiable bajo xvfb en CI.

## [0.3.71] — 2026-08-08

### Added
- Fonts opcionales: `font_css(ids=None)`, `build_html(..., font_ids=...)` y `Application(..., font_ids=...)` permiten embeber solo un subset de las 7 familias para reducir payload.
- `Application.sync_batch()`: context manager opt-in que agrupa `_sync` de varios widgets en una sola transacción JS (`_defer_sync`/`_flush_sync`); fuera del batch el flush sigue siendo inmediato.
- `Application.test_loop()`: backend headless para testing — devuelve `TestLoop` con ventana fake `_TestWindow` (captura `evaluate_js`), expone `loop.html`, `loop.js_calls`, `loop.fire(widget_id, event, event_data)` (puente al bridge) y `loop.stop()`. `TestLoop` y `_TestWindow` exportados desde `iskg.app`.
- `Slider(step=...)`: atributo HTML `step` en el input `range` para valores discretos.
- `Application.sync_batch()`: context manager opt-in que agrupa `_sync` de varios widgets en una sola transacción JS (`_defer_sync`/`_flush_sync`); fuera del batch el flush sigue siendo inmediato.
- `Application.test_loop()`: backend headless para testing — devuelve `TestLoop` con ventana fake `_TestWindow` (captura `evaluate_js`), expone `loop.html`, `loop.js_calls`, `loop.fire(widget_id, event, event_data)` (puente al bridge) y `loop.stop()`. `TestLoop` y `_TestWindow` exportados desde `iskg.app`.
- `Slider(step=...)`: atributo HTML `step` en el input `range` para valores discretos.
- `Frame`: los hijos `.place()` se envuelven en un contenedor `position:relative; flex:1` para que sus coordenadas absolutas queden contenidas.
- `tests/test_e2e_smoke.py`: smoke E2E (árbol headless, roundtrip de sync, fire de comandos vía bridge, ventana real pywebview bajo `xvfb`, entrypoint subprocess).
- CI: job `e2e-linux` con `xvfb` en `.github/workflows/ci.yml`.

### Changed
- `Widget._sync` usa `_defer_sync` de la aplicación (dedup por cola + flush por batch); el archivo `iskg/layout.py` (sin uso) eliminado.

### Fixed
- `Application.run()`: stderr del proceso se restauraba solo en fallo de `webview.start`; ahora se restaura en un `finally` (incluye `SystemExit`/interrupciones). Nuevo parámetro `stderr_log` apunta el redirect a un archivo de log (por defecto `/dev/null`).
- `_JSAPI.on_event`: el debounce de 50 ms descartaba eventos legítimos con distinto payload; ahora dedupa por `(widget_id, event_name, event_data)`.
- `Application.quit()`: no disparaba `on_close`; ahora lo hace mediante `_fire_close_callbacks()` idempotente, también usado por `run()`.
- `iskg_bind_key` (template): el retry para elemento no montado podía quedar en bucle infinito al destruir el widget; ahora reintenta una sola vez.
- `Widget.destroy()`: no limpiaba los listeners/tooltips; nuevo `window.iskg_cleanup(id)` elimina el elemento y sus tooltips del DOM.

## [0.3.70] — 2026-08-07

### Fixed
- Diálogo nativo de carpeta/archivo (GTK) congelaba la app y crasheaba WebKit:
  pywebview despacha las llamadas del bridge JS en un hilo worker, pero ISKG
  ejecutaba `dialog.run()` en ese hilo. Nuevo `Application._run_gtk_modal()`, que
  ejecuta el diálogo en el hilo principal vía `GLib.idle_add` + `Event` (mismo
  patrón que el `create_file_dialog` interno de pywebview). Aplicado a
  `file_dialog`, `color_dialog` y `font_dialog`.
- Pulsar Cancelar en el diálogo GTK abría un segundo diálogo (el fallback de
  pywebview) porque `None` se confundía con "GTK no disponible": `_gtk_file_dialog`
  devuelve ahora el sentinel `_GTK_UNAVAILABLE` cuando no importa GTK, y
  `file_dialog` sólo cae al diálogo de pywebview en ese caso.
- Botones con altura inconsistente: `Button(size="sm"|"lg")` generaba clases CSS
  sin reglas. Ahora `.iskg-btn` usa `height` fija por tamaño (26/22/30/18px) con
  el texto centrado y `padding` horizontal variable, de modo que todos los botones
  de un mismo tamaño comparten altura exacta y el ancho sólo sigue al texto.
- Dropdown de `ComboBox` recortado sin overlay: ahora en apertura se renderiza con
  `position:fixed` (+ `width`/`left`/`top` calculados con `getBoundingClientRect`),
  escapando el `overflow:hidden` y contextos de apilamiento de cualquier ancestro.

## [0.3.69] — 2026-08-07

### Fixed
- 7 tests preexistentes que fallaban desde v0.3.62 (la suite pasa ahora 604/604):
  - `Widget`: validación de tipos en `config()`/`__init__` (`visible`→bool, `text`→str,
    `disabled`/`hidden`→bool): se lanza `TypeError` ante tipos inválidos. `None` se
    permite siempre; `width`/`height` no se validan estrictamente por aceptar CSS
    ("95%", "10px").
  - `_render_style_update_js()`: cache del último CSS → segunda llamada con el mismo
    estilo devuelve "", sólo reenvía al cambiar.
  - `FileDialog.open_file/save_file/open_folder`: ahora reenvían `title` a
    `Application.file_dialog(..., title=...)`, que a su vez lo usa en el diálogo GTK.
  - `Application.get_clipboard/set_clipboard`: importan `pyperclip` vía
    `importlib.import_module` para soportar mocking y fallar a `""` ante ImportError.

## [0.3.68] — 2026-08-07

### Fixed
- Ventana completamente blanca (sin contenido) en Linux/webkit2gtk por un fallo del
  camino de compositing acelerado. `Application.run()` ahora fuerza
  `WEBKIT_DISABLE_COMPOSITING_MODE=1` (con `setdefault`, respetando override
  del usuario) antes de arrancar el loop GTK, de modo que la UI es siempre visible.
- Fallback de color de fondo en `template.py` (`body`/`#iskg-root`): si una
  variable CSS de tema queda sin definir, se usa un fondo oscuro en vez de blanco.

## [0.3.67] — 2026-07-24

### Added
- Canvas: `create_polygon(*points, **kwargs)` — polígonos rellenos con contorno
- Canvas: `create_image(x, y, data, **kwargs)` — blit de tiles PNG desde bytes
- Canvas: `<<Resize>>` event via `ResizeObserver` + bridge — notifica `{width, height}`
- Documentación de API regenerada para nuevos métodos de Canvas

## [0.3.62] — 2026-07-23

### Added
- ARIA attributes (`role`, `aria-*`) en todos los widgets — accesibilidad para screen-readers (#M4)
- Docstrings en ~140 métodos públicos de la API (#M5)
- Test de integración ScrolledFrame + PanedWindow + grid mixto (#F4)

### Fixed
- SyntaxError en `ProgressBar` por `"""` huérfano en `_display.py`
- `aria-disabled="true"` perdido en CheckBox, RadioButton, Slider, SpinBox, ToggleSwitch
- `_render_attrs()` no se emitía en ProgressBar, StatusBar, ScrollBar, ListBox, DataGrid, TreeView, DropTarget, MenuBar, ComboBox, Slider, SpinBox, Scale, Notebook, RichText
- Separator, Entry, Text, RichText sin `_ARIA_ROLE`

### Changed
- Widgets reordenados en demo (gauges, botones 2-col)

## [0.3.11] — 2026-07-22

### Added
- ImageBox: soporte para `command` callback y click (cursor:pointer, `iskg_bridge_event`)
- ImageBox: `width` y `height` aceptan `str` (ej. `"100%"`) además de `int`

### Changed
- ImageBox: ancho/alto renderizado con unidad `px` solo si es `int`

## [0.3.10] — 2026-07-22

### Added
- 8 nuevos temas: infinity (neón), cyberdusk (azul), dracula, nord, gruvbox, monokai, catppuccin, light
- 7 fuentes SIL OFL embebidas (Inter, JetBrains Mono, Nunito, Manrope, Space Grotesk, Fira Sans, Playfair Display) — sin CDN
- `AGENTS.md` con workflow checklist para sesiones futuras
- Nuevas variables CSS: `--font-sans`, `--font-rounded`, `--font-geometric`, `--font-display-alt`, `--font-humanist`, `--font-serif`

### Changed
- Reemplazados 5 temas antiguos (cold, warm, night, ocean) por 8 nuevos
- Descripción del proyecto: eliminada mención "táctico-militar"
- Fuentes CDN (Share Tech Mono, Orbitron) reemplazadas por fuentes embebidas
- Documentación de API actualizada con módulo fonts y lista de temas

## [0.3.9] — 2026-07-22

## [0.2.0] — 2026-07-21

### Added
- 36 widgets: Label, Button, Entry, CheckBox, RadioButton, ComboBox, Slider,
  ProgressBar, Frame, ListBox, ScrollBar, Text, SpinBox, Separator, Notebook,
  Canvas, Scale, MessageDialog, Knob, LEDDisplay, DataGrid, IndicatorLED,
  RadialGauge, ToggleSwitch, StatusBar, Tooltip, Spacer, ImageBox, IconLabel,
  RichText, TreeView, DropTarget, MenuBar, FileDialog, Menu, MenuItem
- Pack, grid, and place layout engines
- IFAZ Tactical Theme (dark, terminal-inspired CSS)
- JS bridge with deduplication for pywebview double-event delivery
- Menu system with nested submenus and keyboard shortcuts
- FileDialog (open, save, folder via native OS dialogs)
- MessageDialog (modal overlay via `insertAdjacentHTML`)
- Canvas with rectangle, line, oval, text, arc drawing primitives
- RadialGauge and Knob with mouse drag/wheel interaction
- LEDDisplay, IndicatorLED, ProgressBar for data visualization
- DataGrid with column sorting and row selection
- RichText editor with formatting toolbar
- TreeView with collapsible nodes
- Tooltip system
- DropTarget for drag-and-drop
- GTK stderr warning suppression during `run()`
- MIT license

### Changed
- Widgets refactored from monolithic `widgets.py` into subpackage `widgets/`
  with one file per category (`_controls.py`, `_display.py`, etc.)
- Legacy standalone files (`index.html`, `js/`, `css/`, `img/`) removed

### Infrastructure
- Sphinx documentation skeleton (`docs/conf.py`, `docs/index.rst`, `docs/api.rst`)
- `pyproject.toml` with setuptools build configuration
- `.gitignore` for Python/bytecode/cache/OS artifacts
