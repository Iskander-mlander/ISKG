"""HTML page builder and JS bridge for ISKG widgets."""

from __future__ import annotations

from typing import Any

from .fonts import font_css

BRIDGE_JS = """
// ISKG Client Bridge for pywebview
(function() {
    window.iskg_bridge_event = function(widgetId, eventName, eventData) {
        try {
            if (typeof pywebview === 'undefined' || !pywebview.api || !pywebview.api.on_event) {
                console.log('[ISKG:bridge] pywebview not ready', widgetId, eventName, eventData);
                return;
            }
            pywebview.api.on_event(widgetId, eventName, JSON.stringify(eventData || ''));
        } catch(e) {
            console.warn('[ISKG:bridge]', e.message);
        }
    };

    window.iskg_set_text = function(id, text) {
        var el = document.getElementById(id);
        if (el) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.value = text;
            } else {
                el.innerText = text;
            }
        }
    };

    window.iskg_set_html = function(id, html) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = html;
    };

    window.iskg_set_value = function(id, value) {
        var el = document.getElementById(id);
        if (el) {
            if (el.tagName === 'INPUT' && el.type === 'range') {
                el.value = value;
                var evt = new Event('input', { bubbles: true });
                el.dispatchEvent(evt);
            } else {
                el.value = value;
            }
        }
    };

    window.iskg_set_attr = function(id, attr, value) {
        var el = document.getElementById(id);
        if (el) el.setAttribute(attr, value);
    };

    window.iskg_set_enabled = function(id, enabled) {
        var el = document.getElementById(id);
        if (el) {
            el.disabled = !enabled;
            el.classList.toggle('disabled', !enabled);
        }
    };

    window.iskg_set_visible = function(id, visible) {
        var el = document.getElementById(id);
        if (el) el.style.display = visible ? '' : 'none';
    };

    window.iskg_add_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.add(cls);
    };

    window.iskg_remove_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.remove(cls);
    };

    window.iskg_toggle_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.toggle(cls);
    };

    window.iskg_focus = function(id) {
        var el = document.getElementById(id);
        if (el) el.focus();
    };

    window.iskg_bind_key = function(id, eventType, keyFilter, mods) {
        var el = document.getElementById(id);
        if (!el) { setTimeout(function(){iskg_bind_key(id,eventType,keyFilter,mods);},50); return; }
        var fn = function(e) {
            if (keyFilter && e.key !== keyFilter && e.code !== keyFilter && e.key.toLowerCase() !== keyFilter.toLowerCase()) return;
            if (mods) {
                if (mods.ctrl && !e.ctrlKey) return;
                if (mods.alt && !e.altKey) return;
                if (mods.shift && !e.shiftKey) return;
            }
            var data = JSON.stringify({key:e.key,code:e.code,ctrl:e.ctrlKey,alt:e.altKey,shift:e.shiftKey});
            iskg_bridge_event(id, eventType, data);
        };
        el.addEventListener(eventType === 'keyrelease' ? 'keyup' : 'keydown', fn);
        el._iskg_key_fn = fn;
    };

    window.iskg_unbind_key = function(id, eventType) {
        var el = document.getElementById(id);
        if (el && el._iskg_key_fn) {
            el.removeEventListener(eventType === 'keyrelease' ? 'keyup' : 'keydown', el._iskg_key_fn);
            delete el._iskg_key_fn;
        }
    };

    window.iskg_set_style = function(id, cssText) {
        var el = document.getElementById(id);
        if (!el) return;
        var props = cssText.split(';');
        for (var i = 0; i < props.length; i++) {
            var p = props[i].trim();
            if (!p) continue;
            var colon = p.indexOf(':');
            if (colon > 0) {
                var name = p.substring(0, colon).trim();
                var value = p.substring(colon + 1).trim();
                el.style[name] = value;
            }
        }
    };

    // Theme switching at runtime
    window._ISKG_THEMES = {};

    window.iskg_register_themes = function(themes) {
        window._ISKG_THEMES = themes;
    };

    window.iskg_apply_theme = function(vars) {
        var root = document.documentElement;
        for (var key in vars) {
            if (vars.hasOwnProperty(key)) {
                root.style.setProperty(key, vars[key]);
            }
        }
    };

    window.iskg_set_theme = function(name) {
        var theme = window._ISKG_THEMES[name];
        if (theme) {
            iskg_apply_theme(theme);
            return true;
        }
        return false;
    };
})();
"""


def build_html(
    root_widgets: list[Any],
    ifaz_css: str,
    extra_js: str = "",
    extra_css: str = "",
    theme_name: str = "ifaz",
) -> str:
    all_widgets: list[Any] = []
    for w in root_widgets:
        all_widgets.extend(w._collect_widgets())

    rendered_html = "".join(w._render() for w in root_widgets if not w._destroyed)

    all_js_parts: list[str] = []
    for w in root_widgets:
        if not w._destroyed:
            all_js_parts.append(w._render_js())
            all_js_parts.append(w._render_children_js())
    # Include base JS (tooltips, key bindings) for every widget in the tree
    for _, w in all_widgets:
        if not w._destroyed:
            all_js_parts.append(w._render_tooltip_js())
            all_js_parts.append(w._render_key_bindings_js())
    all_js = "\n".join(p for p in all_js_parts if p)
    if extra_js:
        all_js += "\n" + extra_js

    # Embed theme data for runtime switching
    import json as _json

    from .themes import THEMES as _THEMES

    theme_data = _json.dumps(_THEMES, indent=2)

    theme_init = f"iskg_register_themes({theme_data});\niskg_set_theme('{theme_name}');\n"

    extra_css_block = f"<style>{extra_css}</style>" if extra_css else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ISKG App</title>
<style>{font_css()}</style>
<style>
body {{ margin:0; padding:0; overflow:auto; width:100vw; height:100vh; background:var(--bg-primary); }}
#iskg-root {{ min-height:100vh; display:flex; flex-direction:column; }}
</style>
<style>{ifaz_css}</style>
{extra_css_block}
</head>
<body>
<div id="iskg-root">{rendered_html}</div>
<script>
{BRIDGE_JS}
</script>
<script>
// Theme registration & init
{theme_init}
// Widget initialization
{all_js}
</script>
</body>
</html>"""
