API Reference
=============

Application
-----------

.. automodule:: iskg.app
   :members:
   :undoc-members:
   :show-inheritance:

Base Widget
-----------

.. automodule:: iskg.base
   :members:
   :undoc-members:
   :show-inheritance:

Widget Controls
---------------

.. automodule:: iskg.widgets._controls
   :members:
   :undoc-members:
   :show-inheritance:

Widget Display
--------------

.. automodule:: iskg.widgets._display
   :members:
   :undoc-members:
   :show-inheritance:

Widget Containers
-----------------

.. automodule:: iskg.widgets._containers
   :members:
   :undoc-members:
   :show-inheritance:

Widget Text
-----------

.. automodule:: iskg.widgets._text
   :members:
   :undoc-members:
   :show-inheritance:

Widget Data
-----------

.. automodule:: iskg.widgets._data
   :members:
   :undoc-members:
   :show-inheritance:

Widget Canvas
-------------

.. automodule:: iskg.widgets._canvas
   :members:
   :undoc-members:
   :show-inheritance:

Widget Menus
------------

.. automodule:: iskg.widgets._menus
   :members:
   :undoc-members:
   :show-inheritance:

Widget Charts
-------------

.. automodule:: iskg.widgets._charts
   :members:
   :undoc-members:
   :show-inheritance:

Widget Log
----------

.. automodule:: iskg.widgets._logview
   :members:
   :undoc-members:
   :show-inheritance:

Widget Datetime
---------------

.. automodule:: iskg.widgets._datetime
   :members:
   :undoc-members:
   :show-inheritance:

Widget Dialogs
--------------

.. automodule:: iskg.widgets._dialogs
   :members:
   :undoc-members:
   :show-inheritance:

Widget Misc
-----------

.. automodule:: iskg.widgets._misc
   :members:
   :undoc-members:
   :show-inheritance:

Template & Bridge
-----------------

.. automodule:: iskg.template
   :members:
   :undoc-members:
   :show-inheritance:

Theme
-----

.. automodule:: iskg.theme
   :members:
   :undoc-members:
   :show-inheritance:

Themes
------

.. automodule:: iskg.themes
   :members:
   :undoc-members:
   :show-inheritance:

Fonts
-----

.. automodule:: iskg.fonts
   :members:
   :undoc-members:
   :show-inheritance:

Reactivity (hot updates)
========================

ISKG refleja los cambios de propiedades en el DOM **sin recrear el widget**,
por capas:

1. **Estilos** (capa base ``_render_style_update_js``): cualquier prop en
   ``_CONFIG_TO_CSS`` se aplica en caliente para *todos* los widgets vía
   ``iskg_set_style`` — ``fg``/``color``, ``bg``/``background``,
   ``font_size``/``font_family``/``font_weight``, ``width``, ``height``,
   ``margin``, ``padding``, ``border_*``, ``opacity``, ``text_align``,
   ``flex``, ``gap``, etc.
2. **Atributos** (``_render_attr_update_js``): ``disabled`` se refleja para
   todos los widgets (``iskg_set_enabled``).
3. **Visibilidad**: el setter ``visible`` usa ``iskg_set_visible``.
4. **Por widget** (``_render_update_js``): props semánticas — ``text``
   (Button/Entry/Label/Text/RichText/IconLabel/StatusBar), ``value``
   (Slider/SpinBox/ProgressBar/LEDDisplay/RadialGauge), ``checked``
   (CheckBox/RadioButton/ToggleSwitch), ``values``/``current`` (ComboBox),
   ``color``/``active``/``size``/``label`` (IndicatorLED), ``src`` (ImageBox),
   etc.

Si una prop no tiene camino incremental, el escape hatch es
``Widget.rerender()``, que reemplaza el DOM y re-engancha el JS de
inicialización. Ver ``docs/PLAN_MEJORAS.md`` (roadmap, punto 3) para el
contrato completo y los tests correspondientes.

