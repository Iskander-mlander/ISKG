# Auditoría y plan de mejora de ISKG

> Fecha: 2026-08-08
> v0.3.70 — 581 tests pasan, ruff limpio (tras corregir 2 SIM105 en `app.py`).
> ~9.081 líneas Python: `base.py` 987, `theme.py` 948, `_controls.py` 893,
> `app.py` 603, widgets 1.908.

Documento de diagnóstico con los hallazgos de la revisión del toolkit, ordenados
por impacto para la integración R3 (launcher GUI). Cada ítem indica archivo/línea,
problema, impacto y propuesta de reparación.

---

## 1. `app.run()` redirige stderr global a `/dev/null` (PRIORIDAD ALTA para R3)

**Ubicación:** `iskg/app.py:187-190` (redirect) y `192-209` (restore).

```python
self._saved_stderr = os.dup(2)
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, 2)
os.close(devnull)
```

La idea original era silenciar las advertencias de GTK/WebKit, pero es **global y
total**: cualquier `print`/`logging` del proceso que no haya retenido el fd original
se pierde durante todo `webview.start()` (incluyendo los de la app, backend, etc.).
Un crash de Python, un traceback de webview o nuestros propios prints no se ven.

**Propuesta:**
- Opción B: dejar el redirect global pero hacer *tee* a un archivo de log
  (`~/.local/share/*/iskg-stderr.log`) además de restaurarlo en un `finally`.
- El `except Exception` de la línea 194 ya restaura stderr y printea el error, así que
  el fallo de `webview.start()` sí llega; el problema es todo lo demás durante el loop.
- Falta un `finally` que restaure stderr si la app se cierra por otra vía
  (`KeyboardInterrupt`/`SystemExit` en la línea 193 no pasa por la restauración).

**Estado:** ✓ CORREGIDO — stderr se restaura en un `finally` garantizado; nuevo param
`Application(stderr_log=...)` permite guardar el stream en un archivo (por defecto
sigue siendo `/dev/null`). Tests `TestRunStderr` (restauración del fd y captura al log).

---

## 2. `_JSAPI.on_event` — debounce de 50 ms descarta eventos legítimos (PRIORIDAD ALTA)

**Ubicación:** `iskg/app.py:30-53`

```python
class _JSAPI:
    _DEBOUNCE_MS = 50
    _last_event: dict[tuple[str, str], float] = {}

    def on_event(self, widget_id, event_name, event_data_json=None):
        key = (widget_id, event_name)
        ...
        if (now - last) * 1000 < self._DEBOUNCE_MS:
            return  # descarta
```

Este debounce (añadido para corregir el duplicado de eventos del pipeline de R3,
documentado como P2 en `ACTUAL.md`) descarta **cualquier** segundo evento del mismo
`(widget, event)` en una ventana de 50ms, **ignorando el `event_data`**. Consecuencias:

- Progresos/actualizaciones del pipeline a alta cadencia (varios logs) se pierden.
- Un doble click rápido en un `Button` lanza un único `click`.
- Cambios rápidos en `Slider`/`Scale` se pierden eventos legítimos.

**Propuesta:** debounce por `(widget, event, event_data)`, o limitar el debounce a
`change`/`click` y eliminar el dedup global corrigiendo el emisor JS (el bug real
estaba ahí, no en el bridge). R3 ya llama `commit=True` en el checker para protegerse.

**Estado:** ✓ CORREGIDO — el debounce ahora dedupa solo eventos del mismo
`(widget, event)` **con el mismo `event_data`**; eventos con datos distintos en la
ventana de 50ms ya pasan. Tests: `test_debounce_allows_different_data_within_window`
y `test_debounce_drops_same_event_same_data`.

---

## 3. `setTimeout` en `iskg_bind_key` se reejecuta tras `destroy()` (PRIORIDAD ALTA)

**Ubicación:** `iskg/template.py:91-93`

```js
window.iskg_bind_key = function(id, eventType, keyFilter, mods) {
    var el = document.getElementById(id);
    if (!el) { setTimeout(function(){iskg_bind_key(id,eventType,keyFilter,mods);},50); return; }
```

Si el widget se destruye entre el bind y el `setTimeout`, el retry se queda en bucle
infinito (el elemento nunca existirá) o atacha un handler a un id reciclado.
Igual en `_render_tooltip_js` (`base.py:362-380`): no hay cleanup al destruir.

**Propuesta:**
- Máximo 1 retry para `iskg_bind_key` (o guardar el timer y cancelarlo en `destroy`).
- `destroy()` (`base.py:784`) debe desatar todos los handlers JS de key/tooltip del widget.
- Tooltips: limpiar el `setTimeout`/`setInterval` al destruir el widget.

**Estado:** ✓ CORREGIDO — `iskg_bind_key` reintenta 1 sola vez con un marcador interno;
nuevo `window.iskg_cleanup(id)` en el bridge que desata listeners y elimina el elemento
+ tooltips (`data-tipfor`); `Widget.destroy()` emite `iskg_cleanup` cuando hay app
corriendo. Tests: `TestBridgeJS`, `test_widget_destroy_calls_cleanup_js`,
`test_tooltip_js_marks_data_tipfor`.

---

## 4. `fonts.py` — 2.339 líneas de base64 embebidas (PRIORIDAD MEDIA-ALTA)

**Ubicación:** `iskg/fonts.py`

- Inter, JetBrains Mono, Nunito, Manrope, Space Grotesk, Fira Sans, Playfair.
- `font_css()` reconstruye todas las reglas `@font-face` **cada vez** que se genera el
  HTML (`template.build_html`, incluido en línea 204), y el payload base64 viaja en el
  arranque sin importar si la app usa o no fuentes personalizadas.

**Propuesta (para R3 y el toolkit):**
- Por defecto no incluir las 7 familias; exponer `font_css(families=...)` con un set
  mínimo (p. ej. sans + mono) y `register_font(family, b64)` para añadir bajo demanda.
- Fallback CSS: usar stack del sistema (`system-ui, sans-serif`) por defecto y sólo
  declarar `@font-face` si la fuente se usa realmente en `_CONFIG_TO_CSS`.

**Estado:** ✓ CORREGIDO — `font_css(ids=None)` acepta un subset por id;
`build_html(..., font_ids=...)` y `Application(..., font_ids=...)` propagan el subset.
`None` sigue embebiendo todas (retrocompat); el launcher R3 puede pasar
`font_ids=["inter", "jetbrains-mono"]` para recortar ~160KB de payload.
Tests: `test_build_html_font_subset_embeds_only_selected` / `..._none_embeds_all`.

---

## 5. `quit()` no notifica `on_close` (PRIORIDAD MEDIA)

**Ubicación:** `iskg/app.py:300-305` (`quit`) vs `run()` 202-208.

- `quit()` destruye la ventana y pone `_running=False` **sin** llamar a
  `_on_close_callbacks`. Los callbacks se ejecutan solo cuando `webview.start()`
  retorna de forma natural (cierre por el usuario).
- Si la app llama `quit()` programáticamente con callbacks de limpieza (guardar conf,
  parar workers), no se ejecutan.

**Propuesta:**
- `quit()` debe: `destroy()`, `_running=False`, **ejecutar las callbacks en el mismo
  `with contextlib.suppress(Exception)` que `run()`** y marcar el cierre como
  programático para que `run()` no las ejecute dos veces (flag `_quit_internal`).
- Separar `quit()` (suave, dispara close) de `destroy()`/`shutdown()` (hard).

**Estado:** ✓ CORREGIDO — nuevo `Application._fire_close_callbacks()` (idempotente);
`quit()` dispara los callbacks `on_close` al cerrar, y `run()` usa el mismo helper al
terminar el loop (flag `_close_fired` evita doble ejecución). Tests
`test_quit_fires_on_close_callbacks` y `test_fire_close_callbacks_idempotent`.

---

## 6. Layout `pack`/`grid`/`place` — ad-hoc y duplicado (PRIORIDAD MEDIA)

**Ubicación:** `iskg/base.py:205-360` (`pack`, `grid`, `place`, `grid_remove`) y
`iskg/widgets/_containers.py:1-140` (`_grid_template`, `Frame._detect_layout`,
`height_mode` flex/percent).

- Existen dos implementaciones de layout que se solapan: `_render_style()`
  (`base.py:890-957`) que genera CSS por child, y `layout.py` (nuevo, **sin integrar,
  no commiteado**, `git status` `??`) que genera el HTML del contenedor.
- `PackLayout.render_open` solo mira el `side` del primer child, no los `_layout_info`
  individuales.
- No hay gestión completa de `weight`/`sticky` para `place` (queda `position:absolute`).

**Propuesta:** unificar en `layout.py` con casos de prueba completos
(`pack(side, fill, expand, padx, pady, anchor)`, `grid(row, col, rowspan/columnspan,
sticky)`, `place(x, y, w, h)`) y detener la duplicación entre CSS y helper. Opcional
antes de R3; pero `layout.py` debe o commitarse y usarse, o eliminarse.

**Estado:** ✓ CORREGIDO — `Frame._render` detecta `has_place` y envuelve los hijos
`.place()` en un wrapper `position:relative; flex:1` (`_containers.py`) para que las
coordenadas absolutas queden contenidas; `iskg/layout.py` (muerto, sin importaciones)
eliminado. Test `test_place_children_relative_wrapper` en `tests/test_widgets_containers.py`.

---

## 7. `_sync()` re-renderiza verboso y compara cadenas (PRIORIDAD MEDIA)

**Ubicación:** `iskg/base.py:794-810`.

```python
def _sync(self):
    ...
    js = self._render_update_js()
    style_js = self._render_style_update_js()
    attr_js = self._render_attr_update_js()
    combined = ";".join(parts) if parts else ""
    if combined and combined != self._last_sync_js:
        self._last_sync_js = combined
        self._app._eval_js(combined)
```

- El dedup por string funciona, pero `eval_js` se sigue llamando con strings completos
  de CSS re-generados (`_render_style_update_js` → `iskg_set_style`).
- No hay invalidación fina por cambio; en widgets con varios `config()` en <100ms se
  manda más trabajo del necesario.

**Propuesta:** batching de `_eval_js` por marco (`after(0)` que agregue todos los
cambios pendientes en una sola transacción) con diff por widget. Opcional para R3.

**Estado:** ✓ CORREGIDO — `Application.sync_batch()` (context manager opt-in, clase
`SyncBatch`) con `_defer_sync`/`_flush_sync`/`_begin_sync_batch`/`_end_sync_batch`;
`Widget._sync` usa `_defer_sync` fuera del batch y vacía la cola al finalizarlo. Tests
`TestSyncBatch` (4) en `tests/test_app.py`; `TestSync` actualizado.

---

## 8. Debounce del log pipeline / batch en R3 (referencia, no cambio de ISKG)

Integrado ya en el launcher R3 (`_eval` en callbacks del GUI). Documentar en README las
garantías: eventos con `commit=True` nunca se debounceen; alta cadencia va por el canal
`batch` no-wait. Solo documental.

---

## 9. Sin backend headless / fallback sin pywebview (PRIORIDAD MEDIA-ALTA)

**Ubicación:** `iskg/app.py:164-166` (`try_import("webview", ...)`) y `app.py:327` (file_dialog).

- ISKG solo se ejecuta con pywebview ≥5 (WebKitGTK/GTK). No hay backend para headless,
  CI sin display (`xvfb`), o entornos embebidos.
- R3 compensa con `DemoBackend`/`QtBackend` en el launcher (fuera de ISKG), así que es
  una carencia del toolkit, no un defecto.

**Propuesta (a largo plazo):**
- Mínimo: `app.test_loop()` que construya el árbol sin ventana y capture el JS emitido
  (recorder) para tests de integración sin display — hoy los tests usan falsos.
- Backend textual de baja densidad (tipo `curses`/ANSI) o `ISKG_HEADLESS=1`.

**Estado:** ✓ CORREGIDO (mínimo) — `Application.test_loop()` devuelve `TestLoop` con
ventana fake `_TestWindow` (graba `evaluate_js`), `loop.html`/`loop.js_calls`,
`loop.fire(id, event, data)` (puente bridge a `_JSAPI.on_event`) y `loop.stop()`.
`TestLoop` y `_TestWindow` exportados desde `iskg.app`; tests `TestTestLoop` (4) en
`tests/test_app.py`. El backend textual dato queda como fase posterior.

---

## 10. Tests sin ventana real / CI (PRIORIDAD MEDIA)

**Datos:** 581 tests en `tests/` (app, base, imports, stress, themes, vars, widgets_*).
Todos corren en ~0.8 s. Ninguno abre una ventana WebKit real; `test_app::TestFileDialog`
mockea GTK (skip si `gi` no está).

**Estado:** ✓ CORREGIDO — `tests/test_e2e_smoke.py` con 5 tests: árbol headless,
roundtrip de sync (JS capturado), fire de comandos vía bridge, ventana real pywebview
bajo `xvfb` (`ISKG_SMOKE_TEST=1`, skip sin flag) y entrypoint subprocess. Nuevo job
`e2e-linux` en `.github/workflows/ci.yml` con `xvfb`.

---

## Correcciones ya hechas en esta pasada

- `iskg/app.py` — 2 `try/except: pass` → `contextlib.suppress(Exception)`
  (callbacks on-close y `window.destroy`) — `ruff check` pasa limpio.
- **Ítem 1** (`run()`): restauración de stderr en `finally` garantizado y nuevo
  parámetro `stderr_log` en `Application`.
- **Ítem 2** (`_JSAPI.on_event`): debounce ahora dedup por `(widget, event, data)`,
  no descarta eventos con datos distintos.
- **Ítem 3** (bind/tooltip post-`destroy`): retry único en `iskg_bind_key`;
  `iskg_cleanup(id)` elimina el elemento y tooltips del DOM; `destroy()` lo emite.
- **Ítem 4** (fonts): `font_css(ids)` + `font_ids` en `build_html`/`Application`.
- **Ítem 5** (`quit()`): callbacks `on_close` disparados con `_fire_close_callbacks()`
  idempotente, compartido con `run()`.
- Verificado: 594 tests pasan (~0.6 s) tras los cambios.

## Ítems 6, 7, 9, 10 — hechos en fases posteriores

- **Ítem 6** (layout): wrapper `position:relative; flex:1` para hijos `.place()`;
  `iskg/layout.py` muerto eliminado.
- **Ítem 7** (`_sync` batching): `Application.sync_batch()` opt-in con `_defer_sync`/
  `_flush_sync`; `Widget._sync` usa `_defer_sync`.
- **Ítem 9** (headless): `Application.test_loop()` → `TestLoop`/`_TestWindow`.
- **Ítem 10** (E2E): `tests/test_e2e_smoke.py` (5 tests) + job `e2e-linux` en CI con
  `xvfb`.
- Verificado: 607 tests pasan (~0.6 s); smoke real pywebview bajo `xvfb` OK.

## Prioridad propuesta

1. **✓ Ítems 1, 2, 3, 4, 5** — hechos en esta pasada.
2. **✓ Ítems 6, 7, 9, 10** — refactors, headless y CI, en una fase posterior.