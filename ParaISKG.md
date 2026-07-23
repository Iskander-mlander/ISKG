# Pendientes en ISKG (widget toolkit)

Funcionalidades que el módulo `iskg` no tiene y que DeepStateMap necesita:

## Canvas

- **`create_polygon(*points, **kwargs)`** — dibujar polígonos rellenos con contorno.
  Se usa para territorios (relleno semitransparente + borde) y aeródromos (triángulos).
  Alternativa actual: dibujar mediante `execute_js()` directamente sobre el canvas 2D context.

- **Soporte nativo de imágenes (`create_image`)** — para blit de tiles OSM.
  Actualmente se hace con `execute_js()` creando `Image` y `drawImage` en el canvas 2D context.
  Sería más limpio tener un método `create_image(x, y, data)` que acepte bytes PNG.

- **Evento `<<Resize>>`** — el Canvas emite `<<Resize>>` pero no hay documentación
  sobre cómo obtener el nuevo tamaño. El handler recibe un dict con `width`/`height`.

- **`widget_id`** — la propiedad existe en `Widget` como `_id`, pero el Canvas
  la expone como `widget_id`. El nombre es confuso porque el HTML id del canvas
  es `_id`, no `_id_c` como el código de `_blit_tile` asumía originalmente.
