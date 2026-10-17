# Changelog

## [0.4.17] — 2026-10-17

### Added
- **Propagación sistemática de mínimo de contenido**
  (`Widget._content_min_size()`): al redimensionar la ventana, los
  frames ya no se encogen por debajo de lo que contienen y dejan sus
  widgets tapados/recortados. Cada contenedor calcula su mínimo
  natural (hijos + gaps + padding + borde + cabecera) según su layout
  — pack suma el eje principal, grid combina tracks, place usa los
  bounds de los hijos — y lo emite como `min-width`/`min-height` en
  el elemento. Los hijos con `pack(expand=True)` también dejan de
  emitir los `min-*:0` ciegos.
- **Ventana con mínimo**: `Application()` pasa `min_size` a pywebview
  calculado del árbol raíz (ancho = raíz más ancha, alto = suma de
  raíces apiladas). `Application(min_size=False)` lo desactiva;
  `app.window_min_size` lo consulta.
- **Opt-out por widget**: `fit=False` mantiene el viejo
  comportamiento (shrink a cero) para ese contenedor. `width`,
  `height`, `min_width` y `min_height` explícitos siempre ganan
  sobre lo calculado.
- **`iskg.metrics`**: fuente única de medidas por defecto
  (botón 30px, entry 28px, estimador de ancho de texto mono
  `estimate_text_width`). `ScrolledFrame` no propaga su contenido
  (scrolla por diseño): solo cuenta su viewport explícito.
- `tests/test_content_min.py` (29 tests).

### Changed
- **Escala cómoda por defecto** (tema `ifaz` + métricas): botones
  30px de alto con fuente 12 (`sm` 24px/11, `lg` 36px/14, `tiny`
  18px/8); entries 28px de alto con fuente 12 y `box-sizing`.
  Antes: botón 26px/10, entry sin alto fijo.

### Tests
- 939 pasan, 2 skip. `ruff check` y `ruff format --check` limpios.

## [0.4.16] — 2026-10-17

### Fixed
- **`WidgetInspector` no inspeccionaba nada**: `enable()` llamaba a
  `app.inject_js()`, un método que **no existía** (`AttributeError` al
  activarlo), y su evento `pick` no tenía handler registrado — el click
  se tragaba en silencio y nunca se mostraban clase/id/config a pesar
  de lo que prometía el docstring. Ahora registra
  `_HANDLERS["iskg-inspector"]`, pinta un panel flotante con el dump
  completo del widget y emite el evento `widget-picked` (suscribible
  con `app.on("widget-picked", ...)`). Se puede llamar `enable()`
  antes de `run()` (el JS se encola, ver Added).
- **`Application.inject_js()` no existía**: `SystemTray`, el toast de
  los pickers (`_pickers.py`) y el inspector lo llamaban y reventaban
  con `AttributeError` en el primer uso — nunca detectado porque los
  tests headless no ejecutan esas rutas. Ahora es el counterpart de
  `inject_css()`; llamado antes de `run()` se encola y se ejecuta cuando
  el DOM da `loaded`.
- **`fps_meter()` devolvía siempre 0**: registraba su callback con
  `app.bind("__fps__", ...)`, que es un atajo de **teclado**, no un
  handler del puente — el evento `done` jamás llegaba y la función
  bloqueaba `duration_s` para devolver 0. Ahora registra en `_HANDLERS`
  y limpia el handler al terminar.

### Added
- **Bridge trace** (`Application.trace()` / `trace_clear()`): ring
  buffer siempre activo (500 entradas, payloads truncados) con todo el
  tráfico Python↔JS: `js-out`, `event-in`, `event-dropped`
  (debounce), `event-unhandled` (el clásico "mi click no hace nada") y
  `js-error`. `Application(debug=True)` además espejea cada entrada a
  stderr (`[ISKG:trace] ...`).
- **Dumps del árbol de widgets**: `Application.dump_tree()` (lista de
  dicts JSON), `Application.dump_tree_text()` (texto indentado),
  `Application.get_widget(id)` y `Widget.dump()` — el árbol completo
  con tipo, id, `destroyed` y config saneada (cadenas truncadas,
  listas acotadas, `repr()` para no-serializables).
- **`tests/test_debug_tools.py`**: 22 tests nuevos (trace, dumps,
  inspector, fps_meter, cola de `inject_js`).

### Tests
- 910 pasan, 2 skip. `ruff check` y `ruff format --check` limpios.

## [0.4.15] — 2026-10-16

### Fixed
- **`app.bind` con teclas globales reventaba en produccion**:
  `_handle_global_event` recibia el payload ya serializado (el bridge
  hace `JSON.stringify` y los listeners de teclado lo pre-serializan
  otra vez) y hacia `data.get(...)` sobre un `str` -> `AttributeError`
  en cada pulsacion. Ningun bind global (`<Control-s>`,
  `<KeyRelease-Enter>`, etc.) funcionaba fuera de los tests (que
  pasan dict). Ahora se desenvuelve la capa extra de JSON; string no
  valido devuelve `None` sin lanzar.

### Added
- **`Text` sincroniza al escribir**: `<textarea>` ahora tambien liga
  `oninput` (ademas de `onchange`, que solo dispara al perder el foco),
  igual que `Entry`. Sin esto, leer `text` justo tras escribir daba el
  valor viejo.

### Tests
- `test_global_shortcut_dispatch_json_string_payload` (payload str + basura).
- `test_render_js_binds_input_and_change` en `TestText`.

## [0.4.14] — 2026-10-16

### Added
- **`_JSAPI.pause_drag()`**: método nuevo expuesto como
  `pywebview.api.pause_drag()`. Pone `gui.move_progress = False` para que
  el easy_drag nativo no mueva la ventana mientras el usuario arrastra un
  grip de resize en HTML; el siguiente press lo re-arma, así que el grip
  solo lo llama una vez por pulsación. Devuelve `False` si no hay ventana
  o la ventana no usa easy_drag.

### Fixed
- **`LogViewer` nunca actualizaba en vivo**: `_render_update_js` emitía
  `if(!el)return;` a nivel superior. `evaluate_js` evalúa el payload como
  script, así que cada sync reventaba con `SyntaxError: Return statements
  are only valid inside functions` y las líneas nuevas no aparecían (el
  HTML inicial sí, porque `_render()` las incluye). Ahora el payload va
  envuelto en IIFE, igual que `_render_js` ya hacía.

### Tests
- `TestWindowFlags`: 3 tests nuevos de `pause_drag` (sin ventana, limpia
  `move_progress`, noop sin easy_drag). `test_features_2026`: regresión
  `test_logviewer_update_js_wrapped_in_iife`.

## [0.4.13] — 2026-10-16

### Added
- **`Application(on_top=..., frameless=..., easy_drag=..., x=..., y=...)`**:
  la ventana nativa ahora acepta always-on-top, sin bordes, easy-drag en
  modo frameless y posición inicial. Todo se pasa a `pywebview.create_window`
  (que ya lo soportaba; ISKG no lo exponía). Pensado para overlays (chat
  flotante, HUDs) donde la ventana debe quedar por encima del juego.
- **`Application.on_top(value)`**: getter/setter estilo `title()` que
  alterna always-on-top **en caliente** cuando la ventana está corriendo
  (setter vivo de pywebview).
- **`_JSAPI.resize(w, h)`**: método nuevo expuesto al JS como
  `pywebview.api.resize(w, h)`. Sirve para construir un grip de resize
  en HTML sobre una ventana frameless (GTK sin decoración no tiene
  tiradores de resize).

### Fixed
- **`geometry()` devuelve la posición real de la ventana**: antes guardaba
  `_x`/`_y` pero nunca se pasaban a `create_window` ni se leían del WM
  (feature muerta). Ahora la posición inicial se envía a pywebview y el
  getter, mientras la ventana corre, reporta la posición viva del window
  manager. Se suscribe también al evento `moved` para conservar el último
  valor tras el cierre.

### Tests
- Nueva clase `TestWindowFlags` (13 tests): defaults y flags custom de
  init, kwargs que llegan a `create_window` (x/y omitidos por defecto),
  get/set de `on_top` con y sin ventana, `geometry()` en vivo vs
  almacenada, `_track_window_move`, y `_JSAPI.resize` (noop sin ventana,
  enteros, basura rechazada). 838 passed, 2 skipped.

## [0.4.12] — 2026-10-13

### Added
- **`padx`/`pady` aceptan tuplas estilo tkinter** en `Widget.pack()`,
  `Widget.grid()` y `Box`: `pady=(0, 8)` = top 0 / bottom 8, `padx=(8, 4)`
  = left 8 / right 4. Antes el valor se interpolaba tal cual en el CSS
  (`padding-top:(0, 8)px`), declaración inválida que el navegador descarta
  en silencio — por eso los ejemplos que usaban tuplas perdían todo el
  espaciado vertical. Un `int` sigue significando "ambos lados" y `0`
  sigue sin emitir nada (para no pisar el padding de la clase CSS).

### Changed
- Nuevo alias de tipos público `iskg.PadValue = int | Sequence[int]` para
  anotar helpers propios de layout; acepta también listas y tuplas de un
  elemento.
- `Box.__init__(padx=..., pady=...)` y `Box.add(..., padx=..., pady=...)`
  usan el mismo tipo y heredan el comportamiento de tuplas.
- README: quick start vuelve a demostrar `pady=(0, 8)` (ahora válido),
  wheel enlazada a `v0.4.12`.

### Tests
- 869 tests pass (2 skipped): cobertura nueva de padding en tupla para
  `pack` y `grid` (simétrico, asimétrico con `0`, lista, tupla vacía),
  de `PadValue` en `Box`, y de la normalización de `_pad_pair`
  (incluye entradas malformadas).

## [0.4.11] — 2026-10-13

### Fixed
- **Ventana en blanco tras la actualización de Arch (2026-10-12)** —
  WebKitGTK 2.52 → 2.54 allocates textures through GBM/dmabuf; on drivers
  without working GBM buffers (NVIDIA proprietary) every allocation fails
  with `Failed to create GBM buffer ... Invalid argument` and the window
  opens completely blank. `iskg/app.py` now also forces
  `WEBKIT_DISABLE_DMABUF_RENDERER=1` (via `setdefault`, so an explicit
  user override still wins), next to the existing
  `WEBKIT_DISABLE_COMPOSITING_MODE=1`.
- **`Application(icon=...)` con una ruta inexistente bloqueaba la app** —
  pywebview's GTK backend calls `Gtk.Window.set_icon_from_file()` during
  window creation, so a bad path raised `GLib.GError` inside the GTK
  `activate` callback, the window was never created and `run()` hung
  forever. New `Application._resolve_icon()` validates the path before
  `webview.start()` and falls back to "no icon" with a warning on stderr.
- `examples/data_widgets_demo.py`: the `ListBox` `change` payload is
  `"index:text"`, so `int(idx)` raised `ValueError` on every selection; the
  callback now reads `listbox.selected_index`.
- `examples/async_task.py`: pointed at a non-existent `icon.ico` (which
  triggered the hang above); it now uses the image shipped next to the
  example and only passes it when it exists.

### Changed
- **`iskg themes` ahora lista los 16 temas reales** (los que acepta
  `app.set_theme(name)`, de `iskg.themes.THEMES`) más los assets CSS base;
  antes solo mostraba `ifaz.css` y escondía el resto.
- **README**: contador de widgets corregido (72 → **71**, con las 5
  familias reales y sin nombres inexistentes como `Toast`/`SystemTray`),
  bullet nuevo de los 16 temas, quick start sin tuplas `pady` (el padding
  en tupla todavía no está soportado y se emitía como CSS inválido),
  enlace de wheel a `v0.4.11` y nota de troubleshooting para la ventana
  en blanco.

### Tests
- 858 tests pass (2 skipped): new coverage for icon validation, the
  WebKit render-path environment variables, and a stronger
  `iskg themes` assertion (every registered theme must be listed).

## [0.4.10] — 2026-08-28

### Test portability
- `tests/test_cli.py::test_run_non_python` no longer relies on
  `/etc/hostname` (which does not exist on macOS). It now creates
  a temporary `.txt` file and asserts the CLI rejects the non-Python
  extension. 854 tests pass on Linux, macOS, and Windows.

## [0.4.9] — 2026-08-28

### Type-safety fixes
- **Pyright clean** across the entire package: 0 errors, 0 warnings.
- `iskg/app.py`: capture `then` in worker closure to avoid the
  ``"Object of type None cannot be called"`` warning; mark `gi`
  imports with `type: ignore[import-not-found]`.
- `iskg/cli.py`: `type: ignore[import-not-found]` on the optional
  `objc` / `Foundation` / `win32gui` imports used only to detect
  backends.
- `iskg/i18n.py`: access `GNUTranslations._catalog` via `getattr`
  with a typed fallback (the attribute is private but stable).
- `iskg/widgets/_calendar.py`: harden `date` / `time` / `datetime`
  property getters against `None`; fix the misplaced
  ``from ._datetime import TimePicker`` (TimePicker lives in
  this module).
- `iskg/widgets/_charts2.py`: reorder the `isinstance` check so
  tuple items are not fed to `float()` in the else branch.
- `iskg/widgets/_data.py`: rename `TreeView.remove(path)` to
  `remove_node(path)` to avoid overriding `Widget.remove(child)`;
  update the test; tighten `add_node`'s children coercion.
- `iskg/widgets/_extras.py`: add a `visible.setter` on `Modal` so
  the override matches the base class shape.

### Statistics
- 854 tests passing, 0 ruff errors, 0 pyright errors.

## [0.4.8] — 2026-08-28

### CLI and project packaging
- **New `iskg` console script** (PEP 621 `[project.scripts]`):
  `iskg --version`, `iskg info`, `iskg widgets`, `iskg themes`,
  `iskg run <script>`, `iskg check <script>`,
  `iskg new <name> [--template tool|dashboard|form|viewer]`,
  `iskg bundle <script> --standalone|--exe`.
- **Scaffolds** (`iskg/scaffolds/<name>/*.tmpl`):
  * `tool` — input form + log + action button (PBRMatGen-style).
  * `dashboard` — metric cards + progress + sparkline + time-series.
  * `form` — validated form with `Form` and 4 validators.
  * `viewer` — `FileBrowser` + `MarkdownViewer` two-pane viewer.
- **`iskg._platform`** — cross-platform helpers: `IS_WINDOWS` /
  `IS_MACOS` / `IS_LINUX` / `IS_BSD` / `IS_POSIX` constants, `OS_NAME`,
  `user_config_dir()` / `user_data_dir()` / `user_cache_dir()` (XDG on
  Linux, `~/Library/Application Support` on macOS, `%APPDATA%` on
  Windows), `native_line_ending()` for cross-platform text files.
- **`pyproject.toml`**: full PEP 621 metadata, PEP 639-compliant
  license expression, OS classifiers (Windows / macOS / Linux / BSD),
  `optional-dependencies = { dev, docs, bundle }`.
- **29 new tests** (`tests/test_cli.py`) for every CLI subcommand and
  the `_platform` module.

### Statistics
- **854 tests** passing (was 825, +29 new).
- **`pip install iskg` works** on any platform that has Python 3.10+.
- **`iskg` is a real console script** on `PATH` after install.

## [0.4.7] — 2026-08-27 (Phases E-I from comparative audit)

### Phase E (Polish)
- **Form validation** (`iskg.validation`): QValidator-style
  ``RequiredValidator``/``RangeValidator``/``LengthValidator``/
  ``PatternValidator``/``EmailValidator``/``URLValidator``/
  ``NumberValidator``/``CustomValidator`` + aggregator ``Form`` with
  per-field error rendering.
- **DataGrid cell types**: ``column_types`` list (``text``/``number``/
  ``bool``/``check``/``choice``/``date``), inline cell editing, focused
  cell outline, ``set_cell``/``get_cell``/``selected_col``/``editable``
  properties, ``command(row, col, value)`` callback.
- **I18n / L10n** (``iskg.i18n``): ``tr()``/``_()``, ``set_language()``,
  ``get_language()``, ``available_languages()``, ``use_language()`` ctx
  manager, ``Translator`` (loads JSON or ``.mo`` catalogues),
  ``format_number``/``format_date`` locale-aware helpers.
- **Theming**: 4 new themes (``high-contrast``, ``solarized``, ``sepia``).
  ``app.inject_css(css)`` for runtime CSS injection.
- **Pickers**: ``FontPicker`` (family + preview), ``DirectoryPicker``
  (path + Browse), ``ImagePicker`` (preview + Browse).
- **Display widgets**: ``Avatar``, ``Badge``, ``Spinner`` (animated),
  ``ProgressCircle``.
- **Charts**: ``BarChart``, ``PieChart``, ``ScatterPlot`` (with trend
  line), ``Heatmap`` (4 colormaps).
- **Utilities**: ``Carousel`` (autoplay + dots), ``SearchCtrl`` (composite
  with clear), ``Toast`` (non-modal notifications).

### Phase F (Advanced)
- **Calendar** widget (full month grid, navigation, day-of-week option).
- **TimePicker / DateTimePicker** (spinbox-style HH:MM:SS).
- **ToolBar** with ``add_action``/``add_separator``/``set_active``.
- **MdiArea / MdiSubWindow** (movable draggable subwindows,
  ``tile()``/``cascade()`` layouts).
- **SystemTray** (notification-area icon with menu and notify()).
- **UndoStack / UndoCommand / SetAttrCommand** (Qt-style undo/redo).
- **PropertyGrid** (object-attribute editor with type-driven editors).
- **CommandPalette** (VSCode-style Ctrl+Shift+P).

### Phase G (Tools / Debug)
- **Debug** (``iskg.debug``): ``qDebug``/``qInfo``/``qWarning``/
  ``qCritical`` print helpers and a ``Logger`` with level filtering and
  rolling history.
- **WidgetInspector** (click-to-inspect overlay, Alt+I toggle).
- **fps_meter** (frame-rate measurement).
- **enable_hot_reload** (CSS file watcher).

### Phase H (Graphics)
- **GraphicsView** (SVG canvas with hit-test items, ``add_item``
  rect/ellipse/text, click selection).

### Phase I (Long tail)
- **MarkdownViewer** + ``render_markdown()`` (headings, bold/italic,
  code, lists, links, blockquotes, hr).

### Statistics
- **72 widgets** (was 49 in 0.4.6).
- **825 tests** passing (was 770, +55 new).

## [0.4.7] — 2026-08-27

### Widgets
- **ColorPicker** — selector de color HSV/RGB/HEX con swatch, sliders y
  entrada de texto. Acepta `#rrggbb` y `rrggbb`. Property `color`.
- **FileBrowser** — árbol de directorios read-only con selección y
  comando. Métodos `refresh()`, property `root`, `selected_path`.
- **Modal** — diálogo overlay con backdrop, título, botón cerrar y eventos
  `on_close`. Métodos `show()`, `hide()` y property `visible`.
- **TabBar** — barra de tabs sin páginas (vs. Notebook). Métodos
  `add_tab()`, `remove_tab()`, property `current_tab`, `tab_count`.
- **RangeSlider** — slider de dos handles (low/high) con clamping
  automático. Property `range` como tupla.

### API consistency
- **`enabled` property** añadida a todos los widgets interactivos
  (Button, CheckBox, RadioButton, ToggleSwitch, Entry, ComboBox,
  Slider, SpinBox, ProgressBar, ListBox, DataGrid, TreeView, Knob).
- **`readonly` property** añadida a Entry y Text.
- **Reactive `from_`/`to`/`step`/`orient`/`show_value`** en Slider, SpinBox,
  Scale, Knob.
- **Reactive `min_value`/`max_value`** alias en SpinBox.
- **Reactive `selected_index`** en ListBox, **`selected_row`** en
  DataGrid, **`selected_path`** en TreeView.
- **`ComboBox.value` writable** — ahora `cb.value = "foo"` selecciona
  el item por string.
- **`ListBox`, `DataGrid`, `TreeView`** con API runtime completa:
  `add`/`append`/`insert`/`delete`/`clear`/`remove`/`append_row`/
  `remove_row`/`add_node`. Para TreeView, `add(string_or_dict, parent_path=...)`
  soporta el formato `node/child/grandchild`.
- **Notebook runtime**: `remove_tab()`, `set_active()`,
  `current_tab` property, `tab_count`.
- **PanedWindow.sash_pos como property** (antes era método).
- **Frame.text como property** reactivo.
- **ImageBox.fit validado** contra
  `{"contain", "cover", "fill", "none", "scale-down"}`.
- **DatePicker.date_format** como property pública limpia
  (almacenada como `date_format`, alias interno `format` para
  retrocompatibilidad).
- **IconLabel.icon/icon_size, ProgressBar.max_/show_text, Knob.from_/to/color**,
  **Clock.seconds/military** ahora son properties reactivas.
- **IndicatorLED, LEDDisplay, RadialGauge, StatusBar** con properties
  para `color`, `label`, `size`, `digits`, `units`, `sections`.

### Bug fixes
- **LogViewer** (from 0.4.6) — re-render por timestamp.
- **`_handle_bridge_event` en Button ya no duplica el command** (la
  base class lo invoca automáticamente).
- **ListBox preserva selección** al refrescar items
  (`_render_update_js` ahora emite el `selected` class).
- **ListBox.command** ahora pasa `idx:text` (no solo idx) para que el
  callback reciba el texto seleccionado.
- **Scale._render_update_js** ahora actualiza también las labels
  min/max cuando cambia el rango.
- **Clock.stop()/start()** — el interval se puede cancelar y reiniciar;
  `destroy()` lo limpia automáticamente.
- **Knob.destroy()** — limpia `window._iskg_knobHandlers[id]` y
  `window.iskg_knob_{id}` para evitar memory leaks.
- **StatusBar.text setter** no muta in-place la lista de sections
  (sin side-effects para callers que retienen referencias).
- **ComboBox editable** ahora implementa filtrado en tiempo real
  (autocomplete) y selección por Enter.
- **TreeView.add** ahora detecta si el argumento es un nodo (dict/str)
  o un Widget, llamando a `add_node` o al `Widget.add` original
  respectivamente.
- **API posicional `("text")`** ahora soportado en CheckBox,
  RadioButton, ToggleSwitch, Text, RichText, IconLabel, Frame (todos
  con `_FIRST_POSITIONAL_AS_TEXT = True`).

### Statistics
- **51 widgets** exportados (era 47).
- **770 tests passing**, 2 skipped, 0 failing.

## [0.4.6] — 2026-08-27

### Fixed
- **LogViewer re-renders every append when `show_timestamp=True`**: a
  `datetime.now()` call inside `_line_html()` produced a fresh ISO string
  on every render, defeating the per-widget `_last_sync_js` dedup and
  flooding the webview with hundreds of `innerHTML` updates per second
  (visible as audio feedback in some webkit2gtk setups). The timestamp
  is now frozen at `append()` time and stored alongside each line, so
  the rendered HTML is stable across no-op syncs.
- **`_render_style_update_js` re-emitted the same CSS on every sync**:
  the style cache started as an empty string, so the first sync always
  emitted `iskg_set_style` bytes that were already in the initial HTML,
  which broke the `_last_sync_js` dedup on the second sync. The cache
  is now primed once in `Application.add()` (`_prime_style_cache`),
  mirroring how the widget's initial render is already in the DOM.
- **`_JSAPI` debounce silently dropped user actions** (clicks, keypresses,
  changes, submits, etc.) when the same event fired twice within 50 ms,
  which is exactly what happens during a double-click. Events are now
  classified; UI events bypass the debounce and only high-frequency
  events (mousemove, scroll, resize) are debounced by payload.
- **`_flush_sync` joined every queued JS statement with `;` and emitted
  one giant `evaluate_js`**: a busy `LogViewer` could push several MB
  into a single call and stall the JS thread. Statements are now
  chunked at 64 KB.
- **`_eval_js` swallowed all `evaluate_js` exceptions** unless
  `debug=True`. The exception is now always printed to stderr; debug
  mode adds a full traceback.
- **`_run_gtk_modal` silently ran dialogs on the worker thread** when
  GLib wasn't importable, deadlocking WebKit. The fallback path now
  raises a `RuntimeError` with a clear remediation message.

### Changed
- **`HBox` / `VBox` are now proper subclasses of `Box`** instead of
  factory functions, so `isinstance(w, HBox)` works and
  `widget.__class__.__name__ == "HBox"` is reliable.
- **First-positional-string constructors**: `Label("text")`,
  `Button("text")`, and `Entry("text")` now work the way every other
  toolkit does (tkinter, Qt, wx). Subclasses opt in via the class flag
  `_FIRST_POSITIONAL_AS_TEXT = True` and call the
  `_swap_first_positional_str()` helper from their `__init__`.
- **`Application.after` uses a single daemon worker thread + priority
  queue** instead of one `threading.Timer` per callback, so concurrent
  timer callbacks can no longer race on `_deferred_sync` or widget
  state. `Widget.after` now delegates to `Application.after` when the
  widget is attached to an app, and falls back to a one-shot timer
  otherwise.
- **`_Timer.cancel()` is safe to call on a handle whose backing timer
  was already None** (e.g. timers created by the new app-level worker).


### Changed
- **`docs/conf.py` deriva `release` de `iskg._version.VERSION`** (antes se
  mantenía a mano y se desincronizaba; ver 0.4.2/0.4.3/0.4.4).
- **API `command`**: el callback recibe el payload del evento cuando acepta 1
  argumento (`command=lambda idx: ...`, `command=lambda files: ...`) y se llama
  sin args si no lo acepta (`command=lambda: ...`). El despacho ya no usa
  `inspect.signature`; hace fallback try/except (mismo comportamiento, más
  simple y sin inspección).
- **`theme.py`**: el CSS base deja de ser un string de ~1000 líneas y pasa a
  `iskg/themes/ifaz.css` (cargado con `importlib.resources`). Mismo render; el
  CSS ahora es editable como tal.

### Added
- **Aviso de typos en kwargs de widgets**: `__init__`/`config()` emiten
  `UserWarning` cuando una clave desconocida es muy parecida a una propiedad
  conocida (p. ej. `textt` → `text`, `widht` → `width`). No avisa para CSS
  arbitrario ni para custom properties (`--x`).
- **CI (`ci.yml`)**: job `examples` importa los módulos de `examples/`.
- **Tests (`tests/test_examples_render.py`)**: renderizan `build_app()` de cada
  ejemplo y verifican que el HTML contiene los ids de todos los widgets.

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
